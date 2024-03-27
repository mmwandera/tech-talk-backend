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

# Route for getting a blog with comments
@app.route('/blogs/<int:blog_id>', methods=['GET'])
def get_blog_with_comments(blog_id):
    # Retrieve the blog with the specified ID
    blog = Blog.query.get(blog_id)

    # Check if the blog exists
    if not blog:
        return jsonify({'message': 'Blog not found'}), 404
    
    # Serialize the blog
    serialized_blog = {
        'id': blog.id,
        'title': blog.title,
        'content': blog.content,
        'image_url': blog.image_url,
        'author': {
            'id': blog.author.id,
            'username': blog.author.username
        }
    }

    # Retrieve comments for the blog
    comments = Comment.query.filter_by(blog_id=blog_id).all()

    # Serialize comments
    serialized_comments = [{
        'id': comment.id,
        'content': comment.content,
        'author_username': comment.author.username
    } for comment in comments]

    # Add serialized comments to the serialized blog
    serialized_blog['comments'] = serialized_comments

    return jsonify(serialized_blog), 200


# Route for posting a comment to a particular blog
@app.route('/blogs/<int:blog_id>/comments', methods=['POST'])
def post_comment(blog_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    
    # Retrieve data from request
    data = request.json
    content = data.get('content')

    # Check if the content is provided
    if not content:
        return jsonify({'message': 'Content is required'}), 400

    # Check if the blog exists
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'message': 'Blog not found'}), 404

    # Create a new comment
    new_comment = Comment(content=content, user_id=session['user_id'], blog_id=blog_id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment posted successfully'}), 201

# Route for getting users available for recommendations
@app.route('/users', methods=['GET'])
def get_available_users():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    
    # Fetch all users except the logged-in user
    users = User.query.filter(User.id != session['user_id']).all()
    # Serialize users to JSON
    serialized_users = [{
        'id': user.id,
        'username': user.username
    } for user in users]
    return jsonify(serialized_users), 200

# Logged in user's profile
@app.route('/my-blogs', methods=['GET'])
def get_my_blogs():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    # Retrieve the logged-in user's ID
    user_id = session['user_id']

    # Retrieve the logged-in user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Serialize user profile data
    serialized_user = {
        'id': user.id,
        'username': user.username,
        'profile_photo': user.profile_photo,
        'num_followers': len(user.followers),
        'num_following': len(user.following),
    }

    # Retrieve blogs authored by the logged-in user
    my_blogs = user.blogs.all()

    # Serialize blogs to JSON with number of comments and likes
    serialized_blogs = [{
        'id': blog.id,
        'title': blog.title,
        'content': blog.content,
        'image_url': blog.image_url,
        'author': {
            'id': blog.author.id,
            'username': blog.author.username
        },
        'num_comments': blog.comments.count(),  # Count the number of comments for the blog
        'num_likes': blog.likes.count()  # Count the number of likes for the blog
    } for blog in my_blogs]

    return jsonify({'user': serialized_user, 'blogs': serialized_blogs}), 200

# Route for getting user profile
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    # Fetch the user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Count the number of followers
    num_followers = len(user.followers)

    # Count the number of following
    num_following = len(user.following)

    # Serialize user profile data
    serialized_user = {
        'id': user.id,
        'username': user.username,
        'profile_photo': user.profile_photo,
        'num_followers': num_followers,
        'num_following': num_following,
        'blogs': []
    }

    # Fetch the user's blogs
    user_blogs = user.blogs.all()

    # Serialize user's blogs
    serialized_blogs = []
    for blog in user_blogs:
        # Count the number of comments for the blog
        num_comments = blog.comments.count()

        # Count the number of likes for the blog
        num_likes = blog.likes.count()

        serialized_blog = {
            'id': blog.id,
            'title': blog.title,
            'content': blog.content,
            'image_url': blog.image_url,
            'num_comments': num_comments,
            'num_likes': num_likes
            # Add more blog data here as needed
        }
        serialized_blogs.append(serialized_blog)

    serialized_user['blogs'] = serialized_blogs

    return jsonify(serialized_user), 200

# Route for showing the list of users followed by a specific user
@app.route('/users/<int:user_id>/following', methods=['GET'])
def get_following(user_id):
    # Retrieve the user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Fetch the users followed by the user
    following = user.following

    # Serialize the list of users followed by the user
    serialized_following = [{
        'id': followed_user.id,
        'username': followed_user.username
        # Add more user data here as needed
    } for followed_user in following]

    return jsonify(serialized_following), 200

# Route for showing the list of users following a specific user
@app.route('/users/<int:user_id>/followers', methods=['GET'])
def get_followers(user_id):
    # Retrieve the user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Fetch the users following the user
    followers = user.followers

    # Serialize the list of users following the user
    serialized_followers = [{
        'id': follower.id,
        'username': follower.username
        # Add more user data here as needed
    } for follower in followers]

    return jsonify(serialized_followers), 200


if __name__ == '__main__':
    app.run(port=3000, debug=True)