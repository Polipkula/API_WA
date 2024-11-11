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
    return jsonify({'message': 'Post created successfully'}), 201

@app.route('/api/blog', methods=['GET'])
def get_posts():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    posts = BlogPost.query.all()
    result = []
    for post in posts:
        author = User.query.get(post.author_id)
        if session['is_admin'] or post.author_id == session['user_id'] or session['username'] in post.visible_to.split(','):
            result.append({
                'id': post.id,
                'content': post.content,
                'author': author.username,
                'created_at': post.created_at,
                'visible_to': post.visible_to.split(',')
            })
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
