from flask import Blueprint

# Create a Blueprint instance for the authentication module
# - 'auth': the name of the Blueprint
# - __name__: the name of the current module (used to locate templates and static files)
# - url_prefix='/auth': all routes defined in this Blueprint will be prefixed with '/auth'
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import the routes defined in the same package
# This ensures that the routes are registered with the Blueprint
from . import routes
