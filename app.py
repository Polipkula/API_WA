from flask import Flask, request, jsonify, session, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# BlogPost Model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visible_to = db.Column(db.Text, default="")  # Comma-separated list of usernames

# Create database tables within the application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = generate_password_hash(data['password'])

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

@app.route('/api/blog', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.get_json()
    if not data or not data.get('content'):
        return jsonify({'message': 'Content is required'}), 400

    new_post = BlogPost(content=data['content'], author_id=session['user_id'])
    db.session.add(new_post)
    db.session.commit()

    # Debug statement to check the new post
    print(f"Post created: {new_post.content} by user_id {new_post.author_id}")
    return jsonify({'message': 'Post created successfully'}), 201

@app.route('/api/blog/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404

    # Only allow the author to delete their own posts
    if post.author_id != session['user_id']:
        return jsonify({'message': 'Forbidden'}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted successfully'}), 200


@app.route('/api/blog', methods=['GET'])
def get_posts():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    posts = BlogPost.query.all()
    result = []

    for post in posts:
        author = User.query.get(post.author_id)
        
        # Handle the case where the user does not exist
        if not author:
            print(f"Warning: No user found for author_id {post.author_id}")
            author_name = "Unknown"
        else:
            author_name = author.username
        
        # Include a flag to indicate if the current user can delete the post
        can_delete = (post.author_id == session['user_id'])

        result.append({
            'id': post.id,
            'content': post.content,
            'author': author_name,
            'created_at': post.created_at,
            'can_delete': can_delete
        })

    print(f"Posts fetched for user {session.get('user_id')}: {result}")
    return jsonify(result), 200



@app.route('/api/blog/<int:post_id>', methods=['DELETE', 'PUT'])
def manage_post(post_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({'message': 'Post not found'}), 404

    if session['is_admin'] or post.author_id == session['user_id']:
        if request.method == 'DELETE':
            db.session.delete(post)
            db.session.commit()
            return jsonify({'message': 'Post deleted successfully'}), 200

        if request.method == 'PUT':
            data = request.get_json()
            post.content = data.get('content', post.content)
            post.visible_to = ",".join(data.get('visible_to', post.visible_to.split(',')))
            db.session.commit()
            return jsonify({'message': 'Post updated successfully'}), 200

    return jsonify({'message': 'Unauthorized'}), 403

@app.route('/api/check-session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'is_admin': session['is_admin'], 'username': session['username']}), 200
    return jsonify({'logged_in': False}), 200

@app.route('/api/about', methods=['GET'])
def api_documentation():
    documentation = {
        "endpoints": [
            {
                "method": "POST",
                "endpoint": "/register",
                "description": "Register a new user.",
                "request_format": {
                    "username": "string",
                    "password": "string"
                },
                "response_format": {
                    "message": "string"
                },
                "authorization": "No authorization required."
            },
            {
                "method": "POST",
                "endpoint": "/login",
                "description": "Log in a user and create a session.",
                "request_format": {
                    "username": "string",
                    "password": "string"
                },
                "response_format": {
                    "message": "string"
                },
                "authorization": "No authorization required."
            },
            {
                "method": "POST",
                "endpoint": "/logout",
                "description": "Log out the current user.",
                "request_format": "None",
                "response_format": {
                    "message": "string"
                },
                "authorization": "Requires session."
            },
            {
                "method": "POST",
                "endpoint": "/api/blog",
                "description": "Create a new blog post.",
                "request_format": {
                    "content": "string"
                },
                "response_format": {
                    "message": "string"
                },
                "authorization": "Requires session."
            },
            {
                "method": "GET",
                "endpoint": "/api/blog",
                "description": "Retrieve all blog posts. Includes a 'can_delete' flag if the logged-in user owns the post.",
                "request_format": "None",
                "response_format": [
                    {
                        "id": "integer",
                        "content": "string",
                        "author": "string",
                        "created_at": "datetime",
                        "can_delete": "boolean"
                    }
                ],
                "authorization": "Requires session."
            },
            {
                "method": "DELETE",
                "endpoint": "/api/blog/<post_id>",
                "description": "Delete a specific blog post.",
                "request_format": "None",
                "response_format": {
                    "message": "string"
                },
                "authorization": "Requires session and user must own the post."
            },
            {
                "method": "GET",
                "endpoint": "/api/about",
                "description": "Retrieve API documentation.",
                "request_format": "None",
                "response_format": "JSON containing all endpoints and their descriptions.",
                "authorization": "No authorization required."
            }
        ],
        "authorization": {
            "description": "Authorization is based on session cookies.",
            "process": [
                "1. User logs in via /login and a session cookie is created.",
                "2. This session cookie must be included in all subsequent requests to authorized endpoints.",
                "3. If the session is invalid or expired, the user will receive a 401 Unauthorized response."
            ]
        }
    }
    return jsonify(documentation), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
