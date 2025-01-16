# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize the SQLAlchemy database object
db = SQLAlchemy()

# Define the User model, which represents the "users" table in the database
class User(UserMixin, db.Model):
    # Define table columns
    id = db.Column(db.Integer, primary_key=True)  # Primary key for identifying users
    username = db.Column(db.String(150), unique=True, nullable=False)  # Unique username, required
    email = db.Column(db.String(150), unique=True, nullable=True)  # Unique email, optional
    password = db.Column(db.String(150), nullable=True)  # User's password, optional
    is_admin = db.Column(db.Boolean, default=False)  # Flag to indicate admin status, defaults to False
    ip = db.Column(db.String(40), unique=False)  # IP address, not required to be unique

    # Ban-related fields
    is_banned = db.Column(db.Boolean, default=False)  # Flag to indicate if the user is banned
    ban_reason = db.Column(db.String(2048))  # Reason for the ban, if applicable
    ban_end_time = db.Column(db.DateTime, nullable=True)  # End time for the ban; None means permanent ban

    def is_ban_active(self):
        """
        Checks if the ban is still active.
        - Returns True if the ban is active.
        - Returns False if the user is not banned or the ban has expired.
        """
        if self.is_banned:
            if self.ban_end_time is None:
                # The ban is permanent, so it's always active
                return True

            # Convert current time and ban end time to UNIX timestamps for comparison
            current_time_timestamp = datetime.utcnow().timestamp()
            ban_end_timestamp = self.ban_end_time.timestamp()

            if current_time_timestamp > ban_end_timestamp:
                # If the current time exceeds the ban end time, lift the ban
                self.remove_ban()
                return False  # The ban has expired

            # The ban is still active if we reach this point
            return True

        # If the user is not banned, return False
        return False

    def remove_ban(self):
        """
        Lifts the ban by resetting ban-related fields and saving the changes to the database.
        """
        self.is_banned = False  # Set the ban status to False
        self.ban_reason = None  # Clear the ban reason
        self.ban_end_time = None  # Clear the ban end time
        db.session.commit()  # Save the updated user information to the database

    def get_ban_status(self):
        """
        Returns the ban status and details as a string.
        - For a permanent ban: "Permanent ban: <reason>"
        - For a temporary ban: "Banned until <end_time>: <reason>"
        - If no ban: "No active ban"
        """
        if self.is_banned:
            if self.ban_end_time is None:
                # If the ban is permanent, return the reason
                return f"Permanent ban: {self.ban_reason}"
            # If the ban is temporary, include the end time and reason
            return f"Banned until {self.ban_end_time}: {self.ban_reason}"
        # If there is no ban, return this message
        return "No active ban"
