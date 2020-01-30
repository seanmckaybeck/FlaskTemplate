import flask


main_blueprint = flask.Blueprint("main", __name__)
from . import views
