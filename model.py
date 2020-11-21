from app import db

# The solution for Flask Lab Exercise #02 starts from here
# Flask #E02 #01
# 1) Please develop a Class to save user's data with the user's Role on the database. This class
# object should develop by using SQLAlchemy. The DB has to have two different tables, i.e.,
# User and Role. The user has id, name, username, email, password, and role_id. The Role
# has id and Role. The role_id is a ForeignKey to Role table.
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable=False)
    name=db.Column(db.String(50),nullable=False)
    password=db.Column(db.String(200),nullable=False)
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'))

    def __repr__(self):
        return "<User %r>" % self.name



class Role(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    users=db.relationship('User',backref='role')

    def __repr__(self):
        return "<Role %r>" % self.name