from flask import Flask,jsonify, request, session, redirect, url_for
from flask_cors import CORS
from models import db, User, Blog, Comment, Like
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techtalk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'

CORS(app)
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
    # return jsonify({'message': 'User created successfully'}), 201

    response_data = {
        'message': 'User created successfully',
        'redirect_url': url_for('login') #Redirect to login page (Client Side routing)
    }
    
    # Return JSON response
    return jsonify(response_data), 201

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

    # Return the user ID in the response
    return jsonify({'message': 'Logged in successfully', 'user_id': user.id}), 200

# Route for getting all blogs
@app.route('/blogs', methods=['GET'])
def get_all_blogs():
    blogs = Blog.query.all()
    # Serialize blogs to JSON
    serialized_blogs = [{
        'id': blog.id,
        'title': blog.title,
        'content': blog.content,
        'image_url': blog.image_url,
        'author': {
            'id': blog.author.id,
            'username': blog.author.username
        }
    } for blog in blogs]
    return jsonify(serialized_blogs), 200

# Route for getting other users
@app.route('/users', methods=['GET'])
def get_other_users():
    logged_in_user_id = request.args.get('user_id')  # Get the logged-in user's ID from the query parameters
    # Query other users excluding the logged-in user
    other_users = User.query.filter(User.id != logged_in_user_id).all()    # Serialize other users to JSON
    serialized_users = [{
        'id': user.id,
        'username': user.username,
        'profile_photo': user.profile_photo,  # Add profile photo URL here
    } for user in other_users]
    return jsonify(serialized_users), 200

@app.route('/blogs/<int:user_id>', methods=['GET'])
def get_user_blogs(user_id):
    # Query blogs associated with the specified user ID
    blogs = Blog.query.filter_by(user_id=user_id).all()
    # Serialize blogs to JSON
    serialized_blogs = [{
        'id': blog.id,
        'title': blog.title,
        'content': blog.content,
        'image_url': blog.image_url,
        'author': {
            'id': blog.author.id,
            'username': blog.author.username
        }
    } for blog in blogs]
    return jsonify(serialized_blogs), 200

@app.route('/post-blog', methods=['POST'])
def post_blog():
    data = request.json

    # Get data from request body
    title = data.get('title')
    content = data.get('content')
    image_url = data.get('image_url')
    user_id = data.get('user_id')  # Assuming you send user_id along with the request

    # Create a new blog
    new_blog = Blog(title=title, content=content, image_url=image_url, user_id=user_id)

    try:
        # Add new blog to the database
        db.session.add(new_blog)
        db.session.commit()
        return jsonify(message='Blog posted successfully'), 201
    except Exception as e:
        print(str(e))
        return jsonify(error='Failed to post blog'), 500


if __name__ == '__main__':
    app.run(port=3000, debug=True)