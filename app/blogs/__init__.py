#
# Initializing the blogs Blueprint
#
from flask import Blueprint

blogs = Blueprint('blogs', __name__)

from app.blogs import views
