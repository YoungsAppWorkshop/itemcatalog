import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))


# default config
class BaseConfig(object):
    """ Define base configuration for other configuration object to inherit
    """
    DEBUG = False
    SECRET_KEY = os.environ['ITEMCATALOG_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['ITEMCATALOG_DB_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')


class DevelopmentConfig(BaseConfig):
    """ Define development configuration object"""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """ Define production configuration object"""
    DEBUG = False
