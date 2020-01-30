import os


PATH = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # TODO: what is this?
    HASHING_ROUNDS = 5
    SALT_LENGTH = 10
    try:
        SECRET_KEY = os.environ['SECRET_KEY']
    except KeyError:
        SECRET_KEY = 'poochoo'
    try:
        SECURITY_PASSWORD_SALT = os.environ['SECURITY_SALT']
    except KeyError:
        SECURITY_PASSWORD_SALT = 'dootdoot'
    MAIL_SERVER = 
    MAIL_PORT = 
    MAIL_USE_TLS = 
    MAIL_USERNAME = 
    MAIL_PASSWORD =     

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PATH, "data-dev.db")


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PATH, "data-test.db")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PATH, "data-prod.db")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}