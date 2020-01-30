import flask

from . import main_blueprint


main_blueprint.route("/")
def index():
    return flask.render_template("index.html")
