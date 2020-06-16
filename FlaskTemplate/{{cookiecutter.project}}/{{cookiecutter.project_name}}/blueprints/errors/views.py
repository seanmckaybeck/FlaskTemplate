import flask

from . import errors_blueprint


@errors_blueprint.errorhandler(404)
def not_found_error(error):
    return flask.render_template("errors/404.html"), 404


@errors_blueprint.errorhandler(500)
def internal_server_error(error):
    return flask.render_template("errors/500.html"), 500
