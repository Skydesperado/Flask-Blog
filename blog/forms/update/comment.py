from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UpdateCommentForm(FlaskForm):
    content = StringField("Update Comment", validators=[DataRequired()])
    submit = SubmitField("Update")
