#
# Creates the blueprint for other pages 
#
from flask import Blueprint

other = Blueprint('other', __name__)

from . import views
