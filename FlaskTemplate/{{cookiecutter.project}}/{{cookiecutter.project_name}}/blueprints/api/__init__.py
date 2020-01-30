import flask


api_blueprint = flask.Blueprint("api", __name__)
from . import views
