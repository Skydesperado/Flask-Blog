from flask import current_app

from blog import db, login_manager

from flask_login import UserMixin

from itsdangerous import URLSafeTimedSerializer as Serializer

from blog.models.post import Post
from blog.models.comment import Comment


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    profile_picture = db.Column(db.String(20), nullable=False, default="default.png")
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    actions = db.relationship("UserAction", backref="user", lazy="dynamic")

    def get_reset_password_token(self, expires_seconds=1800):
        serializer = Serializer(current_app.config["SECRET_KEY"], expires_seconds)
        return serializer.dumps({"user_id": self.id}, salt="b4d3f76e8a2c1e5f")

    @staticmethod
    def verify_reset_password_token(token):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serializer.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.id}', '{self.username}', '{self.email}')"


class UserAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    action = db.Column(db.String(10), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "post_id", name="_user_post_uc"),)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.id}', '{self.action}')"
