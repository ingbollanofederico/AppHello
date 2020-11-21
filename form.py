from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField
from wtforms.validators import DataRequired,Email,Length,ValidationError
import email_validator
from model import User, Role



class formRegisteration(FlaskForm):
    name=StringField('Name',validators=[DataRequired(),Length(min=3,max=25)])
    familyname=StringField('Family Name',validators=[DataRequired(),Length(min=3,max=25)])
    email=StringField('Email',validators=[DataRequired(),Email()])
    password=PasswordField('password',validators=[DataRequired(),Length(min=6,max=20)])
    submit=SubmitField('Register')

    # 4) As you know, the username is a unique value in the user's table, so if someone wants to
    # add the duplicated username, SQLAlchemy will raise an error, and it will give to a page long
    # error list. Please try to handle this error by adding a new instance attribute to the form
    # Object. Then show the user that your username has been taken.
    # Class formName(Flaskform)
    # ...
    # def validate_fieldname(self,fieldname) :
    # userid =User.query.filter_by(username=username.data).first()
    # if userid:
    # raise ValueError('username is exist!')

    def validate_email(self,email):
        user_check=User.query.filter_by(username=self.email.data).first()
        if user_check:
            raise ValidationError('This user has been register before or taken')

# 5)
class loginForm(FlaskForm):
    username=StringField('Name',validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[Length(min=3,max=15),DataRequired()])
    submit=SubmitField('Login')