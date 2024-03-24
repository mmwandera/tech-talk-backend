import ipdb
from models import db, User, BlogPost, Comment, Like

def view_all_users():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}")

def view_user_followers(user_id):
    user = User.query.get(user_id)
    if user:
        followers = user.followers.all()
        num_followers = len(followers)
        print(f"\nFollowers of User ID {user_id}:")
        if followers:
            for follower in followers:
                print(f"ID: {follower.id}, Username: {follower.username}")
        else:
            print("No followers.")
        print(f"Total Followers: {num_followers}")
    else:
        print(f"User with ID {user_id} not found.")

def view_user_posts(user_id):
    user = User.query.get(user_id)
    if user:
        posts = BlogPost.query.filter_by(user_id=user_id).all()
        print(f"\nPosts by User ID {user_id}:")
        if posts:
            for post in posts:
                num_likes = len(post.likes)
                num_comments = len(post.comments)
                print(f"Title: {post.title}")
                print(f"Number of Likes: {num_likes}")
                print(f"Number of Comments: {num_comments}")
        else:
            print("No posts found for this user.")
    else:
        print(f"User with ID {user_id} not found.")

def query_database():
    while True:
        print("\nPlease select an option:")
        print("1. View all users")
        print("2. Select a user to view their followers and number")
        print("3. Select a user to view their posts and the number of likes and comments")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            view_all_users()
        elif choice == '2':
            user_id = int(input("Enter the user ID: "))
            view_user_followers(user_id)
        elif choice == '3':
            user_id = int(input("Enter the user ID: "))
            view_user_posts(user_id)
        elif choice == '4':
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    from app import app
    app.app_context().push()

    query_database()