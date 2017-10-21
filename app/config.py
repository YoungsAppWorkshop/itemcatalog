import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))


# default config
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.environ['ITEMCATALOG_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['ITEMCATALOG_DB_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
