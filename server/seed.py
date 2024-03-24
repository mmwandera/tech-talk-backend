from random import randint, sample
from faker import Faker
from models import db, User, BlogPost, Comment, Like
from app import app

app.app_context().push()

print("🌱 Seeding data...")

# Delete existing data
print("🗑️ Deleting existing data...")
db.drop_all()
db.create_all()
print("✅ Existing data deleted.")

# Generating seed data
print("🌱 Generating seed data...")

# Seed Users
print("👤 Seeding users...")
fake = Faker()
users_data = [
    {"username": fake.user_name(), "email": fake.email(), "password": "password"} for _ in range(10)
]

for user_info in users_data:
    user = User(**user_info)
    db.session.add(user)

# Commit changes to create users first
db.session.commit()

# Create followers and following relationships
users = User.query.all()
for user in users:
    # Select random users to follow
    following = sample(users, randint(1, len(users) - 1))
    user.following.extend(following)

# Commit changes to create followers and following relationships
db.session.commit()

# Seed BlogPosts
print("📝 Seeding blog posts...")
blog_posts_data = [
    {"title": fake.sentence(), "content": fake.paragraph(), "user_id": randint(1, len(users))} for _ in range(20)
]

for post_info in blog_posts_data:
    post = BlogPost(**post_info)
    db.session.add(post)

# Seed Likes
print("❤️ Seeding likes...")
likes_data = [
    {"user_id": randint(1, len(users)), "post_id": randint(1, 20)} for _ in range(50)
]

for like_info in likes_data:
    like = Like(**like_info)
    db.session.add(like)

# Seed Comments
print("💬 Seeding comments...")
comments_data = [
    {"content": fake.text(), "user_id": randint(1, len(users)), "post_id": randint(1, 20)} for _ in range(50)
]

for comment_info in comments_data:
    comment = Comment(**comment_info)
    db.session.add(comment)

# Commit changes
print("💾 Saving changes to the database...")
db.session.commit()

print("🌱 Done seeding!")