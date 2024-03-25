import datetime

from blog import db

from blog.models.comment import Comment


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    post_picture = db.Column(db.String(20), nullable=True)
    content = db.Column(db.Text, nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    comments = db.relationship("Comment", backref="post", cascade="all, delete-orphan", lazy="dynamic")
    actions = db.relationship("UserAction", backref="post", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.id}', '{self.title}', {self.content}, '{self.created_at}')"
