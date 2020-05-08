#
# Blueprint structure is meant to mirror that of the dreamteam example
#
from flask import Blueprint

worksheets = Blueprint('worksheets', __name__)

from app.worksheets import views
