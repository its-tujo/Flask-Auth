from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from . import auth_bp  # Import the authentication blueprint
from models import db, User  # Import database and User model

# Route for logging in users
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # If the request is a POST (form submission)
        username = request.form['username']  # Get the username from the form
        password = request.form['password']  # Get the password from the form
        user = User.query.filter_by(username=username).first()  # Query the user by username

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)  # Log the user in
            flash('Login successful!', 'success')  # Show a success message
            return redirect(url_for('main.index'))  # Redirect to the main index page

        # If login fails, show an error message
        flash('Invalid login credentials.', 'danger')
    
    # Render the login template for GET requests or after a failed login
    return render_template('account/login.html')

# Route for registering new users
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':  # If the request is a POST (form submission)
        username = request.form['username']  # Get the username from the form
        email = request.form['email']  # Get the email from the form
        password = request.form['password']  # Get the password from the form
        hashed_password = generate_password_hash(password, method='sha256')  # Hash the password for security

        # Check if the username or email is already in use
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')  # Show error if username is taken
        elif User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')  # Show error if email is taken
        else:
            # Create a new user and add them to the database
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()  # Commit the new user to the database
            flash('Registration successful! Please log in.', 'success')  # Show a success message
            return redirect(url_for('auth.login'))  # Redirect to the login page

    # Render the registration template for GET requests or after a failed registration
    return render_template('account/register.html')

# Route for logging out users
@auth_bp.route('/logout')
@login_required  # Ensure that only logged-in users can access this route
def logout():
    logout_user()  # Log the user out
    flash('Successfully logged out.', 'success')  # Show a success message
    return redirect(url_for('auth.login'))  # Redirect to the login page
