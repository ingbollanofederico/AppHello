from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField, SelectField
from wtforms.validators import DataRequired,Email,Length,ValidationError
from model import User


class formRegistration (FlaskForm):
    firstName = StringField('Name',validators=[DataRequired(),Length(min=3,max=25)])
    lastName = StringField('Last Name',validators=[DataRequired(),Length(min=3,max=25)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=6,max=20)])
    permission = SelectField('Your Degree',
                             choices=[('1', 'Undergraduate Student'),
                                      ('2', 'Bachelor Student'),
                                      ('3', 'Master Student'),
                                      ('4', 'Graduated')], validators=[DataRequired()])
    submit = SubmitField('Register')
    '''
    def validate_email(self,email):
        user_check = User.query.filter_by(email=self.email.data).first()
        if user_check:
            raise ValidationError('This user has been register before or taken')
   

class loginForm(FlaskForm):
    username = StringField('Name',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[Length(min=3,max=15),DataRequired()])
    submit = SubmitField('Login')
    '''