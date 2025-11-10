from flask import render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Feedback, FeedbackCategory, FeedbackResponse, db
from textblob import TextBlob
import os
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy import func
import csv
from io import StringIO

def init_categories():
    categories = [
        ('Product', 'Feedback about our products and services'),
        ('Service', 'Feedback about customer service experience'),
        ('Website', 'Feedback about website usability and features'),
        ('Support', 'Feedback about technical support'),
        ('Other', 'Other types of feedback')
    ]
    
    for name, description in categories:
        if not FeedbackCategory.query.filter_by(name=name).first():
            category = FeedbackCategory(name=name, description=description)
            db.session.add(category)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing categories: {str(e)}")

def init_app(app):
    # Register all routes with the app
    
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            print(f"\nLogin attempt - Username: {username}")
            
            # Check all users in database
            all_users = User.query.all()
            print("\nAll users in database:")
            for user in all_users:
                print(f"Username: {user.username}, Is Admin: {user.is_admin}")
            
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"User not found: {username}")
                flash('Username not found', 'danger')
                return redirect(url_for('admin_login'))
            
            if not user.is_admin:
                print(f"User is not admin: {username}")
                flash('This account is not an admin account', 'danger')
                return redirect(url_for('admin_login'))
            
            if not user.check_password(password):
                print(f"Invalid password for user: {username}")
                flash('Invalid password', 'danger')
                return redirect(url_for('admin_login'))
            
            print(f"Login successful for user: {username}")
            login_user(user, remember=remember)
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_login.html')

    @app.route('/create_admin', methods=['GET', 'POST'])
    def create_admin():
        # Check if admin already exists
        if User.query.filter_by(is_admin=True).first():
            flash('Admin account already exists', 'warning')
            return redirect(url_for('admin_login'))
        
        try:
            # Create default admin account
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')  # Default password
            
            db.session.add(admin)
            db.session.commit()
            
            flash('Default admin account created successfully! Username: admin, Password: admin123', 'success')
            return redirect(url_for('admin_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating admin account: {str(e)}', 'danger')
            return redirect(url_for('admin_login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            registration_code = request.form.get('registration_code')
            
            # Validate registration code
            if registration_code != 'USER123':  # You can change this to any code you want
                flash('Invalid registration code', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('user_login'))
        
        return render_template('register.html')

    @app.route('/user_login', methods=['GET', 'POST'])
    def user_login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
            
            print(f"\nLogin attempt - Username: {username}")
            
            # Check all users in database
            all_users = User.query.all()
            print("\nAll users in database:")
            for user in all_users:
                print(f"Username: {user.username}, Is Admin: {user.is_admin}")
            
            user = User.query.filter_by(username=username).first()
            
            if not user:
                print(f"User not found: {username}")
                flash('Username not found', 'danger')
                return redirect(url_for('user_login'))
            
            if not user.check_password(password):
                print(f"Invalid password for user: {username}")
                flash('Invalid password', 'danger')
                return redirect(url_for('user_login'))
            
            print(f"Login successful for user: {username}")
            login_user(user, remember=remember)
            flash('Welcome back!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('user_login.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return redirect(url_for('user_login'))

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        user_feedback = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.created_at.desc()).all()
        return render_template('dashboard.html', feedbacks=user_feedback)

    @app.route('/submit_feedback', methods=['GET', 'POST'])
    @login_required
    def submit_feedback():
        if request.method == 'POST':
            title = request.form.get('title')
            category_id = request.form.get('category')
            rating = request.form.get('rating')
            content = request.form.get('content')
            
            # Validate category
            if not category_id:
                flash('Please select a category', 'danger')
                return redirect(url_for('submit_feedback'))
            
            category = FeedbackCategory.query.get(category_id)
            if not category:
                flash('Invalid category selected', 'danger')
                return redirect(url_for('submit_feedback'))
            
            # Validate rating
            if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
                flash('Please select a valid rating', 'danger')
                return redirect(url_for('submit_feedback'))
            
            # Validate content
            if not content or len(content.strip()) < 10:
                flash('Feedback content must be at least 10 characters long', 'danger')
                return redirect(url_for('submit_feedback'))
            
            try:
                feedback = Feedback(
                    title=title,
                    category_id=category_id,
                    rating=int(rating),
                    content=content,
                    user_id=current_user.id
                )
                
                # Calculate sentiment score
                feedback.calculate_sentiment()
                
                db.session.add(feedback)
                db.session.commit()
                
                flash('Feedback submitted successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('Error submitting feedback. Please try again.', 'danger')
                print(f"Error submitting feedback: {str(e)}")
                return redirect(url_for('submit_feedback'))
        
        # Get all categories for the form
        categories = FeedbackCategory.query.order_by(FeedbackCategory.name).all()
        if not categories:
            # If no categories exist, initialize them
            init_categories()
            categories = FeedbackCategory.query.order_by(FeedbackCategory.name).all()
        
        return render_template('submit_feedback.html', categories=categories)

    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('dashboard'))
        
        # Get statistics
        total_feedback = Feedback.query.count()
        resolved_count = Feedback.query.filter_by(status='resolved').count()
        pending_count = Feedback.query.filter_by(status='pending').count()
        avg_rating = db.session.query(func.avg(Feedback.rating)).scalar() or 0
        
        # Get all feedback with user and category information
        feedbacks = Feedback.query.join(User, Feedback.user_id == User.id).outerjoin(FeedbackCategory, Feedback.category_id == FeedbackCategory.id).order_by(Feedback.created_at.desc()).all()
        
        return render_template('admin_dashboard.html',
                             feedbacks=feedbacks,
                             total_feedback=total_feedback,
                             resolved_count=resolved_count,
                             pending_count=pending_count,
                             avg_rating=avg_rating)

    @app.route('/admin/respond/<int:feedback_id>', methods=['POST'])
    @login_required
    def admin_respond_feedback(feedback_id):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('dashboard'))
        
        feedback = Feedback.query.get_or_404(feedback_id)
        response_content = request.form.get('response')
        new_status = request.form.get('status')
        
        # Create or update response
        if feedback.response:
            feedback.response.content = response_content
        else:
            response = FeedbackResponse(
                content=response_content,
                feedback_id=feedback.id,
                admin_id=current_user.id
            )
            db.session.add(response)
        
        feedback.status = new_status
        db.session.commit()
        
        flash('Response submitted successfully!')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/analytics')
    @login_required
    def admin_analytics():
        if not current_user.is_admin:
            flash('Access denied')
            return redirect(url_for('dashboard'))
        
        # Compute analytics without heavy dependencies
        feedbacks = Feedback.query.all()

        rating_stats = {}
        category_stats = {}
        status_stats = {}

        total_sentiment = 0.0
        sentiment_count = 0

        for f in feedbacks:
            rating_stats[f.rating] = rating_stats.get(f.rating, 0) + 1
            category_name = f.category.name if f.category else 'Unknown'
            category_stats[category_name] = category_stats.get(category_name, 0) + 1
            status_stats[f.status] = status_stats.get(f.status, 0) + 1

            if f.sentiment_score is not None:
                total_sentiment += f.sentiment_score
                sentiment_count += 1

        avg_sentiment = (total_sentiment / sentiment_count) if sentiment_count else 0.0
        
        return render_template('admin_analytics.html',
                             rating_stats=rating_stats,
                             category_stats=category_stats,
                             status_stats=status_stats,
                             avg_sentiment=avg_sentiment)

    @app.route('/admin/register', methods=['GET', 'POST'])
    def admin_register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            admin_code = request.form.get('admin_code')
            
            # Validate admin code
            if admin_code != 'ADMIN123':  # You can change this to any code you want
                flash('Invalid admin registration code', 'danger')
                return redirect(url_for('admin_register'))
            
            # Check if passwords match
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('admin_register'))
            
            # Check if username exists
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('admin_register'))
            
            # Check if email exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('admin_register'))
            
            # Create new admin user
            admin = User(
                username=username,
                email=email,
                is_admin=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            flash('Admin account created successfully! Please login.', 'success')
            return redirect(url_for('admin_login'))
        
        return render_template('admin_register.html')

    @app.route('/admin/download-feedback')
    @login_required
    def download_feedback_csv():
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('dashboard'))
        
        # Create a StringIO object to write CSV data
        si = StringIO()
        cw = csv.writer(si)
        
        # Write header row
        cw.writerow(['ID', 'User', 'Title', 'Category', 'Rating', 'Content', 'Status', 'Created At', 'Response', 'Response Date'])
        
        # Get all feedback with related data
        feedbacks = Feedback.query.join(User, Feedback.user_id == User.id).outerjoin(FeedbackCategory, Feedback.category_id == FeedbackCategory.id).all()
        
        # Write data rows
        for feedback in feedbacks:
            cw.writerow([
                feedback.id,
                feedback.user.username,
                feedback.title,
                feedback.category.name,
                feedback.rating,
                feedback.content,
                feedback.status,
                feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                feedback.response.content if feedback.response else '',
                feedback.response.created_at.strftime('%Y-%m-%d %H:%M:%S') if feedback.response else ''
            ])
        
        # Create the response
        output = si.getvalue()
        si.close()
        
        # Generate filename with current timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'feedback_data_{timestamp}.csv'
        
        return Response(
            output,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv'
            }
        )

    @app.route('/admin/delete-feedback/<int:feedback_id>', methods=['POST'])
    @login_required
    def delete_feedback(feedback_id):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        
        feedback = Feedback.query.get_or_404(feedback_id)
        
        try:
            # Delete associated response if exists
            if feedback.response:
                db.session.delete(feedback.response)
            
            # Delete the feedback
            db.session.delete(feedback)
            db.session.commit()
            
            flash('Feedback deleted successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error deleting feedback. Please try again.', 'danger')
            print(f"Error deleting feedback: {str(e)}")
        
        return redirect(url_for('admin_dashboard'))

    @app.route('/debug/users')
    def debug_users():
        users = User.query.all()
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            })
        return jsonify(result)

    @app.route('/debug/categories')
    def debug_categories():
        categories = FeedbackCategory.query.all()
        result = []
        for cat in categories:
            result.append({
                'id': cat.id,
                'name': cat.name,
                'description': cat.description
            })
        return jsonify(result)

    @app.route('/admin/bulk-actions', methods=['GET', 'POST'])
    @login_required
    def bulk_actions():
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            action = request.form.get('action')
            ids = request.form.get('ids', '').split(',')
            
            try:
                feedbacks = Feedback.query.filter(Feedback.id.in_(ids)).all()
                
                for feedback in feedbacks:
                    if action == 'resolve':
                        feedback.status = 'resolved'
                    elif action == 'progress':
                        feedback.status = 'in_progress'
                    elif action == 'pending':
                        feedback.status = 'pending'
                    elif action == 'delete':
                        if feedback.response:
                            db.session.delete(feedback.response)
                        db.session.delete(feedback)
                
                db.session.commit()
                return jsonify({'success': True, 'message': f'Bulk action completed on {len(feedbacks)} items'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': str(e)})
        
        # GET request - show bulk actions page
        total_feedback = Feedback.query.count()
        resolved_count = Feedback.query.filter_by(status='resolved').count()
        pending_count = Feedback.query.filter_by(status='pending').count()
        feedbacks = Feedback.query.join(User, Feedback.user_id == User.id).outerjoin(FeedbackCategory, Feedback.category_id == FeedbackCategory.id).order_by(Feedback.created_at.desc()).all()
        
        return render_template('bulk_actions.html',
                             feedbacks=feedbacks,
                             total_feedback=total_feedback,
                             resolved_count=resolved_count,
                             pending_count=pending_count)

    @app.route('/search')
    @login_required
    def search():
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        status = request.args.get('status', '')
        rating = request.args.get('rating', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Build query based on user role
        if current_user.is_admin:
            base_query = Feedback.query.join(User, Feedback.user_id == User.id).outerjoin(FeedbackCategory, Feedback.category_id == FeedbackCategory.id)
        else:
            base_query = Feedback.query.filter_by(user_id=current_user.id).outerjoin(FeedbackCategory, Feedback.category_id == FeedbackCategory.id)
        
        # Apply filters
        if query:
            base_query = base_query.filter(
                (Feedback.title.contains(query)) | 
                (Feedback.content.contains(query))
            )
        
        if category:
            base_query = base_query.filter(FeedbackCategory.name == category)
        
        if status:
            base_query = base_query.filter(Feedback.status == status)
        
        if rating:
            base_query = base_query.filter(Feedback.rating == int(rating))
        
        if date_from:
            base_query = base_query.filter(Feedback.created_at >= datetime.strptime(date_from, '%Y-%m-%d'))
        
        if date_to:
            base_query = base_query.filter(Feedback.created_at <= datetime.strptime(date_to, '%Y-%m-%d'))
        
        results = base_query.order_by(Feedback.created_at.desc()).all()
        
        return render_template('advanced_search.html', results=results)

    @app.route('/feedback/<int:feedback_id>')
    @login_required
    def feedback_details(feedback_id):
        feedback = Feedback.query.get_or_404(feedback_id)
        
        # Check permissions
        if not current_user.is_admin and feedback.user_id != current_user.id:
            flash('Access denied.')
            return redirect(url_for('dashboard'))
        
        return render_template('feedback_details.html', feedback=feedback)