import functools
import os
import time

import flask
import flask_login
import itsdangerous

from {{cookiecutter.project_name}} import db, login_manager, hashing
from {{cookiecutter.project_name}}.models import User
import {{cookiecutter.project_name}}.utils as utils
from .forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm
from . import auth_blueprint

# ----------------
# helper functions
# ----------------
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flask.flash(error, 'error')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


def check_confirmed(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        if flask_login.current_user.confirmed is False:
            flask.flash('Please confirm your account!', 'warning')
            return flask.redirect(flask.url_for('users.unconfirmed'))
        return func(*args, **kwargs)
    return decorated_function


def check_admin(func):
    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        if flask_login.current_user.is_admin is False:
            return flask.abort(404)
        return func(*args, **kwargs)
    return decorated_function


# -------------------------------------
# user login/logout/registration routes
# -------------------------------------
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user:
            if hashing.check_value(user.password, form.password.data, salt=user.salt):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                flask_login.login_user(user, remember=True)
                flask.flash('Successfully logged in!', 'success')
                return flask.redirect(flask.url_for('main.index'))
            else:
                flask.flash('Incorrect username or password.', 'error')
        else:
            flask.flash('Incorrect username or password.', 'error')
    if flask.request.method == 'POST' and not form.validate():
        flash_errors(form)
    return flask.render_template('auth/login.html', form=form)


@auth_blueprint.route('/logout')
@flask_login.login_required
def logout():
    user = flask_login.current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    flask_login.logout_user()
    return flask.redirect(flask.url_for('main.index'))


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if not user:
            pswd, salt = User.gen_password(form.password.data)
            user = User(form.email.data, pswd, salt)
            db.session.add(user)
            db.session.commit()
            # ------------------
            # registration token
            # ------------------
            token = User.generate_confirmation_token(user.email)
            confirm_url = flask.url_for('auth.confirm_email', token=token, _external=True)
            html = flask.render_template('auth/activate.html', confirm_url=confirm_url)
            utils.send_email(user, html)  # TODO
            flask.flash('A confirmation email has been sent via email.', 'success')
            flask_login.login_user(user)
            return flask.redirect(flask.url_for('auth.unconfirmed'))
        else:
            # user exists
            flask.flash('A user with that email already exists.', 'error')
    if flask.request.method == 'POST' and not form.validate():
        flash_errors(form)
    return flask.render_template('auth/register.html', form=form)


@auth_blueprint.route('/confirm/<token>')
@flask_login.login_required
def confirm_email(token: str):
    try:
        email = User.confirm_token(token)
    except:
        flask.flash('The confirmation link is invalid or has expired.', 'danger')
        return flask.redirect(flask.url_for('auth.unconfirmed'))
    user = User.query.get(email)
    if user:
        if user.confirmed:
            flask.flash('Account already confirmed. Please login.', 'success')
            return flask.redirect(flask.url_for('auth.login'))
        else:
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
            flask.flash('You have confirmed your account. Thanks!', 'success')
            return flask.redirect(flask.url_for('main.index'))
    else:
        flask.flash('Not a valid email address.', 'error')
        return flask.redirect(flask.url_for('auth.unconfirmed'))


@auth_blueprint.route('/unconfirmed')
@flask_login.login_required
def unconfirmed():
    if flask_login.current_user.confirmed:
        return flask.redirect('main.index')
    flask.flash('Please confirm your account!', 'warning')
    return flask.render_template('auth/unconfirmed.html')


@auth_blueprint.route('/resend')
@flask_login.login_required
def resend_confirmation():
    token = User.generate_confirmation_token(flask_login.current_user.email)
    confirm_url = flask.url_for('auth.confirm_email', token=token, _external=True)
    html = flask.render_template('auth/activate.html', confirm_url=confirm_url)
    utils.send_email(current_user, html)  # TODO
    flask.flash('A new confirmation email has been sent.', 'success')
    return flask.redirect(flask.url_for('auth.unconfirmed'))


@auth_blueprint.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)  # TODO
        flask.flash('Check your email for instructions to reset your password')
        return flask.redirect(flask.url_for('auth.login'))
    return flask.render_template('auth/reset_password_form.html',
                           title='Reset Password', form=form)

@auth_blueprint.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token: str):
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return flask.redirect(flask.url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        pswd, salt = User.gen_password(form.password.data)
        user.password = pswd
        user.salt = salt
        db.session.commit()
        flask.flash('Your password has been reset.')
        return flask.redirect(flask.url_for('auth.login'))
    return flask.render_template('reset_password.html', form=form)  # TODO
