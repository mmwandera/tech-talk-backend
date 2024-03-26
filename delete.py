from app import app, db
from models import User, Blog, Comment, Like, followers

def delete_data():
    print("🗑️ Deleting existing data...")
    with app.app_context():
        try:
            # Delete all data from tables
            db.session.query(User).delete()
            db.session.query(Blog).delete()
            db.session.query(Comment).delete()
            db.session.query(Like).delete()

            # Delete all data from followers table
            db.session.execute(followers.delete())

            # Commit the changes
            db.session.commit()
            print("✅ Existing data deleted.")
        except Exception as e:
            # Rollback changes if an error occurs
            db.session.rollback()
            print(f"❌ An error occurred while deleting data: {str(e)}")
        finally:
            # Close the session
            db.session.close()

if __name__ == "__main__":
    delete_data()
