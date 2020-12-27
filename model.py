from app import db


class Permissions (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200),unique=True,nullable=False)
    users = db.relationship('User',backref='permissions')

    def __repr__(self):
        return "<Role %r>" % self.name
''''
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



