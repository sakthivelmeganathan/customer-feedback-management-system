from app import app, db
from models import User, FeedbackCategory
import mysql.connector
from mysql.connector import Error

def create_admin_directly():
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Drop and recreate database
            cursor.execute("DROP DATABASE IF EXISTS customerfeedbacks")
            cursor.execute("CREATE DATABASE customerfeedbacks")
            print("Database reset complete")
            
            cursor.close()
            connection.close()
            
            # Now create admin in Flask context
            with app.app_context():
                # Create tables
                db.create_all()
                
                # Create new admin user with different credentials
                admin = User(
                    username='superuser',  # New username
                    email='super@example.com',
                    is_admin=True
                )
                admin.set_password('super123')  # New password
                db.session.add(admin)
                db.session.commit()
                
                # Verify admin was created
                admin = User.query.filter_by(username='superuser').first()
                if admin:
                    print("\nAdmin account created successfully!")
                    print("Username: superuser")
                    print("Password: super123")
                    
                    # Double check in MySQL
                    connection = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='',
                        database='customerfeedbacks'
                    )
                    cursor = connection.cursor()
                    cursor.execute("SELECT username, is_admin FROM user")
                    users = cursor.fetchall()
                    print("\nUsers in database:")
                    for user in users:
                        print(f"Username: {user[0]}, Is Admin: {user[1]}")
                    
                    cursor.close()
                    connection.close()
                else:
                    print("Error: Admin user not found after creation!")
                    
    except Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    create_admin_directly() 