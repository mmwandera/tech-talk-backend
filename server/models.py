import bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define the association table for the many-to-many relationship between users (followers/following)
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: User can follow other users
    following = db.relationship('User', 
                                secondary=followers,  # Using the followers association table
                                primaryjoin=(followers.c.follower_id == id),  # User follows other users
                                secondaryjoin=(followers.c.followed_id == id),  # User is followed by other users
                                backref=db.backref('followers', lazy='select'))  # Reverse relationship

    # Relationship: User can post multiple blogs
    blogs = db.relationship('Blog', backref='author', lazy='dynamic')

    # Relationship: User can leave multiple comments
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    # Relationship: User can like multiple blogs
    likes = db.relationship('Like', backref='liker', lazy='dynamic')

    def set_password(self, password):
        """Set password hash using bcrypt."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the hashed password."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Blog(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship: Blog can have multiple comments
    comments = db.relationship('Comment', backref='blog', lazy='dynamic')

    # Relationship: Blog can have multiple likes
    likes = db.relationship('Like', backref='blog', lazy='dynamic')

class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

class Like(db.Model):
    __tablename__ = 'like'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
