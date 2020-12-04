#import
from flask import Flask,render_template,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)

@app.route('/')
@app.route('/logout')
def landing():
    return render_template('landingPage.html')

@app.route('/homePage')
def homePage():
    return render_template('homePage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/search')
def search():
    return render_template('searchPage.html')



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
@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = loginForm()
    if login_form.validate_on_submit():
        user_info = User.query.filter_by(username=login_form.username.data).first()
        if user_info and bcrypt.check_password_hash(user_info.password, login_form.password.data):
            session['user_id'] = user_info.id
            session['name'] = user_info.name
            session['email'] = user_info.username
            session['role_id'] = user_info.role_id
            return redirect('dashboard')

    return render_template('Test/0_login.html', login_form=login_form)


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



