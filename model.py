from app import db


class User (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(50),unique=True,nullable=False)
    firstName = db.Column(db.String(50),nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200),nullable=False)
    permissions_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))

    def __repr__(self):
        return "<User %r>" % self.firstName, self.lastName


class Permissions (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),unique=True,nullable=False)
    users = db.relationship('User',backref='permissions')

    def __repr__(self):
        return "<Role %r>" % self.name




