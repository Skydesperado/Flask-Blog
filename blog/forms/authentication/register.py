from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from blog.models.user import User


class RegisterForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired(), Length(min=4, max=20, message="Username Must Be Between 4 and 20 Characters")])
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords Must Match")])
	submit = SubmitField("Sign Up")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("This Username Already Exists")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data.lower()).first()
		if user:
			raise ValidationError("This Email Already Exists")
