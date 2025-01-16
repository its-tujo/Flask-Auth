# app.py
from flask import Flask, request, flash, redirect, url_for, render_template, render_template_string
from flask_login import LoginManager, current_user
from datetime import datetime
import time
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User  # Import database and User model from models.py
from auth import auth_bp  # Blueprint for authentication
from main import main_bp  # Blueprint for main application routes
import ipaddress
import requests

# Initialize Flask application
app = Flask(__name__)

# Application configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database location
app.config['SECRET_KEY'] = 'your_secret_key'  # Secret key for session management
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking for performance

# Initialize the database with the Flask app
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'  # Redirect unauthorized users to the login page

# URLs for downloading IP block lists
IPV4_URL = "https://raw.githubusercontent.com/lord-alfred/ipranges/main/all/ipv4_merged.txt"
IPV6_URL = "https://raw.githubusercontent.com/lord-alfred/ipranges/main/all/ipv6_merged.txt"

# Caching lists of IP ranges for blocked IPs
ipv4_ranges = []
ipv6_ranges = []

# Function to load IP ranges from the provided URLs
def load_ip_ranges():
    global ipv4_ranges, ipv6_ranges
    try:
        ipv4_response = requests.get(IPV4_URL)
        ipv6_response = requests.get(IPV6_URL)

        if ipv4_response.status_code == 200:
            # Parse IPv4 ranges into `ipaddress` objects
            ipv4_ranges = [ipaddress.ip_network(line.strip()) for line in ipv4_response.text.splitlines() if line.strip()]
        if ipv6_response.status_code == 200:
            # Parse IPv6 ranges into `ipaddress` objects
            ipv6_ranges = [ipaddress.ip_network(line.strip()) for line in ipv6_response.text.splitlines() if line.strip()]

    except requests.RequestException as e:
        print(f"Error loading IP block lists: {e}")

# Load IP ranges when the app starts
load_ip_ranges()

# HTML template for blocked IP page
html_page = """
{% extends "base.html" %}
{% block title %}IP Blocked{% endblock %}
{% block content %}
<div class="bg-gray-100 h-screen flex flex-col items-center justify-center">
    <div class="bg-white shadow-md rounded-lg p-8 text-center">
        <img src="https://i.ibb.co/Qc7SWJD/rrg-logo-nbg.png" alt="Logo" style="height:150px" class="mx-auto mb-4">
        <h1 class="text-2xl font-bold text-red-600">Your IP address is blocked</h1>
        <p class="text-gray-700 mt-4">Please contact the administrator if you believe this is a mistake.</p>
    </div>
</div>
{% endblock %}
"""

# Function to check user ban and IP block status before processing any request
@app.before_request
def check_ban_and_ip_status():
    load_ip_ranges()  # Reload IP ranges
    client_ip = get_ip()  # Get client IP address
    try:
        client_ip_obj = ipaddress.ip_address(client_ip)

        # Check if client IP is in the blocked ranges
        if any(client_ip_obj in net for net in ipv4_ranges + ipv6_ranges):
            return render_template_string(html_page)  # Render IP blocked page
    except ValueError:
        pass  # Ignore invalid IP addresses

    if current_user.is_authenticated:  # If the user is logged in
        current_user.ip = get_ip()  # Update the user's IP address

        # If the user's ban end time is in the past, lift the ban
        if current_user.ban_end_time and is_past_timestamp(current_user.ban_end_time):
            current_user.remove_ban()

        # If the user is still banned, show the ban page
        if current_user.is_ban_active():
            return render_template("accounts/ban.html")

# Flask-Login user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user by ID from the database

# Initialize Flask-Admin , change the name to your app name
admin = Admin(app, name='Admin | YOUR APP NAME/WEBBSITE NAME', template_mode='bootstrap4')

# Custom ModelView for Flask-Admin
class UserModelView(ModelView):
    def is_accessible(self):
        # Only allow access if the user is authenticated and an admin
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Redirect unauthorized users to the login page with a flash message
        flash("Unauthorized", "danger")
        return redirect(url_for('auth.login', next=request.url))

    # Exclude sensitive columns from admin panel
    column_exclude_list = ['password']
    # Make certain fields searchable in the admin panel
    column_searchable_list = ['username', 'email', 'ip', 'is_admin', 'is_banned', 'ban_reason']
    # Add filters for specific fields
    column_filters = ['username', 'email', 'ip', 'is_admin', 'is_banned', 'ban_reason']

# Add User model to the admin interface
admin.add_view(UserModelView(User, db.session))

# Function to check if a timestamp is in the past
def is_past_timestamp(given_timestamp) -> bool:
    if isinstance(given_timestamp, datetime):
        given_timestamp = given_timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format as string

    current_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # Get current time as string
    # Convert timestamps to seconds since epoch
    current_seconds = time.mktime(time.strptime(current_timestamp, '%Y-%m-%d %H:%M:%S'))
    given_seconds = time.mktime(time.strptime(given_timestamp, '%Y-%m-%d %H:%M:%S'))

    # Return True if the given timestamp is in the past
    return given_seconds < current_seconds

# Function to retrieve the client's IP address
def get_ip():
    # First try to get the IP from the X-Forwarded-For header
    forwarded_for = request.headers.get('X-Forwarded-For')

    if forwarded_for:
        ips = forwarded_for.split(',')  # X-Forwarded-For may contain multiple IPs
        ip = ips[0].strip()  # Use the first IP
    else:
        ip = request.remote_addr  # Fallback to the direct request IP

    return ip or '0.0.0.0'  # Return default if IP is not found

# Register blueprints for authentication and main routes
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
