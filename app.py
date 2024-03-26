from flask import Flask,jsonify, request, session, redirect, url_for
from models import db, User, Blog, Comment, Like
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techtalk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'

migrate = Migrate(app, db)
db.init_app(app)

# Route for user sign up
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if the username or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'message': 'Username or email already exists'}), 400

    # Create a new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

# Route for user log in
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Check if the username exists
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid username or password'}), 401

    # Set the user ID in the session to indicate that the user is logged in
    session['user_id'] = user.id
    return jsonify({'message': 'Logged in successfully'}), 200

# Route for user log out
@app.route('/logout', methods=['GET'])
def logout():
    # Remove the user ID from the session to log out the user
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

# Route for creating a new blog post
@app.route('/blogs', methods=['POST'])
def create_blog():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.json
    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url')

    user_id = session['user_id']
    new_blog = Blog(title=title, content=content, image_url=image_url, user_id=user_id)
    db.session.add(new_blog)
    db.session.commit()
    return jsonify({'message': 'Blog post created successfully'}), 201

# Route for deleting a blog post
@app.route('/blogs/<int:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'message': 'Blog post not found'}), 404

    if blog.author.id != session['user_id']:
        return jsonify({'message': 'You are not authorized to delete this blog post'}), 403

    db.session.delete(blog)
    db.session.commit()
    return jsonify({'message': 'Blog post deleted successfully'}), 200

# Route for updating a blog post
@app.route('/blogs/<int:blog_id>', methods=['PUT'])
def update_blog(blog_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'message': 'Blog post not found'}), 404

    if blog.author.id != session['user_id']:
        return jsonify({'message': 'You are not authorized to update this blog post'}), 403

    data = request.json
    blog.title = data.get('title', blog.title)
    blog.content = data.get('content', blog.content)
    blog.image_url = data.get('image_url', blog.image_url)
    db.session.commit()
    return jsonify({'message': 'Blog post updated successfully'}), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)