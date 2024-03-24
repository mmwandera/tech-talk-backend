# app.py
from flask import Flask
from models import db, User, BlogPost, Comment, Like
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///techtalk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return 'TechTalk'

if __name__ == '__main__':
    app.run(port=3000, debug=True)