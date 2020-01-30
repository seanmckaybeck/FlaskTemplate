"""
All web forms for the application
"""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Required, Email, EqualTo, DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Email address', validators=[Required(message='An email address is required.'), Email()])
    password = PasswordField('Password', validators=[Required(message='A password is required.')])


class RegistrationForm(FlaskForm):
    email = EmailField('Email address', validators=[Required(message='You must enter an email address'), Email()])
    password = PasswordField('Password', validators=[Required(message='You must enter a password.'),
                                                     EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Repeat password', validators=[Required(message='You must confirm your password.')])


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')
