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


class Config(object) :
    pass

class BaseConfiguration(object):
    pass


class TestConfiguration(BaseConfiguration):
    TESTING = True
    WTF_CSRF_ENABLED = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'testing.sqlite')
