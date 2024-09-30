from flask import Flask, render_template
from flask_cors import CORS
from datetime import timedelta

from .extensions import db, migrate
from .api.routes.auth import auth
from .api.routes.blog import blog

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://blog:blog@localhost:3306/blog'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '7938414aed691e4bf32edcad0d7df0c6' 
    
     # Configuration de session
    app.config['SESSION_COOKIE_NAME'] = 'session'
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['SESSION_COOKIE_SECURE'] = False  
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
 
    
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    
    db.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(blog, url_prefix='/api/blog')
    
    @app.route('/test_db')
    def test_db():
        try:
            db.session.execute('SELECT 1')
            return 'Database connection successful'
        except Exception as e:
           return f'Database connection failed: {str(e)}'
       
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app