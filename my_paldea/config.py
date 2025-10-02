import os
basedir = os.path.abspath(os.path.dirname(__file__))
class BaseConfig(object):
    'Base config class'
    #SECRET_KEY =
    DEBUG = True
    TESTING = False
    NEW_CONFIG_VARIABLE ='my value'
    SECRET_KEY = "kjsd8f7s9df8s7df8s7df98s7df98s7df98s7df\
        98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df\
        98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98\
        s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7\
        df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d\
        f98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s\
        7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df9\
        8s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7df98!!!\
        !!!s7df98s7df98s7df98s7df98s7df98s7df98s7df98s7d!#$^&f98s7\
        df98s7df98s7d)))(((?><<<>>f98s7df98s7df98s7df+=$%&98s7df98\
        s7df98s7d^&((]]{{f98s7df98s7df98s7*#@!df98s7df98s7df98!@#*\
        s7df98s7df98s7df98s"
    # SQLite database path
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(BaseConfig):
    'Production specific config'
    DEBUG=False
    #SECRET_KEY = open('/path/to/secret/file').read()'

class StagingConfig(BaseConfig):
    'Staging specific config'
    DEBUG = True

class DevelopmentConfig(BaseConfig):
    'Development environment specific config'
    DEBUG = True
    TESTING = True
    #SECRET_KEY ='Another random secret key'