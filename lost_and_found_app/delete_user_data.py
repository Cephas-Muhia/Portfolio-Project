import os
from app import create_app, db
from app.models import User, LostItem, FoundItem

# Create an app context for database operations
app = create_app()
app.app_context().push()

def delete_user_data():
    try:
        # Confirmation step
        confirmation = input("Are you sure you want to delete all user data? This action cannot be undone. (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Operation canceled.")
            return

        # Delete all entries in LostItem and FoundItem tables
        LostItem.query.delete()
        FoundItem.query.delete()
        
        # Delete all users
        User.query.delete()
        
        # Commit changes to the database
        db.session.commit()
        print("All user data has been deleted successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    delete_user_data()

