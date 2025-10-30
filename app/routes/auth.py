from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user
from app.models.users import User, db
import re

bp = Blueprint('auth', __name__)

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):  # At least one uppercase
        return False
    if not re.search(r"[a-z]", password):  # At least one lowercase
        return False
    if not re.search(r"\d", password):     # At least one digit
        return False
    if not re.search(r"[@$!%*?&]", password):  # At least one special char
        return False
    return True


@bp.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email exists in UserProfile
        user = User.query.join(User.profile).filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('signin.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not all([username, email, password1, password2]):
            flash('Please fill in all fields', 'error')
            return render_template('register.html')

        if password1 != password2:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        if not validate_password(password1):
            flash('Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character', 'error')
            return render_template('register.html')

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register.html')

        from app.models.users import UserProfile
        existing_email = User.query.join(User.profile).filter_by(email=email).first()
        if existing_email:
            flash('Email already registered', 'error')
            return render_template('register.html')

        try:
            # Create new user
            user = User(username=username)
            user.set_password(password1)
            db.session.add(user)
            
            # Create user profile
            profile = UserProfile(user=user, email=email)
            db.session.add(profile)
            
            # Commit changes
            db.session.commit()
            
            flash('Registration successful! Please sign in.', 'success')
            return redirect(url_for('auth.signin'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html')

    return render_template('register.html')