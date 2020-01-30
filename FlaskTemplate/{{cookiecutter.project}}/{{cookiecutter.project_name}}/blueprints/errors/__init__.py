import flask


errors_blueprint = flask.Blueprint("errors", __name__)
from . import views
