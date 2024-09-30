from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from ..models.user import User
from ...extensions import db

auth = Blueprint('auth', __name__)


@auth.before_app_request
def make_session_permanent():
    session.permanent = True


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs): 
        if 'user_id' not in session:
            return jsonify({'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400
    
    if not username or not password:
        return jsonify({'message': 'Username, Email and password required'}), 400
    elif len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully'}), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
   
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    return jsonify({'message': 'Invalid username or password'}), 401


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200



@auth.route('/check_auth', methods=['GET'])
@login_required
def check_auth():
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'message': 'User authenticated',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })


