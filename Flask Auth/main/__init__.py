from flask import Blueprint

# Create a Blueprint instance for the main application module
# - 'main': the name of the Blueprint
# - __name__: the name of the current module (used to locate templates and static files)
# - url_prefix='': no prefix is applied to the routes, so they will be accessible at the root level
main_bp = Blueprint('main', __name__, url_prefix='')

# Import the routes defined in the same package
# This ensures that the routes are registered with the Blueprint
from . import routes
