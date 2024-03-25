from flask import render_template

from blog import app


@app.errorhandler(403)
def HTTP_403(error):
    return render_template("blog/errors/403.html"), 403
