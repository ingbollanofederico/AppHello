# import
import datetime
import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import Serializer
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_, func

import db_connector

app = Flask(__name__)

# Database settings
app.config['SECRET_KEY'] = 'sssdhgclshfsh;shd;jshjhsjhjhsjldchljk'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///website.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config['MAIL_SERVER'] = 'smtp.mail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_SSL'] = False
app.config['MAIL_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ['EMAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['EMAIL_PASSWORD']

mail = Mail(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    highestDegreeObtained = db.Column(db.String(100))
    currentInstitution = db.Column(db.String(100))
    city = db.Column(db.String(100))
    stateRegion = db.Column(db.String(100))
    country = db.Column(db.String(100))

    permissions_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))
    reviews = db.relationship('Review', backref='User')  # only here, not in the db


from model import Permissions, Program, University, Exam, Review
from form import formRegistration, loginForm, formSearch, formReview, formEditProfile, formDeleteReview


@app.route('/')
def landing():
    return render_template('landingPage.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You logged out successfully', 'warning')
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


def searchValidator(searchForm):
    searchMethod = searchForm.searchMethod.data
    city = searchForm.city.data
    searchText = searchForm.searchText.data
    academicDegree = searchForm.acedemicDegree.data

    resultList = []
    searchForm2 = searchFunction()

    # Start of the search engine. The search engine is composed by 2 main functions: searchValidator and ResultValidator
    # SearchValidator implements the logic of the different type of researches that an user can do:
    # searching a university, a specific degree course or a specific exam
    # ResultValidator implements the logic of the different type of choices that the user made and match them with the relative reviews.
    # The ResultValidator is the powerful logic that connects reviews, information regarding universities, degree courses and exam and
    # the possibility of the user to interact with the platform by contributing with reviews and opinions

    # SearchValidator: the following code explore all the possible combination made by the user and the filter applied to the research
    # The output of this function is a result list with the elements researched and filtered by the user

    if city == "All":
        if searchMethod == "University":
            if searchText == "":
                resultList = University.query.order_by(University.name).all()
            else:
                searchText = "%" + searchText + "%"
                resultList = University.query.filter(
                    or_(University.name.ilike(searchText), University.nickname.ilike(searchText))).group_by(
                    University.name).all()
        if searchMethod == "Program":
            if searchText == "":
                resultList = Program.query.filter(Program.academicDegree.ilike(academicDegree)).group_by(
                    Program.courseName).all()
            else:
                searchText = "%" + searchText + "%"
                resultList = Program.query.filter(and_(Program.academicDegree.ilike(academicDegree),
                                                       or_(Program.courseName.ilike(searchText),
                                                           Program.className.ilike(searchText)))).group_by(
                    Program.courseName).all()
        if searchMethod == "Exam":
            if searchText == "":
                resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                    filter(Program.academicDegree.ilike(academicDegree)).group_by(Exam.exam).all()
            else:
                searchText = "%" + searchText + "%"
                resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                    filter(and_(Program.academicDegree.ilike(academicDegree), Exam.exam.ilike(searchText))).group_by(
                    Exam.exam).all()
    else:
        if searchMethod == "University":
            if searchText == "":
                resultList = University.query.join(Program, University.idUniversity == Program.idUniversity). \
                    filter(Program.sedeP.ilike(city)).all()
            else:
                searchText = "%" + searchText + "%"
                resultList = University.query.join(Program, University.idUniversity == Program.idUniversity). \
                    filter(and_(Program.sedeP.ilike(city),
                                or_(University.name.ilike(searchText), University.nickname.ilike(searchText)))).all()
        if searchMethod == "Program":
            if searchText == "":
                resultList = Program.query.filter(
                    and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree))).group_by(
                    Program.courseName).all()
            else:
                searchText = "%" + searchText + "%"
                resultList = Program.query. \
                    filter(and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                                or_(Program.courseName.ilike(searchText),
                                    Program.className.ilike(searchText)))).group_by(Program.courseName).all()
        if searchMethod == "Exam":
            if searchText == "":
                resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                    filter(and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree))).group_by(
                    Exam.exam).all()
            else:
                searchText = "%" + searchText + "%"
                resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                    filter(and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                                Exam.exam.ilike(searchText))).group_by(Exam.exam).all()

    # The following section asses whether the search made by the user found any possible matches in the db.
    # In case there are no matches: the webpage will show an alert message inviting to try a new search
    # In case there are matches in the DB: the algorithm will dive depp and search for all the reviews present in the system for the choice made.
    # For each element of the research found on the DB, the logic will try to match all the review present for that specific element regardless the level of the hierarchy

    if len(resultList) == 0:
        flash('Your search does not match any information. Please try again!', 'warning')
        return render_template('searchPage.html', resultList=resultList, searchForm=searchForm2,
                               searchMethod=searchMethod, city=city, acedemicDegree=academicDegree)
    else:
        firstSearch = searchMethod
        dictReviews = {}

        if firstSearch == "University" or firstSearch == "Program" or firstSearch == "Exam":
            for x in resultList:
                if firstSearch == "University":

                    reviewList = Review.query.join(University, University.idUniversity == Review.idUniversity). \
                        filter_by(idUniversity=x.idUniversity).order_by(Review.starRating.desc()).all()

                    dictReviews[x.idUniversity] = reviewList

                elif firstSearch == "Program":

                    reviewList = Review.query.join(Program, Program.idProgram == Review.idProgram).join(University,
                                                                                                        University.idUniversity == Program.idUniversity). \
                        filter(Program.courseName.ilike(x.courseName)).order_by(Review.starRating.desc()).all()

                    dictReviews[x.courseName] = reviewList

                elif firstSearch == "Exam":

                    reviewList = Review.query.join(Exam, Exam.idExam == Review.idExam).join(Program,
                                                                                            Exam.idProgram == Program.idProgram).join(
                        University, University.idUniversity == Program.idUniversity). \
                        filter(Exam.exam.ilike(x.exam)).order_by(Review.starRating.desc()).all()

                    dictReviews[x.exam] = reviewList

        numberOfReviews = 0
        dictRatingReviews = {}

        # This part of the code aggregates the all review for each element of the dictionary and calculates the
        # mathematical average of the star reviews given to that specific element.

        if searchMethod == "University":
            for result in resultList:
                numberOfReviews = len(dictReviews[result.idUniversity])
                averageValue = 0
                star1 = 0.0
                star2 = 0.0
                star3 = 0.0
                star4 = 0.0
                star5 = 0.0
                for review in dictReviews[result.idUniversity]:
                    averageValue = averageValue + review.starRating
                    if review.starRating <= 1:
                        star1 = star1 + 1
                    elif review.starRating > 1 and review.starRating <= 2:
                        star2 = star2 + 1
                    elif review.starRating > 2 and review.starRating <= 3:
                        star3 = star3 + 1
                    elif review.starRating > 3 and review.starRating <= 4:
                        star4 = star4 + 1
                    elif review.starRating > 4 and review.starRating <= 5:
                        star5 = star5 + 1

                if averageValue > 0:
                    averageValue = averageValue / numberOfReviews
                    star1 = (star1 / numberOfReviews) * 100
                    star2 = (star2 / numberOfReviews) * 100
                    star3 = (star3 / numberOfReviews) * 100
                    star4 = (star4 / numberOfReviews) * 100
                    star5 = (star5 / numberOfReviews) * 100

                dictRatingReviews[result.idUniversity] = [round(averageValue, 2), numberOfReviews, star1, star2, star3,
                                                          star4, star5]

        elif searchMethod == "Program":
            for result in resultList:
                numberOfReviews = len(dictReviews[result.courseName])
                averageValue = 0
                star1 = 0.0
                star2 = 0.0
                star3 = 0.0
                star4 = 0.0
                star5 = 0.0
                for review in dictReviews[result.courseName]:
                    averageValue = averageValue + review.starRating
                    if (review.starRating <= 1):
                        star1 = star1 + 1
                    elif (review.starRating > 1 and review.starRating <= 2):
                        star2 = star2 + 1
                    elif (review.starRating > 2 and review.starRating <= 3):
                        star3 = star3 + 1
                    elif (review.starRating > 3 and review.starRating <= 4):
                        star4 = star4 + 1
                    elif (review.starRating > 4 and review.starRating <= 5):
                        star5 = star5 + 1

                if averageValue > 0:
                    averageValue = averageValue / numberOfReviews
                    star1 = (star1 / numberOfReviews) * 100
                    star2 = (star2 / numberOfReviews) * 100
                    star3 = (star3 / numberOfReviews) * 100
                    star4 = (star4 / numberOfReviews) * 100
                    star5 = (star5 / numberOfReviews) * 100

                dictRatingReviews[result.courseName] = [round(averageValue, 2), numberOfReviews, star1, star2, star3,
                                                        star4, star5]

        elif searchMethod == "Exam":
            for result in resultList:
                numberOfReviews = len(dictReviews[result.exam])
                averageValue = 0
                star1 = 0.0
                star2 = 0.0
                star3 = 0.0
                star4 = 0.0
                star5 = 0.0
                for review in dictReviews[result.exam]:
                    averageValue = averageValue + review.starRating
                    if (review.starRating <= 1):
                        star1 = star1 + 1
                    elif (review.starRating > 1 and review.starRating <= 2):
                        star2 = star2 + 1
                    elif (review.starRating > 2 and review.starRating <= 3):
                        star3 = star3 + 1
                    elif (review.starRating > 3 and review.starRating <= 4):
                        star4 = star4 + 1
                    elif (review.starRating > 4 and review.starRating <= 5):
                        star5 = star5 + 1

                if averageValue > 0:
                    averageValue = averageValue / numberOfReviews
                    star1 = (star1 / numberOfReviews) * 100
                    star2 = (star2 / numberOfReviews) * 100
                    star3 = (star3 / numberOfReviews) * 100
                    star4 = (star4 / numberOfReviews) * 100
                    star5 = (star5 / numberOfReviews) * 100

                dictRatingReviews[result.exam] = [round(averageValue, 2), numberOfReviews, star1, star2, star3, star4,
                                                  star5]

        return render_template('searchPage.html', resultList=resultList, searchForm=searchForm2, city=city,
                               academicDegree=academicDegree, searchMethod=searchMethod, dictReviews=dictReviews,
                               dictRatingReviews=dictRatingReviews)


@app.route('/homePage', methods=['POST', 'GET'])
def homePage():
    '''If logged in vs not logged in = 2 different views based on customer type/degree/characteristics'''
    program = Program.query.filter_by(sedeC="TORINO").all()

    '''Search Function'''
    searchForm = searchFunction()

    if searchForm.validate_on_submit():
        return searchValidator(searchForm)

    return render_template('homePage.html', program=program, searchForm=searchForm)


def resultValidator(searchForm, searchMethod, city, academicDegree, university, program, exam):
    resultList = []
    dictReviews = {}

    # The ResultValidator is the powerful logic that connects reviews, information regarding universities, degree courses and exam and
    # the possibility of the user to interact with the platform by contributing with reviews and opinions

    # The following code implements the search logic after the user made the first choice. Depending on the results that the user
    # wants to see based on the first level of granularity shown in the search page, the search engine will try to find any match
    # on the next level of granularity (i.e if the user chose university, the search engine will look for all the programs that the specific university can offer)

    # The logic have been pre defined by us as developers in the following way:

    # UNIVERSITY FLOW (TOP DOWN): If the user chose a specific university, the search engine will show all the degree courses available in that university.
    # In case the user will choose a specific degree course, the search engine will go deeper in the granularity and show all the exams of that degree course in that specific university (if anyone available in the db)

    # DEGREE COURSE FLOW: If the user chose a specific Degree Course, the search engine will show all the universities in which that degree course is available (i.e Management Engineering -> Polito, Polimi, etc)
    # In case the user will choose a specific university, the search engine will go deeper in the granularity and show all the exams of that degree course in that specific university (if anyone available in the db)

    # EXAMS FLOW (BOTTOM UP): If the user chose a specific Exam, the search engine will show all the programs in which that exam is required.
    # In case the user will choose a specific degree course, the search engine will go deeper in the granularity and show all the universities providing that exam in that specific degree course.

    # These 3 approaches allow the user to choose where to start the research, and aggregate data at the level of the granularity desired by the user.

    # A parallel stream are the reviews that are aggregated at a level of granularity lower than the level of research.
    # When the user selects a specific university, he will see all the reviews of all the specific degree courses of that university.
    # The aggregation is done at a lower level respect to the choice made (i.e university vs reviews all programs of that university).
    # This choice of asymmetry in the query at the db allows the user to visualize the reviews of the next level of granularity in order to better fine tune the research when going down in the dive deep.

    if university != "null" and program == "null" and exam == "null":
        if city == "All":
            resultList = Program.query.join(University, University.idUniversity == Program.idUniversity). \
                filter(
                and_(Program.academicDegree.ilike(academicDegree), Program.idUniversity.ilike(university))).group_by(
                Program.courseName).all()
            searchMethod = "Program"
        else:
            resultList = Program.query.join(University, University.idUniversity == Program.idUniversity). \
                filter(
                and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                     Program.idUniversity.ilike(university))).group_by(Program.courseName).all()
            searchMethod = "Program"

        # For all the different results to be shown in the page, it is created a dictionary using as a key the element of the list (result list)
        # and as a value the array/list of reviews for that specific key

        for x in resultList:
            reviewList = Review.query.join(Program, Program.idProgram == Review.idProgram).join(University,
                                                                                                University.idUniversity == Program.idUniversity). \
                filter(and_(Program.courseName.ilike(x.courseName), Program.idUniversity.ilike(university))).order_by(
                Review.timeStamp.desc()).all()

            dictReviews[x.courseName] = reviewList

    elif university == "null" and program != "null" and exam == "null":
        if city == "All":
            resultList = University.query.join(Program, University.idUniversity == Program.idUniversity). \
                filter(and_(Program.academicDegree.ilike(academicDegree), Program.courseName.ilike(program))).group_by(
                University.name).all()
            searchMethod = "University"
        else:
            resultList = University.query.join(Program, University.idUniversity == Program.idUniversity). \
                filter(and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                            Program.courseName.ilike(program))).group_by(University.name).all()
            searchMethod = "University"

        for x in resultList:
            reviewList = Review.query.join(Program, Program.idProgram == Review.idProgram).join(University,
                                                                                                University.idUniversity == Program.idUniversity). \
                filter(and_(Program.courseName.ilike(program), Program.idUniversity.ilike(x.idUniversity))).order_by(
                Review.timeStamp.desc()).all()

            dictReviews[x.idUniversity] = reviewList

    elif university == "null" and program == "null" and exam != "null":
        if city == "All":
            resultList = Program.query.join(Exam, Exam.idProgram == Program.idProgram). \
                filter(and_(Program.academicDegree.ilike(academicDegree), Exam.exam.ilike(exam))).group_by(
                Program.courseName).all()
            searchMethod = "Program"
        else:
            resultList = Program.query.join(Exam, Exam.idProgram == Program.idProgram). \
                filter(
                and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                     Exam.exam.ilike(exam))).group_by(Program.courseName).all()
            searchMethod = "Program"

        for x in resultList:
            reviewList = Review.query.join(Exam, Exam.idExam == Review.idExam).join(Program,
                                                                                    Exam.idProgram == Program.idProgram).join(
                University, University.idUniversity == Program.idUniversity). \
                filter(and_(Program.courseName.ilike(x.courseName), Exam.exam.ilike(exam))).order_by(
                Review.timeStamp.desc()).all()

            dictReviews[x.courseName] = reviewList

    elif university != "null" and program != "null" and exam == "null":
        if city == "All":
            resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                filter(and_(Program.academicDegree.ilike(academicDegree), Program.courseName.ilike(program),
                            Program.idUniversity.ilike(university))).group_by(
                Exam.exam).all()
            searchMethod = "Exam"
        else:
            resultList = Exam.query.join(Program, Exam.idProgram == Program.idProgram). \
                filter(and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                            Program.courseName.ilike(program),
                            Program.idUniversity.ilike(university))).group_by(Exam.exam).all()
            searchMethod = "Exam"

        for x in resultList:
            reviewList = Review.query.join(Exam, Exam.idExam == Review.idExam).join(Program,
                                                                                    Exam.idProgram == Program.idProgram).join(
                University, University.idUniversity == Program.idUniversity). \
                filter(and_(Program.courseName.ilike(program), Exam.exam.ilike(x.exam),
                            Program.idUniversity.ilike(university))).order_by(
                Review.timeStamp.desc()).all()

            dictReviews[x.exam] = reviewList

    elif university == "null" and program != "null" and exam != "null":
        if city == "All":
            resultList = University.query.join(
                Program, University.idUniversity == Program.idUniversity).join(
                Exam, Program.idProgram == Exam.idProgram).filter(
                and_(Program.academicDegree.ilike(academicDegree), Program.courseName.ilike(program),
                     Exam.exam.ilike(exam))).group_by(University.name).all()
            searchMethod = "University"
        else:
            resultList = University.query.join(
                Program, University.idUniversity == Program.idUniversity).join(
                Exam, Program.idProgram == Exam.idProgram).filter(
                and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                     Program.courseName.ilike(program),
                     Exam.exam.ilike(exam))).group_by(University.name).all()
            searchMethod = "University"

        for x in resultList:
            reviewList = Review.query.join(Exam, Exam.idExam == Review.idExam).join(Program,
                                                                                    Exam.idProgram == Program.idProgram).join(
                University, University.idUniversity == Program.idUniversity). \
                filter(and_(Program.courseName.ilike(program), Exam.exam.ilike(exam),
                            Program.idUniversity.ilike(x.idUniversity))).order_by(
                Review.timeStamp.desc()).all()

            dictReviews[x.idUniversity] = reviewList

    elif university != "null" and program != "null" and exam != "null":
        if city == "All":
            resultList = Exam.query.join(
                Program, Program.idProgram == Exam.idProgram).join(
                University, University.idUniversity == Program.idUniversity).filter(
                and_(Program.academicDegree.ilike(academicDegree), Program.courseName.ilike(program),
                     Exam.exam.ilike(exam), Program.idUniversity.ilike(university))).group_by(Exam.exam).all()
            searchMethod = "EndSearch"
        else:
            resultList = Exam.query.join(
                Program, Program.idProgram == Exam.idProgram).join(
                University, University.idUniversity == Program.idUniversity).filter(
                and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                     Program.courseName.ilike(program),
                     Exam.exam.ilike(exam), Program.idUniversity.ilike(university))).group_by(Exam.exam).all()
            searchMethod = "EndSearch"

        for x in resultList:
            reviewList = Review.query.join(Exam, Exam.idExam == Review.idExam).join(Program,
                                                                                    Exam.idProgram == Program.idProgram).join(
                University, University.idUniversity == Program.idUniversity). \
                filter(and_(Program.courseName.ilike(program), Exam.exam.ilike(x.exam),
                            Program.idUniversity.ilike(university))).order_by(
                Review.timeStamp.desc()).all()

            dictReviews[x.exam] = reviewList
    else:
        flash('Your search has been altered during your request! Please try to search it again.', 'warning')

    university_object = "null"
    if university != "null":
        university_object = University.query.filter_by(idUniversity=university).all()

    # This part of the code asses whether the next layer of granularity is available or not.
    # In case it is not available (that means that the search process can't go on), the search engine will come back to the
    # last level of granularity available and will search for all of the reviews at that specific level.

    if len(resultList) == 0:
        if searchMethod == "Program":
            resultList = university
            reviewList = Review.query.join(University, University.idUniversity == Review.idUniversity). \
                filter_by(idUniversity=university).order_by(Review.timeStamp.desc()).all()

            dictReviews[university] = reviewList
            searchMethod = "EndSearchUniversity"
        if searchMethod == "Exam":
            resultList = program
            reviewList = Review.query.join(Program, Program.idProgram == Review.idProgram).join(University,
                                                                                                University.idUniversity == Program.idUniversity). \
                filter(and_(Program.courseName.ilike(program), Program.idUniversity.ilike(university))).order_by(
                Review.timeStamp.desc()).all()

            dictReviews[program] = reviewList
            searchMethod = "EndSearchProgram"

    numberOfReviews = 0
    RatingReviews = []

    # This part of the code aggregates the all review for each element of the dictionary and calculates the
    # mathematical average of the star reviews given to that specific element.

    if searchMethod == "University":
        numberOfReviews = 0
        averageValue = 0
        star1 = 0.0
        star2 = 0.0
        star3 = 0.0
        star4 = 0.0
        star5 = 0.0
        for result in resultList:
            # overall rew
            numberOfReviews = numberOfReviews + len(dictReviews[result.idUniversity])
            for review in dictReviews[result.idUniversity]:
                averageValue = averageValue + review.starRating
                if review.starRating <= 1:
                    star1 = star1 + 1
                elif review.starRating > 1 and review.starRating <= 2:
                    star2 = star2 + 1
                elif review.starRating > 2 and review.starRating <= 3:
                    star3 = star3 + 1
                elif review.starRating > 3 and review.starRating <= 4:
                    star4 = star4 + 1
                elif review.starRating > 4 and review.starRating <= 5:
                    star5 = star5 + 1

        if averageValue > 0:
            averageValue = averageValue / numberOfReviews
            star1 = (star1 / numberOfReviews) * 100
            star2 = (star2 / numberOfReviews) * 100
            star3 = (star3 / numberOfReviews) * 100
            star4 = (star4 / numberOfReviews) * 100
            star5 = (star5 / numberOfReviews) * 100

        RatingReviews = [round(averageValue, 2), numberOfReviews, star1, star2, star3,
                         star4, star5]

    elif searchMethod == "Program":
        numberOfReviews = 0
        averageValue = 0
        star1 = 0.0
        star2 = 0.0
        star3 = 0.0
        star4 = 0.0
        star5 = 0.0
        for result in resultList:
            numberOfReviews = numberOfReviews + len(dictReviews[result.courseName])
            for review in dictReviews[result.courseName]:
                averageValue = averageValue + review.starRating
                if review.starRating <= 1:
                    star1 = star1 + 1
                elif review.starRating > 1 and review.starRating <= 2:
                    star2 = star2 + 1
                elif review.starRating > 2 and review.starRating <= 3:
                    star3 = star3 + 1
                elif review.starRating > 3 and review.starRating <= 4:
                    star4 = star4 + 1
                elif review.starRating > 4 and review.starRating <= 5:
                    star5 = star5 + 1

        if averageValue > 0:
            averageValue = averageValue / numberOfReviews
            star1 = (star1 / numberOfReviews) * 100
            star2 = (star2 / numberOfReviews) * 100
            star3 = (star3 / numberOfReviews) * 100
            star4 = (star4 / numberOfReviews) * 100
            star5 = (star5 / numberOfReviews) * 100

        RatingReviews = [round(averageValue, 2), numberOfReviews, star1, star2, star3, star4,
                         star5]

    elif searchMethod == "Exam" or searchMethod == "EndSearch":
        numberOfReviews = 0
        averageValue = 0
        star1 = 0.0
        star2 = 0.0
        star3 = 0.0
        star4 = 0.0
        star5 = 0.0
        for result in resultList:
            numberOfReviews = numberOfReviews + len(dictReviews[result.exam])
            for review in dictReviews[result.exam]:
                averageValue = averageValue + review.starRating
                if review.starRating <= 1:
                    star1 = star1 + 1
                elif review.starRating > 1 and review.starRating <= 2:
                    star2 = star2 + 1
                elif review.starRating > 2 and review.starRating <= 3:
                    star3 = star3 + 1
                elif review.starRating > 3 and review.starRating <= 4:
                    star4 = star4 + 1
                elif review.starRating > 4 and review.starRating <= 5:
                    star5 = star5 + 1

        if averageValue > 0:
            averageValue = averageValue / numberOfReviews
            star1 = (star1 / numberOfReviews) * 100
            star2 = (star2 / numberOfReviews) * 100
            star3 = (star3 / numberOfReviews) * 100
            star4 = (star4 / numberOfReviews) * 100
            star5 = (star5 / numberOfReviews) * 100

        RatingReviews = [round(averageValue, 2), numberOfReviews, star1, star2, star3, star4,
                         star5]

    elif searchMethod == "EndSearchUniversity":
        numberOfReviews = len(dictReviews[university])
        averageValue = 0
        star1 = 0.0
        star2 = 0.0
        star3 = 0.0
        star4 = 0.0
        star5 = 0.0
        for review in dictReviews[university]:
            averageValue = averageValue + review.starRating
            if review.starRating <= 1:
                star1 = star1 + 1
            elif review.starRating > 1 and review.starRating <= 2:
                star2 = star2 + 1
            elif review.starRating > 2 and review.starRating <= 3:
                star3 = star3 + 1
            elif review.starRating > 3 and review.starRating <= 4:
                star4 = star4 + 1
            elif review.starRating > 4 and review.starRating <= 5:
                star5 = star5 + 1

        if averageValue > 0:
            averageValue = averageValue / numberOfReviews
            star1 = (star1 / numberOfReviews) * 100
            star2 = (star2 / numberOfReviews) * 100
            star3 = (star3 / numberOfReviews) * 100
            star4 = (star4 / numberOfReviews) * 100
            star5 = (star5 / numberOfReviews) * 100

        RatingReviews = [round(averageValue, 2), numberOfReviews, star1, star2, star3, star4,
                         star5]

    elif searchMethod == "EndSearchProgram":
        numberOfReviews = len(dictReviews[program])
        averageValue = 0
        star1 = 0.0
        star2 = 0.0
        star3 = 0.0
        star4 = 0.0
        star5 = 0.0
        for review in dictReviews[program]:
            averageValue = averageValue + review.starRating
            if review.starRating <= 1:
                star1 = star1 + 1
            elif review.starRating > 1 and review.starRating <= 2:
                star2 = star2 + 1
            elif review.starRating > 2 and review.starRating <= 3:
                star3 = star3 + 1
            elif review.starRating > 3 and review.starRating <= 4:
                star4 = star4 + 1
            elif review.starRating > 4 and review.starRating <= 5:
                star5 = star5 + 1

        if averageValue > 0:
            averageValue = averageValue / numberOfReviews
            star1 = (star1 / numberOfReviews) * 100
            star2 = (star2 / numberOfReviews) * 100
            star3 = (star3 / numberOfReviews) * 100
            star4 = (star4 / numberOfReviews) * 100
            star5 = (star5 / numberOfReviews) * 100

        RatingReviews = [round(averageValue, 2), numberOfReviews, star1, star2, star3, star4,
                         star5]

    return render_template('resultPage.html', resultList=resultList, searchForm=searchForm, city=city,
                           academicDegree=academicDegree, university=university, program=program, exam=exam,
                           searchMethod=searchMethod, dictReviews=dictReviews, university_object=university_object,
                           numberOfReviews=numberOfReviews, RatingReviews=RatingReviews)


@app.route('/resultPage/<searchMethod>/<city>/<academicDegree>/<university>/<program>/<exam>', methods=['POST', 'GET'])
def resultPage(searchMethod, city, academicDegree, university, program, exam):
    '''Search Function'''
    searchForm = searchFunction()

    if searchForm.validate_on_submit():
        return searchValidator(searchForm)

    return resultValidator(searchForm, searchMethod, city, academicDegree, university, program, exam)


@app.route('/universities', methods=['POST', 'GET'])
def universities():
    university = University.query.order_by(University.name).all()

    '''Search Function'''
    searchForm = searchFunction()

    if searchForm.validate_on_submit():
        return searchValidator(searchForm)

    return render_template('infoPage.html', university=university, searchForm=searchForm, element="university")


@app.route('/programs', methods=['POST', 'GET'])
def programs():
    program = Program.query.group_by(Program.courseName).all()

    '''Search Function'''
    searchForm = searchFunction()

    if searchForm.validate_on_submit():
        return searchValidator(searchForm)

    return render_template('infoPage.html', program=program, searchForm=searchForm, element="program")


@app.route('/exams', methods=['POST', 'GET'])
def exams():
    exam = Exam.query.group_by(Exam.exam).all()

    '''Search Function'''
    searchForm = searchFunction()

    if searchForm.validate_on_submit():
        return searchValidator(searchForm)

    return render_template('infoPage.html', exam=exam, searchForm=searchForm, element="exam")


def editProfileFunction():
    editProfileForm = formEditProfile()

    '''get all cities in the db & add them to the editProfileForm'''
    cities = Program.query.order_by(Program.sedeP)
    myCities = []
    for x in cities:
        myCities.append(x.sedeP)

    myCities = list(dict.fromkeys(myCities))
    myCities.sort()
    editProfileForm.city.choices = myCities

    return editProfileForm


def editProfileValidator(editProfileForm, dbUser):

    # This code validates the changes made by the user to the profile. The basic information of the users are already included in the db during the registration phase.
    # However the user might want to change some of them, change the email or simply add more information for a better description of his/her profile.

    # The first part of the code checks what are the choices made by the user in the form
    # The placeholder of the forms already shows what are the data present in the db on the user information
    # The user can decided either to modify them, not modify them of simply overwrite partially some information.
    # For this reason the following code checks whether the user wants to change the information in the db or not.
    # In case he wants to change it, those are overwritten by updating the db through a query statement. In case he doesn't want to change them, the query is updating the information with the information already present in the db.

    conn = db_connector.create_connection()

    id = int(session['user_id'])
    email = editProfileForm.email.data
    firstName = editProfileForm.firstName.data
    lastName = editProfileForm.lastName.data
    highestDegreeObtained = editProfileForm.highestDegreeObtained.data
    if highestDegreeObtained == "": highestDegreeObtained = dbUser.highestDegreeObtained
    currentInstitution = editProfileForm.currentInstitution.data
    if currentInstitution == "": currentInstitution = dbUser.currentInstitution
    selectedCity = editProfileForm.city.data
    stateRegion = editProfileForm.stateRegion.data
    if stateRegion == "": stateRegion = dbUser.stateRegion
    country = editProfileForm.country.data
    if country == "": country = dbUser.country

    cursor = conn.cursor()
    # cursor.execute("""UPDATE user SET firstName='""" + firstName + """', lastName='""" + lastName + """',  highestDegreeObtained= '""" + highestDegreeObtained + """', currentInstitution = '""" + currentInstitution + """', city='""" + selectedCity + """', stateRegion='""" + stateRegion + """', country='""" + country + """' WHERE id='""" + id + """'""")
    cursor.execute(
        'UPDATE user SET firstName = ?, lastName = ?, email = ?, highestDegreeObtained = ?, currentInstitution = ?, city= ?, stateRegion = ?, country = ? WHERE id = ? ',
        (firstName, lastName, email, highestDegreeObtained, currentInstitution, selectedCity, stateRegion, country, id))
    conn.commit()
    conn.close()

    flash('Profile Successfully updated', 'success')

    return redirect(url_for('editProfile'))


def deleteReviewFunction(listReviews):

    # This function lists all the reviews that are written by the current user and populates a drop down menu from which the user can choose what to delete.

    deleteReviewForm = formDeleteReview()

    myReviews = []

    for x in listReviews:
        myReviews.append(x.idReview)

    deleteReviewForm.reviews.choices = myReviews

    return deleteReviewForm


def deleteReviewValidator(deleteReviewForm):

    # This function implements the query to delete from the DB a specific review made by the user.

    conn = db_connector.create_connection()

    idReview = int(deleteReviewForm.reviews.data)

    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM review WHERE idReview = ? ', (idReview,))
    conn.commit()
    conn.close()

    return redirect(url_for('editProfile'))


@app.route('/editProfile', methods=['POST', 'GET'])
def editProfile():
    if 'logged_in' not in session or session['logged_in'] == False:
        return redirect(url_for('login'))

    '''Search Function'''
    searchForm = searchFunction()

    if searchForm.validate_on_submit():
        return searchValidator(searchForm)

    conn = db_connector.create_connection()
    dbUser = User.query.filter(User.id == session['user_id']).first()
    conn.close()

    '''edit Profile Function'''
    editProfileForm = editProfileFunction()

    '''fetching reviews'''
    listReviews = Review.query.filter_by(idUser=session['user_id']).order_by(Review.starRating.desc()).all()

    if editProfileForm.validate_on_submit():
        return editProfileValidator(editProfileForm, dbUser)

    deleteReviewForm = deleteReviewFunction(listReviews)

    if deleteReviewForm.validate_on_submit():
        return deleteReviewValidator(deleteReviewForm)

    return render_template('editProfile.html', searchForm=searchForm, editProfileForm=editProfileForm,
                           listReviews=listReviews, dbUser=dbUser, deleteReviewForm=deleteReviewForm)


def reviewValidator(reviewForm, city, academicDegree, university, program, exam, searchMethod):

    # This function is validating the review submited by the user.

    conn = db_connector.create_connection()
    cursor = conn.cursor()
    query2 = " SELECT idReview from Review where idReview IN (SELECT max(idReview) FROM Review) "
    cursor.execute(query2)
    record = cursor.fetchone()

    university_object = "null"
    idProgram = "null"
    idExam = "null"

    university_orig = university
    program_orig = program
    city_orig = city

    # this is needed to show data about the object currently rendered and to fetch again ids of program and exam

    if (university != "null"):
        university_object = University.query.filter_by(idUniversity=university).all()

    if (program != "null"):
        # id program
        if (city == "All"):
            program_list = Program.query. \
                filter(and_(Program.academicDegree.ilike(academicDegree), Program.courseName.ilike(program),
                            Program.idUniversity.ilike(university))).group_by(Program.courseName).all()
            program_object = program_list[0]
            idProgram = program_object.idProgram
            city = Program.query.filter_by(idProgram=idProgram).all()[0].sedeC
        else:
            idProgram = Program.query. \
                filter(and_(Program.sedeP.ilike(city), Program.academicDegree.ilike(academicDegree),
                            Program.courseName.ilike(program),
                            Program.idUniversity.ilike(university))).group_by(Program.courseName).all()[0].idProgram

    if (exam != "null"):
        # id program and idexam
        idExam = Exam.query.filter(and_(Exam.idProgram.ilike(idProgram), Exam.exam.ilike(exam))).all()[0].idExam

    idReview = int(record[0]) + 1
    idUser = session['user_id']
    sedeC = city
    reviewTitle = reviewForm.ReviewTitle.data
    review = reviewForm.Review.data
    timeStamp = datetime.datetime.now()

    starRating = reviewForm.starRating.data

    newReview = Review(idReview=idReview,
                       idUser=idUser,
                       sedeC=sedeC,
                       idUniversity=university,
                       idProgram=idProgram,
                       idExam=idExam,
                       reviewTitle=reviewTitle,
                       review=review,
                       timeStamp=timeStamp,
                       starRating=starRating)

    db.session.add(newReview)
    db.session.commit()
    conn.close()
    return redirect(url_for('resultPage', searchMethod=searchMethod,
                            city=city_orig, academicDegree=academicDegree, university=university_orig,
                            program=program_orig, exam=exam))


@app.route('/leaveReview/<city>/<academicDegree>/<university>/<program>/<exam>/<searchMethod>', methods=['POST', 'GET'])
def leaveReview(city, academicDegree, university, program, exam, searchMethod):
    '''Search Function'''
    searchForm = searchFunction()

    university_object = "null"

    if (university != "null"):
        university_object = University.query.filter_by(idUniversity=university).all()

    if searchForm.validate_on_submit():
        return searchValidator(searchForm)

    '''review Function'''
    reviewForm = formReview()

    if reviewForm.validate_on_submit():
        return reviewValidator(reviewForm, city, academicDegree, university, program, exam, searchMethod)

    return render_template('leaveReview.html', reviewForm=reviewForm, searchForm=searchForm, city=city,
                           academicDegree=academicDegree, university=university, program=program, exam=exam,
                           searchMethod=searchMethod, university_object=university_object)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.before_first_request
def setup():
    conn = db_connector.create_connection()

    # add here all the tables to be dropped during the setup
    tables_db = ['permissions']
    db_connector.dropTables(conn, tables_db)

    # create all the tables in the db (classes in model)
    db.create_all()

    # method 1 adding 1 item in the table
    cursor = conn.cursor()
    query1 = "INSERT INTO permissions VALUES (1,'High School Student')"
    cursor.execute(query1)
    conn.commit()
    conn.close()

    # method 2 adding 1 item in the table
    permission_bachelor = Permissions(name='Bachelor Student')
    permission_master = Permissions(name='Master Student')
    permission_graduated = Permissions(name='Graduated')

    db.session.add_all([permission_bachelor, permission_master,
                        permission_graduated])
    db.session.commit()


@app.route('/registration', methods=['POST', 'GET'])
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

        # ENCODE PASSWORD BEFORE ADDING IT
        password_1 = bcrypt.generate_password_hash(registerForm.password.data).encode('utf-8')

        # creation of the USER
        newUser = User(email=email, firstName=firstName, lastName=lastName, password=password_1,
                       permissions_id=permission)

        # save everything in the db
        db.session.add(newUser)
        db.session.commit()

        # send mail
        sendmail(registerForm.email.data,
                 'You have registered successfully',
                 'mail',
                 firstName=registerForm.firstName.data,
                 email=registerForm.email.data,
                 password=registerForm.password.data)

        return redirect(url_for('login'))
    return render_template('registration.html', registerForm=registerForm)


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


def sendmail(to, subject, template, **kwargs):
    msg = Message(subject,
                  recipients=[to],
                  sender=app.config['MAIL_USERNAME'])

    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


if __name__ == '__main__':
    app.run()