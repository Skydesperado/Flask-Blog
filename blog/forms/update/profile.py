from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from flask_login import current_user

from blog.models.user import User


class UpdateProfileForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20, message="Username Must Be Between 4 and 20 Characters")])
	email = StringField("Email", validators=[DataRequired(), Email()])
	profile_picture = FileField("Profile Picture", validators=[FileAllowed(["jpg", "png"])])
	submit = SubmitField("Update")

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError("This Username Already Exists")

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError("This Email Already Exists")
