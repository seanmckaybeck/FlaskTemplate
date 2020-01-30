import flask
import flask_hashing
import flask_login
import flask_mail
import flask_sqlalchemy

import blueprints
import config
import utils


db = flask_sqlalchemy.SQLAlchemy()
login_manager = flask_login.LoginManager()
hashing = flask_hashing.Hashing()
mail = flask_mail.Mail()


def create_app(config_name):
    # config
    app = flask.Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)
    # extensions
    db.init_app(app)
    login_manager.init_app(app)
    hashing.init_app(app)
    mail.init_app(app)
    # blueprints
    app.register_blueprint(blueprints.api_blueprint)
    app.register_blueprint(blueprints.auth_blueprint)
    app.register_blueprint(blueprints.main_blueprint)
    return app
