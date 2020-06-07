import os
from os.path import abspath, dirname, join
import secrets

_basedir = os.path.abspath(os.path.dirname(__file__))


TOP_LEVEL_DIR = os.path.abspath(os.curdir)

class BaseConfiguration(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfiguration(BaseConfiguration):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE')
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_size' : 100, 'pool_recycle' : 280}
    SECRET_KEY = secrets.token_urlsafe(16)
    UPLOAD_FOLDER = TOP_LEVEL_DIR + '/app/static'


class TestConfiguration(BaseConfiguration):
    TESTING = True
    WTF_CSRF_ENABLED = False

    USERNAME=os.getenv('LOGIN_USERNAME')
    PASSWORD=os.getenv('LOGIN_PASSWORD')

    UPLOAD_FOLDER = TOP_LEVEL_DIR

    SECRET_KEY = secrets.token_urlsafe(16)

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'testing.sqlite')
