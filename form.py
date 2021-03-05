from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo
from app import User
from app import bcrypt


class formRegistration(FlaskForm):
    firstName = StringField('Name', validators=[DataRequired(), Length(min=3, max=25)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20),
                                                     EqualTo('repeat_password', message='Passwords must match')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=6, max=20)])
    permission = SelectField('Your Degree',
                             choices=[('1', 'High School Student'),
                                      ('2', 'Bachelor Student'),
                                      ('3', 'Master Student'),
                                      ('4', 'Graduated')], validators=[DataRequired()])
    submit = SubmitField('Register Account')

    def validate_email(self, email):
        user_check = User.query.filter_by(email=self.email.data).first()
        if user_check:
            raise ValidationError('This user has been register before or already taken')


class loginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=3, max=15), DataRequired()])
    submit = SubmitField('Login')

class resetPassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20),
                                                     EqualTo('repeat_password', message='Passwords must match')])
    repeat_password = PasswordField('Repeat Password', validators=[DataRequired(), Length(min=6, max=20)])
    submit = SubmitField('Reset Password')


class formSearch(FlaskForm):
    searchMethod = SelectField('Search Method',
                               choices=[('University', 'University'),
                                        ('Program', 'Degree Course'),
                                        ('Exam', 'Exam')], validators=[DataRequired()])
    city = SelectField('city', choices=[])
    acedemicDegree = SelectField('Academic Degree',
                                 choices=[('%', 'All'),
                                          ('Laurea Triennale', 'Laurea Triennale'),
                                          ('Laurea Magistrale', 'Laurea Magistrale'),
                                          ('Laurea Magistrale Ciclo Unico', 'Laurea Magistrale Ciclo Unico')],
                                 validators=[DataRequired()])

    searchText = StringField('University, Degree Course, Exam')

    submit = SubmitField('Search')


class formReview(FlaskForm):
    ReviewTitle = StringField('Review', validators=[DataRequired(), Length(min=5, max=50)])
    Review = TextAreaField('Review', validators=[DataRequired(), Length(min=15, max=500)])
    starRating = RadioField('Star Rating', choices = [1,2,3,4,5,], validators=[DataRequired()])
    submit = SubmitField('Submit Review')


class formEditProfile(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=3, max=50)])
    lastName = StringField('Last Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    highestDegreeObtained = StringField('Highest Degree Obtained')
    currentInstitution = StringField('Current Institution')
    city = SelectField('city', choices=[])
    stateRegion = StringField('State Region')
    country = StringField('Country')
    submit = SubmitField('Submit Changes')

class formDeleteReview(FlaskForm):
    reviews = SelectField('Reviews', choices=[])
    submit = SubmitField('Delete Review')


