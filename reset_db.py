from app import app, db
from models import User, FeedbackCategory
import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS customerfeedbacks")
            print("Database 'customerfeedbacks' created or already exists")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return False
    
    return True

def reset_database():
    # First ensure database exists
    if not create_database():
        print("Failed to create database. Please check MySQL connection.")
        return
    
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("Dropped all existing tables")
            
            # Create all tables
            db.create_all()
            print("Created all tables")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("Created admin user")
            
            # Create default categories
            categories = [
                ('Product', 'Feedback about our products and services'),
                ('Service', 'Feedback about customer service experience'),
                ('Website', 'Feedback about website usability and features'),
                ('Support', 'Feedback about technical support'),
                ('Other', 'Other types of feedback')
            ]
            
            for name, description in categories:
                category = FeedbackCategory(name=name, description=description)
                db.session.add(category)
            print("Created default categories")
            
            # Commit changes
            db.session.commit()
            print("\nDatabase reset complete. Admin account created with:")
            print("Username: admin")
            print("Password: admin123")
            
            # Verify admin user was created
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("\nAdmin user verification successful!")
            else:
                print("\nWarning: Admin user not found after creation!")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error during database reset: {e}")

if __name__ == '__main__':
    reset_database() 