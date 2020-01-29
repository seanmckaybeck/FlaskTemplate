"""
All web forms for the application
"""
from flask.ext.wtf import Form
from wtforms import PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, EqualTo


class LoginForm(Form):
    email = EmailField('Email address', validators=[Required(message='An email address is required.'), Email()])
    password = PasswordField('Password', validators=[Required(message='A password is required.')])


class RegistrationForm(Form):
    email = EmailField('Email address', validators=[Required(message='You must enter an email address'), Email()])
    password = PasswordField('Password', validators=[Required(message='You must enter a password.'),
                                                     EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Repeat password', validators=[Required(message='You must confirm your password.')])
