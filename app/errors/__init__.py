# This creates the auth blueprint
from flask import Blueprint

errors = Blueprint('errors', __name__)

from . import views
