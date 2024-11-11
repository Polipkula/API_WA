from flask import Flask, request, jsonify, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace this with a secure secret key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# BlogPost model with permissions
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('User', backref='posts')

with app.app_context():
    db.create_all()

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# Login user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

# Logout user
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return jsonify({'message': 'Logged out'}), 200

# POST: Create a new blog post
@app.route('/api/blog', methods=['POST'])
def create_blog_post():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    new_post = BlogPost(content=content, author_id=session['user_id'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'id': new_post.id}), 201

# GET: Get all blog posts
@app.route('/api/blog', methods=['GET'])
def get_all_blog_posts():
    posts = BlogPost.query.all()
    return jsonify([{
        'id': post.id,
        'content': post.content,
        'author': User.query.get(post.author_id).username,
        'created_at': post.created_at
    } for post in posts])

# DELETE: Delete a blog post
@app.route('/api/blog/<int:blog_id>', methods=['DELETE'])
def delete_blog_post(blog_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    post = BlogPost.query.get(blog_id)
    if not post:
        return jsonify({'error': 'Blog post not found'}), 404

    if session['user_id'] != post.author_id and not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Blog post deleted'}), 200

# GET: Display main page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

