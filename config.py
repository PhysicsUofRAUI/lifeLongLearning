import os
from os.path import abspath, dirname, join

# _cwd = dirname(abspath(__file__))

_basedir = os.path.abspath(os.path.dirname(__file__))


#
# Need this for the testing
#
# Need to look here closer: https://realpython.com/python-web-applications-with-flask-part-iii/
# class TestConfiguration(BaseConfiguration):
#     TESTING = True
#     WTF_CSRF_ENABLED = False
#
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # + join(_cwd, 'testing.db')
#
#     # Since we want our unit tests to run quickly
#     # we turn this down - the hashing is still done
#     # but the time-consuming part is left out.
#     HASH_ROUNDS = 1


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

    SECRET_KEY = 'sajg4ewqokghd8934jhrskdl'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'testing.sqlite')
