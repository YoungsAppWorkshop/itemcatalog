import os


# default config
class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = os.environ['ITEMCATALOG_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['ITEMCATALOG_DB_URI']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
