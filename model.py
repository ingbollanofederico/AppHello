from app import db


class Permissions (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),unique=True,nullable=False)
    users = db.relationship('User',backref='permissions')

    def __repr__(self):
        return "<Role %r>" % self.name


class University(db.Model):
    idUniversity = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(200), nullable=False)
    state = db.Column(db.String(200))
    region = db.Column(db.String(50))
    staticLogo = db.Column(db.String(400))
    website = db.Column(db.String(200))
    address = db.Column(db.String(50))
    Cap = db.Column(db.String(50))
    Tel = db.Column(db.String(50))
    Fax = db.Column(db.Integer)

    reviews             = db.relationship('Review', backref='university')
    programs            = db.relationship('Program', backref='university')

    def __repr__(self):
        return "<University %r>" % self.name

    def display (self):
        return "%s" % self.name


class Exam (db.Model):
    idExam              = db.Column(db.Integer,primary_key=True)
    idProgram           = db.Column(db.Integer,db.ForeignKey('program.idProgram'), nullable=False)
    exam                = db.Column(db.String(50),nullable=False)
    Reference           = db.Column(db.String(50))
    SSD                 = db.Column(db.String(50))
    language            = db.Column(db.String(50))
    credits             = db.Column(db.Integer)
    teachingStaff       = db.Column(db.String(200))

    reviews = db.relationship('Review', backref='exam')
    def __repr__(self):
        return "<Exam %r>" % self.exam

    def display(self):
        return "%s" % self.exam


class Program (db.Model):
    idProgram           = db.Column(db.Integer,primary_key=True)
    idUniversity        = db.Column(db.Integer,db.ForeignKey('university.idUniversity'), nullable=False)
    classLevel          = db.Column(db.String(50),nullable=False)
    className           = db.Column(db.String(50),nullable=False)
    courseName          = db.Column(db.String(50),nullable=False)
    sedeC               = db.Column(db.String(50),nullable=False)
    sedeP               = db.Column(db.String(50),nullable=False)
    language1           = db.Column(db.String(50),nullable=False,default="IT")
    language2           = db.Column(db.String(50))
    language3           = db.Column(db.String(50))
    academicDegree      = db.Column(db.String(200), nullable=False)

    exams               = db.relationship('Exam',   backref='program') #only here, not in the db
    reviews             = db.relationship('Review', backref='program')

    def __repr__(self):
        return "<Program %r>" % self.courseName

    def display(self):
        return "%s - (%s %s)" % (self.courseName, self.classLevel, self.className )

class Review (db.Model):
    idReview            = db.Column(db.Integer,primary_key=True)
    idUser              = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sedeC               = db.Column(db.String(50), nullable=False)
    idUniversity        = db.Column(db.Integer, db.ForeignKey('university.idUniversity'), nullable=False)
    idProgram           = db.Column(db.Integer, db.ForeignKey('program.idProgram'), nullable=True)
    idExam              = db.Column(db.Integer, db.ForeignKey('exam.idExam'), nullable=True)
    reviewTitle         = db.Column(db.String(200), nullable=False)
    review              = db.Column(db.String(400), nullable=False)
    timeStamp           = db.Column(db.DateTime)
    starRating          = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return "Review %s - %s" % (self.reviewTitle, self.review)

    def display(self):
        return "%s " % self.review

#class User is in App.py


