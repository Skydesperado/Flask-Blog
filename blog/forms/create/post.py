from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CreatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    post_picture = FileField("Post Picture", validators=[FileAllowed(["jpg", "png"])])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")
