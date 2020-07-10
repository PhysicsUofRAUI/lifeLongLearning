from flask import Blueprint

learner = Blueprint('learner', __name__)

from app.learner import views
