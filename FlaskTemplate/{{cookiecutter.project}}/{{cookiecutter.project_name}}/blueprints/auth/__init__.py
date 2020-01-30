import flask


auth_blueprint = flask.Blueprint("auth", __name__)
from . import views