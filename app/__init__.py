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
from app.database import db_session, init_db
from config import Config
db = SQLAlchemy()

TOP_LEVEL_DIR = os.path.abspath(os.curdir)

UPLOAD_FOLDER = TOP_LEVEL_DIR + '/app/static'
ALLOWED_EXTENSIONS = set(['pdf'])

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '7$@[V@(f`h`x<j,s@%Aey]v(@yR$O9'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_POOL_PRE_PING'] = True

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle' : 3600}

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from app import models

    from .blogs import blogs as blogs_blueprint
    app.register_blueprint(blogs_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .other import other as other_blueprint
    app.register_blueprint(other_blueprint)

    from .worksheets import worksheets as worksheets_blueprint
    app.register_blueprint(worksheets_blueprint)


    init_db()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

        if exception and db_session.is_active:
            db_session.rollback()


    return app
