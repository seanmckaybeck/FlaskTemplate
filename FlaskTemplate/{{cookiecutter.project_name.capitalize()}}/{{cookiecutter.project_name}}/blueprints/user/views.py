from functools import wraps
import os
import time

from flask import render_template, abort, request, redirect, url_for, flash
# from flask_restful import Api, Resource, reqparse
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.hashing import Hashing
from itsdangerous import URLSafeTimedSerializer

from .mailgun import mailgun_notify
from stacktracker import app, db
from stacktracker.models import Coin, Item, User
from stacktracker.forms import CoinForm, ItemForm, LoginForm, RegistrationForm


# TODO finish

# ----------------
# helper functions
# ----------------
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except:
        return False


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('unconfirmed'))
        return func(*args, **kwargs)
    return decorated_function


def check_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin is False:
            return abort(404)
        return func(*args, **kwargs)
    return decorated_function


# -------------------------------------
# user login/logout/registration routes
# -------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user:
            if hashing.check_value(user.password, form.password.data, salt=user.salt):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect username or password.', 'error')
        else:
            flash('Incorrect username or password.', 'error')
    if request.method == 'POST' and not form.validate():
        flash_errors(form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if not user:
            salt = os.urandom(app.config['SALT_LENGTH'])
            pswd = hashing.hash_value(form.password.data, salt=salt)
            user = User(form.email.data, pswd, salt)
            db.session.add(user)
            db.session.commit()
            # ------------------
            # registration token
            # ------------------
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            send_email(user, html)
            flash('A confirmation email has been sent via email.', 'success')
            login_user(user)
            return redirect(url_for('unconfirmed'))
        else:
            # user exists
            flash('A user with that email already exists.', 'error')
    if request.method == 'POST' and not form.validate():
        flash_errors(form)
    return render_template('register.html', form=form)


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('unconfirmed'))
    user = User.query.get(email)
    if user:
        if user.confirmed:
            flash('Account already confirmed. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
            flash('You have confirmed your account. Thanks!', 'success')
            return redirect(url_for('index'))
    else:
        flash('Not a valid email address.', 'error')
        return redirect(url_for('unconfirmed'))


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('home')
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')


@app.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    send_email(current_user, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))
