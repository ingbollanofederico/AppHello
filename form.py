from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired,Email,Length,ValidationError, EqualTo
from app import User
from app import bcrypt


class formRegistration (FlaskForm):
    firstName = StringField('Name',validators=[DataRequired(),Length(min=3,max=25)])
    lastName = StringField('Last Name',validators=[DataRequired(),Length(min=3,max=25)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=6,max=20), EqualTo('repeat_password', message='Passwords must match')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=6, max=20)])
    permission = SelectField('Your Degree',
                             choices=[('1', 'High School Student'),
                                      ('2', 'Bachelor Student'),
                                      ('3', 'Master Student'),
                                      ('4', 'Graduated')], validators=[DataRequired()])
    submit = SubmitField('Register Account')

    def validate_email(self,email):
        user_check = User.query.filter_by(email=self.email.data).first()
        if user_check:
            raise ValidationError('This user has been register before or already taken')


class loginForm (FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[Length(min=3,max=15),DataRequired()])
    submit = SubmitField('Login')


class forgotPassword (FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class resetPassword (FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20),
                                                     EqualTo('repeat_password', message='Passwords must match')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=6, max=20)])
    submit = SubmitField('Reset Password')

class formSearch (FlaskForm):

    searchMethod = SelectField('Search Method',
                             choices=[('University', 'University'),
                                      ('Program', 'Degree Course'),
                                      ('Exam', 'Exam')], validators=[DataRequired()])
    city = SelectField('city', choices=[])
    acedemicDegree = SelectField('Academic Degree',
                               choices=[('%', 'All'),
                                        ('Laurea Triennale', 'Laurea Triennale'),
                                        ('Laurea Magistrale', 'Laurea Magistrale'),
                                        ('Laurea Magistrale Ciclo Unico', 'Laurea Magistrale Ciclo Unico')], validators=[DataRequired()])

    searchText = StringField('University, Degree Course, Exam')

    submit = SubmitField('Search')

class formReview(FlaskForm):
    '''
      gcapOption = Markup('<i class="rating__icon rating__icon--star fa fa-graduation-cap"></i>')
      radioStar = RadioField(gcapOption, choices=[('0' , '0star'),('1','1star'),('2','2star'),('3','3star'),('4','4star'),('5' , '5star')])
      starOption = Markup('<i class="rating__icon rating__icon--star fa fa-graduation-cap"></i>')'''

    ReviewTitle = StringField('Review', validators=[DataRequired(), Length(min=20, max=50)])
    Review = TextAreaField('Review', validators=[DataRequired(), Length(min=20, max=500)])
    submit = SubmitField('Submit Review')



class formEditProfile(FlaskForm):
    firstName = StringField('Name',validators=[DataRequired(),Length(min=3,max=25)])
    lastName = StringField('Last Name',validators=[DataRequired(),Length(min=3,max=25)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=6,max=20), EqualTo('repeat_password', message='Passwords must match')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=6, max=20)])
    permission = SelectField('Your Degree',
                             choices=[('1', 'High School Student'),
                                      ('2', 'Bachelor Student'),
                                      ('3', 'Master Student'),
                                      ('4', 'Graduated')], validators=[DataRequired()])
    submit = SubmitField('Register Account')

    def validate_email(self,email):
        user_check = User.query.filter_by(email=self.email.data).first()
        if user_check:
            raise ValidationError('This user has been register before or already taken')


