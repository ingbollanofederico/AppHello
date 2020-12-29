#import
import os
import sqlite3
from flask import Flask,render_template,redirect,url_for,session, flash
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask_bcrypt import Bcrypt
from flask_mail import Mail,Message
from itsdangerous import Serializer
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, func



import db_connector

app = Flask(__name__)

#Database settings
app.config['SECRET_KEY']='sssdhgclshfsh;shd;jshjhsjhjhsjldchljk'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///website.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config['MAIL_SERVER']='smtp.mail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_SSL']=False
app.config['MAIL_TLS']=True
app.config['MAIL_USERNAME']=os.environ['EMAIL_USERNAME']
app.config['MAIL_PASSWORD']=os.environ['EMAIL_PASSWORD']

mail = Mail(app)

class User (db.Model):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(50),unique=True,nullable=False)
    firstName = db.Column(db.String(50),nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200),nullable=False)

    permissions_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))
    reviews = db.relationship('Review', backref='User')  # only here, not in the db

    #Token for password reset
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.email}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return "<User %r>" % self.firstName


from model import Permissions, Program, University, Exam
from form import formRegistration, loginForm, forgotPassword, formSearch


@app.route('/')
def landing():
    return render_template('landingPage.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

def searchFunction():

    '''create searchForm'''
    searchForm = formSearch()

    '''get all cities in the db & adding them to the searchForm'''
    cities = Program.query.order_by(Program.sedeP)
    myCities = []
    for x in cities:
        myCities.append(x.sedeP)

    myCities = list(dict.fromkeys(myCities))
    myCities.sort()
    myCities = ["All"] + myCities
    searchForm.city.choices = myCities

    return searchForm


@app.route('/homePage', methods=['POST','GET'])
def homePage():
    '''If logged in vs not logged in = 2 different views based on customer type/degree/characteristics'''
    program = Program.query.filter_by(sedeC="TORINO").all()

    '''Search Function'''
    searchForm = searchFunction()

    if searchForm.validate_on_submit():
        searchMethod = searchForm.searchMethod.data
        city = searchForm.city.data
        searchText = searchForm.searchText.data
        academicDegree = searchForm.acedemicDegree.data

        resultList = []
        searchForm2 = searchFunction()

        if(city == "All"):
            if(searchMethod == "University"):
                if (searchText == ""):
                    resultList = University.query.order_by(University.name).all()
                else:
                    searchText = "%"+searchText+"%"
                    resultList = University.query.filter(or_(University.name.ilike(searchText), University.nickname.ilike(searchText))).group_by(University.name).all()
            if (searchMethod == "Program"):
                if (searchText == ""):
                    resultList = Program.query.filter(Program.academicDegree.ilike(academicDegree)).group_by(Program.courseName).all()
                else:
                    searchText = "%" + searchText + "%"
                    resultList = Program.query.filter(and_(Program.academicDegree.ilike(academicDegree),
                                                           or_(Program.courseName.ilike(searchText), Program.className.ilike(searchText)))).group_by(Program.courseName).all()
            if (searchMethod == "Exam"):
                if (searchText == ""):
                    resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                        filter(Program.academicDegree.ilike(academicDegree)).group_by(Exam.exam).all()
                else:
                    searchText = "%" + searchText + "%"
                    resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                        filter(and_(Program.academicDegree.ilike(academicDegree),Exam.exam.ilike(searchText))).group_by(Exam.exam).all()
        else:
            if (searchMethod == "University"):
                if (searchText == ""):
                    resultList = University.query.join(Program, University.idUniversity == Program.idUniversity).\
                        filter(Program.sedeP.ilike(city)).all()
                else:
                    searchText = "%" + searchText + "%"
                    resultList = University.query.join(Program, University.idUniversity == Program.idUniversity). \
                        filter(and_(Program.sedeP.ilike(city), or_(University.name.ilike(searchText), University.nickname.ilike(searchText)))).all()
            if (searchMethod == "Program"):
                if (searchText == ""):
                    resultList = Program.query.filter(and_(Program.sedeP.ilike(city),Program.academicDegree.ilike(academicDegree))).group_by(Program.courseName).all()
                else:
                    searchText = "%" + searchText + "%"
                    resultList = Program.query.\
                        filter(and_(Program.sedeP.ilike(city),Program.academicDegree.ilike(academicDegree),
                                    or_(Program.courseName.ilike(searchText), Program.className.ilike(searchText)))).group_by(Program.courseName).all()

            if (searchMethod == "Exam"):
                if (searchText == ""):
                    resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                        filter(and_(Program.sedeP.ilike(city),Program.academicDegree.ilike(academicDegree))).group_by(Exam.exam).all()
                else:
                    searchText = "%" + searchText + "%"
                    resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                        filter(and_(Program.sedeP.ilike(city),Program.academicDegree.ilike(academicDegree), Exam.exam.ilike(searchText))).group_by(Exam.exam).all()

        if (len(resultList) ==0):
            flash('Your search does not match any information. Please try again!', 'warning')
            return render_template('searchPage.html', resultList=resultList, searchForm=searchForm2,
                                   searchMethod=searchMethod, city=city, acedemicDegree = academicDegree)
        else:


            if (searchMethod == "Program"):
                searchPageList = []
                for x in resultList:
                    searchPageList.append(x.courseName)

                searchPageList.sort()
                resultList = searchPageList

            if (searchMethod == "Exam"):
                searchPageList = []
                for x in resultList:
                    searchPageList.append(x.exam)

                searchPageList.sort()
                resultList = searchPageList


            return render_template('searchPage.html', resultList = resultList, searchForm=searchForm2, searchMethod = searchMethod,city= city, academicDegree=academicDegree)

    return render_template('homePage.html', program=program, searchForm=searchForm)

@app.route('/resultPage/<searchMethod>/<city>/<academicDegree>/<university>/<program>/<exam>', methods=['POST', 'GET'])
def resultPage(searchMethod,city,academicDegree, university,program,exam):

    '''query dive deep on university/course/exam + first 3 reviews'''
    searchForm = searchFunction()

    '''1 giro'''

    '''university nul null'''
        #'''to program'''
        #'''reviews universities'''

    '''null program null'''
       # '''to university'''
        #'''reviews program'''

    '''null null exam'''
       # '''to program'''
        #''reviews exam'''


    '''2 giro'''

    '''university program null'''
        # '''to exam'''
        # '''reviews program'''

    '''university program null - INUTILE'''
       # '''to exam'''
        # '''reviews program'''

    '''null program exam'''
       # '''to university'''
        #''reviews exam'''

    '''3 giro'''

    '''university program exam'''
        # '''reviews EXAM'''

    return render_template('resultPage.html', searchForm=searchForm, searchMethod = searchMethod,city= city, academicDegree=academicDegree )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'),500


@app.before_first_request
def setup():

    conn = db_connector.create_connection()

    #add here all the tables to be dropped during the setup
    tables_db = ['permissions']
    db_connector.dropTables(conn, tables_db)

    #create all the tables in the db (classes in model)
    db.create_all()

    #method 1 adding 1 item in the table
    cursor = conn.cursor()
    query1 = "INSERT INTO permissions VALUES (1,'High School Student')"
    cursor.execute(query1)
    conn.commit()
    conn.close()

    #method 2 adding 1 item in the table
    permission_bachelor = Permissions(name='Bachelor Student')
    permission_master = Permissions(name='Master Student')
    permission_graduated = Permissions(name='Graduated')

    db.session.add_all([permission_bachelor, permission_master,
                        permission_graduated])
    db.session.commit()

@app.route('/registration', methods=['POST','GET'])
def registration():
    if 'logged_in' in session:
        return redirect(url_for('homePage'))
    firstName = None
    lastName = None
    email = None
    permission = None
    registerForm = formRegistration()

    if registerForm.validate_on_submit():
        firstName = registerForm.firstName.data
        lastName = registerForm.lastName.data
        email = registerForm.email.data
        permission = registerForm.permission.data

        #ENCODE PASSWORD BEFORE ADDING IT
        password_1 = bcrypt.generate_password_hash(registerForm.password.data).encode('utf-8')

        #creation of the USER
        newUser = User(email=email, firstName=firstName, lastName=lastName,  password=password_1, permissions_id=permission)

        #save everything in the db
        db.session.add(newUser)
        db.session.commit()

        #send mail
        sendmail(registerForm.email.data,
                 'You have registred succesfully',
                 'mail',
                 firstName=registerForm.firstName.data,
                 email=registerForm.email.data,
                 password=registerForm.password.data)

        return redirect(url_for('login'))
    return render_template('registration.html',registerForm=registerForm)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('homePage'))
    login_form = loginForm()
    if login_form.validate_on_submit():
        user_info = User.query.filter_by(email=login_form.email.data).first()
        if user_info and bcrypt.check_password_hash(user_info.password, login_form.password.data):
            session['user_id'] = user_info.id
            session['first name'] = user_info.firstName
            session['last name'] = user_info.lastName
            session['email'] = user_info.email
            session['permissions_id'] = user_info.permissions_id
            session['logged_in'] = True
            return redirect('homePage')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', login_form=login_form)


@app.route('/forgot-password', methods=['POST', 'GET'])
def forgot_password():
    if 'logged_in' in session:
        return redirect(url_for('homePage'))

    forgot_password_form = forgotPassword()
    if forgot_password_form.validate_on_submit():
        user_info = User.query.filter_by(email=forgot_password_form.email.data).first()
        if user_info:
            token = user_info.get_reset_token()
            sendmail(forgot_password_form.email.data,
                     'Reset Password',
                     'reset_mail',
                     firstName=user_info.firstName,
                     email=forgot_password_form.email.data,
                     password=user_info.password,
                     token=token)
            flash('An email with instructions to reset your password has been sent to the specified account.', 'info')
        else:
            flash('User not found. Please check again the e-mail or register a new account.', 'danger')

    return render_template('forgot-password.html', forgot_password_form=forgot_password_form)


@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_password(token):
    if 'logged_in' in session:
        return redirect(url_for('homePage'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('Expired or invalid token', 'warning')
        return redirect(url_for('forgot-password'))

    reset_password_form = forgotPassword()
    if reset_password_form.validate_on_submit():
        password_1 = bcrypt.generate_password_hash(reset_password_form.password.data).encode('utf-8')
        pwd = password_1
        db.get_engine().connect().execute("""UPDATE user
                                                     SET pwd = '""" + pwd + """'
                                                     WHERE id = '""" + user.id + """'""")
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', title='Reset Password', reset_password_form=reset_password_form)


def sendmail(to, subject, template, **kwargs):
    msg=Message(subject,
                recipients=[to],
                sender=app.config['MAIL_USERNAME'])

    msg.html=render_template(template+'.html',**kwargs )
    mail.send(msg)

if __name__ == '__main__':
    app.run()

'''












######### old
app.config['SECRET_KEY']='sssdhgclshfsh;shd;jshjhsjhjhsjldchljk'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///website.db'

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
#prova push github

#prova push back

#pushpushback mat

#pushpushpushpush fed
from model import User,Role
from form import formRegisteration,loginForm

names=["Andrea","Elena","Edoardo","Francesco"]
posts=[
    {
    'author':'Mohammad',
    'title':'Flask session 1',
    'content' : 'please continue....',
    'date_posted':'19 Oct. 2020'
    },
    {
    'author': 'Andrea',
    'title': 'Flask session 2',
    'content': 'please continue....',
    'date_posted': '19 Oct. 2020'
    },
    {
    'author': 'Edoardo',
    'title': 'Flask session 3',
    'content': 'please continue....',
    'date_posted': '19 Oct. 2020'
    },
    {
    'author': 'Sina',
    'title': 'Flask session 4',
    'content': 'please continue....',
    'date_posted': '19 Oct. 2020'
    }
]



# Flask Lab Exercise #02
# 1) Please develop a web page which can get an id(integer number) then can return
# the corresponding name from this list:
# names=["Andrea","Elena","Edoardo","Francesco"]
@app.route('/student/<int:name_id>')
def student_page(name_id):
    if name_id<4:
        return '<h1>Hello %s !<\h1>' % names[name_id]
    else:
        return '<h1> your request is not inside the list</h1>'

# Flask Lab Exercise #01
# 2)Please develop a Flask application, which it can return names from the above list to
# the HTML code by using the render_template('page.html')
@app.route('/studnethtml/<int:name_id>')
def student_html_page(name_id):
    if name_id<4:
        student_name=names[name_id]
    else:
        student_name='Guest'

    return render_template('Test/page.html', student_name=student_name)

# Flask Lab Exercise #03
# 3)In this exercise, you need to work with static files; please add the bootstrap
# framework to your project and Develop an HTML page by using the CSS
# framework. In this practice, you need to use url_for('static', filename='pathfilename')
@app.route('/templatehtml')
def bootstrap():
    return render_template('Test/templatehtml.html')


# Flask Lab Exercise #04
# 4) Develop a webpage by using the template engine and show the list of posts on the
# page; the code has to develop by using the Jinja2 loop syntax.
# Note: The posts template is in the index of this document.
@app.route('/blog')
def posthtml():
    return render_template('Test/blog.html', posts=posts, name_website='IS 2020 Platform')

# Flask Lab Exercise #05
# 5) Develop a page by dividing one single HTML page into a sub-section by using Jinja
#    and Flask Framework.
#       *Layout.html: consist of a menu and main HTML like a header and other parts.
#       *Main.html: consist of your data which is coming from python
# please check the additional material
# This solution is for the blog page. We separated into the layout.html as base web page
# and blog-2.html as a content page
# we extend blog-2.html page from layout.html
@app.route('/bloglayout')
@app.route('/index')



@app.errorhandler(404)
def page_not_found(e):
    return render_template('Test/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('Test/500.html'), 500

# Flask Lab Exercise #06 and #07
# 6) and 7) Develop a webpage with webform that asks for the following information:
# Name
# Family name
# Email
# After submitting the webform, we would like to redirect the user to a welcome
# page and showing the client this sentence:
# Hello Mr. "name" "Family", please check your email!
@app.route('/register',methods=['POST','GET'])
def regiterPage():
    name=None
    regiterForm=formRegisteration()
    if regiterForm.validate_on_submit():
        name=regiterForm.name.data
        session['name']=regiterForm.name.data
        session['email']=regiterForm.email.data
        #TODO store on the db
        return redirect(url_for('dashboard'))
    return render_template('Test/register.html', regiterForm=regiterForm, name_website='Registration to IS 2020 Platform', name=name)

# The solution for Flask Lab Exercise #02 starts from here
# 1) solution is inside the model.py

# 2) In addition to the first Exercise, please create DB and fill the data by using the command
# line for the first time. Then you could add some line to your flask code(app.py) to create DB
# by trigging the first request.
# Recall:
# db.create_all(), app.before_first_request
@app.before_first_request
def setup():
    db.create_all()
    role_teacher = Role(name='Teacher')
    role_student = Role(name='Student')
    role_admin=Role(name='Admin')
    db.session.add_all([role_teacher,role_student,role_admin])
    db.session.commit()



# 3) Develop a registration page; this page will ask for user data like name, username, and
# password. Then it could save data to the database. Bcrypt lib should be used to generate a
# password from plaintext.
# Recall:
# db.session.add() or db.session.add_all([..,..,...])
# db.session.delete()
# db.session.commit()

@app.route('/registerdb',methods=['POST','GET'])
def regiterPagedb():
    name=None
    regiterForm=formRegisteration()
    if regiterForm.validate_on_submit():
        name=regiterForm.name.data
        session['name']=regiterForm.name.data
        session['email']=regiterForm.email.data
        password_2 = bcrypt.generate_password_hash(regiterForm.password.data).encode('utf-8')
        newuser = User(name=regiterForm.name.data, username=regiterForm.email.data, password=password_2, role_id=2)
        db.session.add(newuser)
        db.session.commit()
        return redirect(url_for('posthtml_layout'))
    return render_template('Test/register-db.html', regiterForm=regiterForm, name_website='SQL Registration to IS 2020 Platform', name=name)


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
# solution is inside the form.py

# 5) Develop a login page. This page has to verify the user data and then have to save the user
# data into the session variable and then redirect it to the profile page.



@app.route('/dashboard')
def dashboard():
    if session.get('email'):
        name=session.get('name')
        return render_template('Test/dashboard.html', name=name)
    else:
        return redirect(url_for('login'))
    
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('posthtml_layout')) # =>redirect(index)

'''



