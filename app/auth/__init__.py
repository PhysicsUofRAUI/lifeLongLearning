# This creates the auth blueprint
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
