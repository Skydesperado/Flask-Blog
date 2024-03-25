from flask import Blueprint, render_template

errors = Blueprint("errors", __name__)


@errors.errorhandler(403)
def HTTP_403(error):
    return render_template("blog/errors/403.html"), 403

@errors.errorhandler(404)
def HTTP_404(error):
    return render_template("blog/errors/404.html"), 404
