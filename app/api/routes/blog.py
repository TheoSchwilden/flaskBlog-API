from flask import Blueprint, request, jsonify, session
from markupsafe import escape
from .auth import login_required
from ..models.post import Post
from ...extensions import db

## TODO 1: ADD DATETIME TO POSTS
## TODO 2 : CHECK IN FRONTEND PADDING PROBLEM

blog = Blueprint('blog', __name__)

@blog.route('/posts', methods=['GET'])
def index():
    posts = Post.query.all()
    return jsonify([{'id': post.id, 'title': post.title, 'content': post.content} for post in posts]), 200



@blog.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    author = post.user.username
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    return jsonify({'id': post.id, 'title': post.title, 'content': post.content, 'author' : author}), 200


@blog.route('/posts/user', methods=['GET'])
@login_required
def get_user_posts():
    user_id = session.get('user_id')
    posts = Post.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': post.id, 'title': post.title, 'content': post.content} for post in posts]), 200


@blog.route('/post', methods=['POST'])
@login_required
def create_post():
    user_id = session.get('user_id')
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'message': 'Title and content required'}), 400
    
    safe_title = escape(title)
    safe_content = escape(content)
    
    new_post = Post(title=safe_title, content=safe_content, user_id=user_id)
    
    db.session.add(new_post)
    db.session.commit()
    
    post_data = {'id': new_post.id, 'title': new_post.title, 'content': new_post.content}
    
    return jsonify({
        'message': 'Post created', 
        'post' : post_data
    }), 201


@blog.route('/post/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    user_id = session.get('user_id')
    
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    if post.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    
    safe_title = escape(title)
    safe_content = escape(content)
    
    if title:
        post.title = safe_title
    if content:
        post.content = safe_content
    
    db.session.commit()
    
    return jsonify({'message': 'Post updated'}), 200


@blog.route('/post/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    user_id = session.get('user_id')
    
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404
    if post.user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 401
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted'}), 200

  


