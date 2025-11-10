from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User
from sqlalchemy import event, text, Engine
import os
import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/customer_feedback_management_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'pool_timeout': 30
}

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'faculty_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    try:
        # Create all tables (SQLite)
        db.create_all()
        
        # Initialize categories if they don't exist
        from routes import init_categories
        init_categories()
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.session.rollback()
        raise

# Lightweight connection check for SQLite (optional)
@event.listens_for(Engine, "connect")
def ping_connection(connection, branch):
    if branch:
        return
    try:
        connection.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise Exception("Database connection failed")

# Import and register routes
from routes import init_app as init_routes
init_routes(app)

if __name__ == '__main__':
    with app.app_context():
        init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 

    
