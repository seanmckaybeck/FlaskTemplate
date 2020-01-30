"""
Contains all of the database models
"""
import hashlib
import os
import time

import flask
import itsdangerous
import jwt

from . import db, hashing


class User(db.Model):
    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    salt = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)
    confirmed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    def __init__(self, email, password, salt):
        self.email = email
        self.password = password
        self.salt = salt

    def __repr__(self) -> str:
        return '<User %r>' % self.email

    def is_active(self) -> bool:
        return self.active

    def get_id(self) -> str:
        return self.email

    def is_authenticated(self) -> bool:
        return self.authenticated

    def is_anonymous(self) -> bool:
        return False
    
    @staticmethod
    def gen_password(password: str) -> Tuple[str, str]:
        salt = os.urandom(flask.current_app.config['SALT_LENGTH'])
        return hashing.hash_value(password, salt=salt), salt
    
    def avatar(self, size: int) -> str:
        digest = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    @staticmethod
    def generate_confirmation_token(email: str) -> str:
        serializer = itsdangerous.URLSafeTimedSerializer(flask.current_app.config['SECRET_KEY'])
        return serializer.dumps(email, salt=flask.current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def confirm_token(token: str, expiration: int=3600) -> str:
        serializer = itsdangerous.URLSafeTimedSerializer(flask.current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(
                token,
                salt=flask.current_app.config['SECURITY_PASSWORD_SALT'],
                max_age=expiration
            )
            return email
        except:
            return ""

    def get_reset_password_token(self, expires_in: int=600) -> str:
        return jwt.encode(
            {'user': self.id, 'expiry': time.time() + expires_in},
            flask.current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token: str) -> 'User':
        try:
            id = jwt.decode(token, flask.current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['user']
        except:
            return
        return User.query.get(id)
