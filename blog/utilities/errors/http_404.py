from flask import render_template

from blog import app


@app.errorhandler(404)
def HTTP_404(error):
    return render_template("blog/errors/404.html"), 404
