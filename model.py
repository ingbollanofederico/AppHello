from app import db
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class Permissions (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),unique=True,nullable=False)
    users = db.relationship('User',backref='permissions')

    def __repr__(self):
        return "<Role %r>" % self.name




