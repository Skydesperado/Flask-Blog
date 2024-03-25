import os

from flask import Flask

from flask_bcrypt import Bcrypt

from flask_login import LoginManager

from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = "main.login"
login_manager.login_message = "Please Login"
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../blog/database/sqlite3.db"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_SERVER"] = "smtp.googlemail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from blog.main.routes import main
    from blog.utilities.errors.errors import errors
    app.register_blueprint(main)
    app.register_blueprint(errors)

    create_db_tables(app)

    return app

def create_db_tables(app):
    with app.app_context():
        db.create_all()
