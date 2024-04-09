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


# Route for user log out
@app.route('/logout', methods=['GET'])
def logout():
    # Remove the user ID from the session to log out the user
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

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


if __name__ == '__main__':
    app.run(port=3000, debug=True)