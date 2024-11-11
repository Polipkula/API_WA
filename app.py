from flask import Flask, request, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definice modelu BlogPost
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Vytvoření databáze
with app.app_context():
    db.create_all()

# POST: Vytvoření nového blog postu
@app.route('/api/blog', methods=['POST'])
def create_blog_post():
    data = request.get_json()
    content = data.get('content')
    author = data.get('author')
    
    if not content or not author:
        return jsonify({'error': 'Content and author are required'}), 400
    
    new_post = BlogPost(content=content, author=author)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'id': new_post.id}), 201

# GET: Zobrazení všech blog postů
@app.route('/api/blog', methods=['GET'])
def get_all_blog_posts():
    posts = BlogPost.query.all()
    return jsonify([{
        'id': post.id,
        'content': post.content,
        'author': post.author,
        'created_at': post.created_at
    } for post in posts])

# GET: Zobrazení jednoho blog postu
@app.route('/api/blog/<int:blog_id>', methods=['GET'])
def get_blog_post(blog_id):
    post = BlogPost.query.get(blog_id)
    if not post:
        return jsonify({'error': 'Blog post not found'}), 404
    
    return jsonify({
        'id': post.id,
        'content': post.content,
        'author': post.author,
        'created_at': post.created_at
    })

# DELETE: Smazání blog postu
@app.route('/api/blog/<int:blog_id>', methods=['DELETE'])
def delete_blog_post(blog_id):
    post = BlogPost.query.get(blog_id)
    if not post:
        return jsonify({'error': 'Blog post not found'}), 404
    
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Blog post deleted'}), 200

# PATCH: Částečná aktualizace blog postu
@app.route('/api/blog/<int:blog_id>', methods=['PATCH'])
def update_blog_post(blog_id):
    post = BlogPost.query.get(blog_id)
    if not post:
        return jsonify({'error': 'Blog post not found'}), 404
    
    data = request.get_json()
    content = data.get('content')
    author = data.get('author')
    
    if content:
        post.content = content
    if author:
        post.author = author
    
    db.session.commit()
    return jsonify({'message': 'Blog post updated'}), 200

# Zobrazení stránky
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

