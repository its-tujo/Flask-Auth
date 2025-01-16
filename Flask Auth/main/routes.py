from flask import render_template  # Used to render HTML templates
from flask_login import current_user  # For user authentication and session management
from . import main_bp  # Import the Blueprint instance from the main module

# Route for the home page
@main_bp.route('/')  # Maps the root URL '/' to this function
def index():
    # Render the 'index.html' template from the 'main' folder
    # Pass the current user object to the template for personalized content
    return render_template('main/index.html', user=current_user)
