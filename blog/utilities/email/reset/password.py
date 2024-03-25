from blog import mail
from flask import url_for
from flask_mail import Message

def send_reset_password_email(user):
    token = user.get_reset_password_token()
    sender_email = "your-email@example.com"
    message = Message("Password Reset Request", sender=sender_email, recipients=[user.email])
    message.body = f"""To Reset Your Password, Visit The Following Link:
{url_for('reset_password', token=token, _external=True)}

If You Did Not Make This Request Then Simply Ignore This Email and No Changes Will Be Made
"""
    mail.send(message)
