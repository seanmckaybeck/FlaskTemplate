import flask
import flask.ext.login as flask_login
import flask.ext.sqlalchemy as flask_sqlalchemy

import config
import utils


db = flask_sqlalchemy.SQLAlchemy()
login_manager = flask_login.LoginManager()


def create_app(config_name):
    app = flask.Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    # TODO register blueprints
    return app
