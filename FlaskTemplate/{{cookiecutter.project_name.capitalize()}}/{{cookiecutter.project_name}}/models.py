"""
Contains all of the database models
"""
from {{cookiecutter.project_name}} import db


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

    def __repr__(self):
        return '<User %r>' % self.email

    def is_active(self):
        return self.active

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
