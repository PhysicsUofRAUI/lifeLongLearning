#
# This will initialize everything
#   register blueprints
#   start the database
#   many other things (see the personal website for more
#   follow this webpage for changing the database: https://flask-migrate.readthedocs.io/en/latest/
#
# P.S. This is my most hated file
#
import os

# third-party imports
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from app.database import db
from config import ProductionConfiguration
from flask_migrate import Migrate

ALLOWED_EXTENSIONS = set(['pdf'])

def create_app(config_class=ProductionConfiguration):
    app = Flask(__name__)

    app.config.from_object(config_class)

    migrate = Migrate(app, db)

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

    from .author import author as author_blueprint
    app.register_blueprint(author_blueprint)

    from .errors import errors as errors_blueprint
    app.register_blueprint(errors_blueprint)

    with app.app_context():
        db.create_all()


    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.close()
        db.session.remove()
        db.session.rollback()


    return app
