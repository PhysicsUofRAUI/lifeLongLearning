import os
from os.path import abspath, dirname, join

# _cwd = dirname(abspath(__file__))

_basedir = os.path.abspath(os.path.dirname(__file__))


TOP_LEVEL_DIR = os.path.abspath(os.curdir)

class Config(object) :
    pass

class BaseConfiguration(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfiguration(BaseConfiguration):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://lllAdmin:$ingap0re@localhost/lll'
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle' : 3600}
    SECRET_KEY = 'sajg4ewqokghd8934jhrskdl'
    UPLOAD_FOLDER = TOP_LEVEL_DIR + '/app/static'


class TestConfiguration(BaseConfiguration):
    TESTING = True
    WTF_CSRF_ENABLED = False

    UPLOAD_FOLDER = TOP_LEVEL_DIR

    SECRET_KEY = 'sajg4ewqokghd8934jhrskdl'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'testing.sqlite')
