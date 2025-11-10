from app import app, db
from models import User, FeedbackCategory

def reset_database():
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