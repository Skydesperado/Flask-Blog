from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CreateCommentForm(FlaskForm):
    content = StringField("Comment", validators=[DataRequired()])
    submit = SubmitField("Comment")
