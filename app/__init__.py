#
# This will initialize everything
#   register blueprints
#   start the database
#   many other things (see the personal website for more)
#
# P.S. This is my most hated file
#
import os

# third-party imports
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from app.database import db

ALLOWED_EXTENSIONS = set(['pdf'])

def create_app(config_class):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)

    from app import models

    from .blogs import blogs as blogs_blueprint
    app.register_blueprint(blogs_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .other import other as other_blueprint
    app.register_blueprint(other_blueprint)

    from .worksheets import worksheets as worksheets_blueprint
    app.register_blueprint(worksheets_blueprint)

    with app.app_context():
        db.create_all()


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.close()
        db.session.remove()
        db.session.rollback()


    return app
