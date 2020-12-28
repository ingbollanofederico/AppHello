from app import db


class Permissions (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),unique=True,nullable=False)
    users = db.relationship('User',backref='permissions')

    def __repr__(self):
        return "<Role %r>" % self.name

class University(db.Model):
    idUniversity        = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String(200), nullable=False)
    nickname            = db.Column(db.String(200), nullable=True)
    state               = db.Column(db.String(200))
    status              = db.Column(db.String(50))
    type                = db.Column(db.String(50))
    stataleLibera       = db.Column(db.String(50))
    geogrZone           = db.Column(db.String(50))
    address             = db.Column(db.String(50))
    dean                = db.Column(db.String(50))
    website             = db.Column(db.String(50))
    numberOfStudents    = db.Column(db.Integer)

    reviews             = db.relationship('Review', backref='university')
    programs            = db.relationship('Program', backref='university')

    def __repr__(self):
        return "<University %r>" % self.name, self.idUniversity

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
        return "<Exam %r>" % self.exam, self.idExam



     #'Corso di laurea - Politecnico di Torino Ing Gest'
class Program (db.Model):
    idProgram           = db.Column(db.Integer,primary_key=True)
    idUniversity        = db.Column(db.Integer,db.ForeignKey('university.idUniversity'), nullable=False)
    classLevel          = db.Column(db.String(50),nullable=False)
    className           = db.Column(db.String(50),nullable=False)
    courseName          = db.Column(db.String(50),nullable=False)
    sedeC               = db.Column(db.String(50),nullable=False)
    sedeP               = db.Column(db.String(50))
    language1           = db.Column(db.String(50),nullable=False,default="IT")
    language2           = db.Column(db.String(50))
    language3           = db.Column(db.String(50))

    exams               = db.relationship('Exam',   backref='program') #only here, not in the db
    reviews             = db.relationship('Review', backref='program')
    def __repr__(self):
        return "<Program %r>" % self.idProgram, self.className, self.courseName


class Review (db.Model):
    idReview            = db.Column(db.Integer,primary_key=True)
    idUser              = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sedeC               = db.Column(db.String(50), nullable=False)
    idUniversity        = db.Column(db.Integer, db.ForeignKey('university.idUniversity'), nullable=False)
    idProgram           = db.Column(db.Integer, db.ForeignKey('program.idProgram'), nullable=True)
    idExam              = db.Column(db.Integer, db.ForeignKey('exam.idExam'), nullable=True)
    review              = db.Column(db.String(400),unique=True,nullable=False)
    timeStamp           = db.Column(db.DateTime, nullable =False)

    def __repr__(self):
        return "<Review %r>" % self.idReview, self.review







'''
    #'Ateneo'
class University(db.Model):
    idUniversity        = db.Column(db.Integer, primary_key=True)
    name                = db.Column(db.String(200), nullable=False)
    nickname            = db.Column(db.String(200), nullable=True)
    state               = db.Column(db.String(200), nullable=False)
    status              = db.Column(db.String(50))
    stataleLibera       = db.Column(db.String(50))
    geogrZone           = db.Column(db.String(50))
    address             = db.Column(db.String(50))
    dean                = db.Column(db.String(50))
    website             = db.Column(db.String(50))
    numberOfStudents    = db.Column(db.Integer)

    def __repr__(self):
        return "<University %r>" % self.name

class Exam (db.Model):
    idExam              = db.Column(db.Integer,primary_key=True)
    name                = db.Column(db.String(50),unique=True,nullable=False)
    professor           = db.Column(db.String(50),nullable=False)
    assistant1          = db.Column(db.String(50), nullable=False)
    assistant2          = db.Column(db.String(50),nullable=False)
    CFU                 = db.Column(db.Integer)

    def __repr__(self):
        return "<Exam %r>" % self.Name, self.professor




     #'Corso di laurea - Politecnico di Torino Ing Gest'
class Program (db.Model):
    idProgram           = db.Column(db.String(50),primary_key=True)  #Foreign? Mix da creare
    nameProgram         = db.Column(db.String(50),nullable=False)
    descriptionProgram  = db.Column(db.String(50),nullable=False)
    classification      = db.Column(db.String(50),nullable=False)
    responsible         = db.Column(db.String(50),nullable=False)

    def __repr__(self):
        return "<Program %r>" % self.nameProgram, self.descriptionProgram

    #'classe di laurea - L8 LM31 ..'
class Classification(db.Model):
    idClass             = db.Column(db.String(50),primary_key=True)
    type                = db.Column(db.String(50),unique=False)
    name                = db.Column(db.String(50),unique=False)
    Name2         = db.Column(db.String(50), unique=False)

    def __repr__(self):
        return "<Class %r>" % self.idClass, self.name

    #'Esame'
class Esame (db.Model):
    idExam              = db.Column(db.String(50),primary_key=True)
    name                = db.Column(db.String(50),unique=True,nullable=False)
    professor           = db.Column(db.String(50),nullable=False)
    assistant1          = db.Column(db.String(50), nullable=False)
    assistant2          = db.Column(db.String(50),nullable=False)
    CFU                 = db.Column(db.Integer)

    def __repr__(self):
        return "<Exam %r>" % self.Name, self.professor

 #'Relazione Offerta Formativa'
class RelationProgram (db.Model):
    idProgram           = db.Column(db.Integer,db.ForeignKey('Program.idProgram'))
    idUser              = db.Column(db.String(200),db.ForeignKey('User.id'))
    idUniversity        = db.Column(db.String(200),db.ForeignKey('University.name'))
    idClassification    = db.Column(db.String(200),db.ForeignKey('Classification.idClass'))
    idExam              = db.Column(db.String(200),db.ForeignKey('Exam.idExam'))



   #'Recensione'
class Review (db.Model):
    idReview            = db.Column(db.Integer,primary_key=True)
    review              = db.Column(db.String(200),unique=True,nullable=False)
    author              = db.Column(db.String(50), nullable =False)

    def __repr__(self):
        return "<Review %r>" % self.id, self.review

    #'Relazione Recensioni'
class RelationReview (db.Model):
    idReview            = db.Column(db.Integer,db.ForeignKey('Review.idReview'))
    idUser              = db.Column(db.String(200),db.ForeignKey('User.id'))
    idUniversity        = db.Column(db.String(200),db.ForeignKey('University.name'))
    idProgram           = db.Column(db.String(200),db.ForeignKey('Program.idProgram'))
    idExam              = db.Column(db.String(200),db.ForeignKey('Exam.idExam'))
'''



