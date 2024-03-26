from app import app
from models import db, User, Blog, Comment, Like

def query_database():
    while True:
        print("\nPlease select an option:")
        print("1. View all users")
        print("2. View all blogs")
        print("3. View all comments")
        print("4. View all likes")
        print("5. View user's blogs with comments and likes")
        print("6. View user's followers and following")
        print("7. Exit")
        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            # Query all users
            users = User.query.all()
            print("\nAll Users:")
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

        elif choice == '2':
            # Query all blogs
            blogs = Blog.query.all()
            print("\nAll Blogs:")
            for blog in blogs:
                print(f"ID: {blog.id}, Title: {blog.title}, Content: {blog.content}, Author: {blog.author.username}")

        elif choice == '3':
            # Query all comments
            comments = Comment.query.all()
            print("\nAll Comments:")
            for comment in comments:
                print(f"ID: {comment.id}, Content: {comment.content}, Author: {comment.author.username}, Blog: {comment.blog.title}")

        elif choice == '4':
            # Query all likes
            likes = Like.query.all()
            print("\nAll Likes:")
            for like in likes:
                print(f"ID: {like.id}, User: {like.liker.username}, Blog: {like.blog.title}")

        elif choice == '5':
            # View user's blogs with comments and likes
            user_id = int(input("Enter the user ID: "))
            user = User.query.get(user_id)
            if user:
                print(f"\nBlogs by User {user.username}:")
                for blog in user.blogs:
                    print(f"Title: {blog.title}")
                    print("Comments:")
                    for comment in blog.comments:
                        print(f"  - {comment.content} by {comment.author.username}")
                    print("Likes:")
                    for like in blog.likes:
                        print(f"  - Liked by {like.liker.username}")
            else:
                print(f"User with ID {user_id} not found.")

        elif choice == '6':
            # View user's followers and following
            user_id = int(input("Enter the user ID: "))
            user = User.query.get(user_id)
            if user:
                num_followers = len(user.followers)
                num_following = len(user.following)
                print(f"\nUser {user.username} has {num_followers} followers and is following {num_following} users.")
            else:
                print(f"User with ID {user_id} not found.")

        elif choice == '7':
            print("Exiting.")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    app.app_context().push()
    query_database()
