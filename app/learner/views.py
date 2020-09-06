from . import learner
from flask import render_template, session, redirect, url_for, request, current_app, flash
from ..models import Learner, Worksheet
from .forms import LearnerForm, LearnerLoginForm
from .. import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
import random
import string
from .. import mail

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

#
# Learner Login
# Purpose: to allow learner to login with their permissions.
#   Will set a session variable called 'learner_logged_in' to true.
#
@learner.route('/learner_login', methods=['GET', 'POST'])
def learner_login():
    form = LearnerLoginForm()
    if form.validate_on_submit():
        try :
            learner = Learner.query.filter_by(email=form.email.data).first()
            if learner == None :
                flash("Email does not exist")

                return redirect(request.url)
            elif check_password_hash(learner.password, form.password.data):
                session['learner_logged_in'] = True
                session['learner_name'] = learner.name

                return redirect(url_for('learner.learner_dashboard', id=learner.id))
            elif not check_password_hash(learner.password, form.password.data) :
                flash("password was incorrect")
                return redirect(request.url)
        except :
            db.session.rollback()

    # load login template
    return render_template('learner_login.html.j2', form=form, title='Learner Login')

#
# Learner Logout
# Purpose: To unset a the 'learner_logged_in'
#
@learner.route('/learner_logout')
def learner_logout():
    if session.get('learner_logged_in'):
        session['learner_logged_in'] = False
        session['learner_name'] = None

    # redirect to the login page
    return redirect(url_for('other.home'))


#
# Password Reset
#   Will request the email of the learner and then on submit will change
#   the password associated with that account to a knew password and email it
#   to the learner.
# Look here for advice: https://pythonhosted.org/Flask-Mail/
# These are also useful: https://pythonbasics.org/flask-mail/
#                        https://www.hesk.com/knowledgebase/?article=72
#
@learner.route('/learner_password_reset', methods=['GET', 'POST'])
def learner_password_reset() :
    form = LearnerForm()

    if form.validate_on_submit():
        learner = Learner.query.filter_by(email=form.email.data).first()

        if not learner == None :
            temp_pass = get_random_string(8)
            try :
                learner.password = generate_password_hash(temp_pass)

                db.session.commit()

                msg = Message("Temporary Password", sender = 'kodyrogers21@gmail.com', recipients = [learner.email])
                msg.body = "Your temporary password is '" + temp_pass + "'. It is highly recommended that you change it right away."
                mail.send(msg)

                return redirect(url_for('learner.learner_login'))
            except :
                db.session.rollback()
                msg = Message("Password Reset Failed", sender = 'kodyrogers21@gmail.com', recipients = [learner.email])
                msg.body = "Something went wrong on our side and you password was not reset. Please try again or contact admin at kodyroger21@gmail.com."
                mail.send(msg)

                raise
        else :
            return render_template('learner_password_reset.html.j2', form=form)

    return render_template('learner_password_reset.html.j2', form=form)
#
# Edit Learner
#   Will edit an author
#
@learner.route('/edit_learner/<int:id>', methods=['GET', 'POST'])
def edit_learner(id) :
    """
    Edit an Author
    """

    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    try :
        learner = Learner.query.get(id)
    except :
        db.session.rollback()
        raise

    form = LearnerForm(obj=learner)

    if form.validate_on_submit():
        try :
            learner.password = generate_password_hash(form.password.data)

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('other.home'))
        except :
            db.session.rollback()
            raise

    return render_template('edit_learner.html.j2', form=form, learner=learner, title="Edit Learner")

#
# delete_learner
#   Will delete an author
#
@learner.route('/delete_learner/<int:id>', methods=['GET', 'POST'])
def delete_learner(id):
    """
    Delete a post from the database
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    try :
        learner = Learner.query.get(id)
        db.session.delete(learner)
        db.session.commit()

        # redirect to the home page
        return redirect(url_for('other.home'))
    except :
        db.session.rollback()
        raise


#
# Learner Change Password
# Purpose: To give a learner an easy way to change their password.
#
@learner.route('/learner_change_password/<int:id>', methods=['GET', 'POST'])
def learner_change_password(id):
    if not session.get('learner_logged_in') :
        return redirect(url_for('other.home'))

    try :
        learner = Learner.query.get(id)
    except :
        db.session.rollback()
        raise

    if not learner.name == session.get('learner_name') :
        return redirect(url_for('other.home'))

    form = LearnerForm(obj=learner)

    if form.validate_on_submit():
        try :
            learner.password = generate_password_hash(form.password.data)

            db.session.commit()

            # redirect to the author dashboard
            return redirect(url_for('learner.learner_dashboard', id=learner.id))
        except :
            db.session.rollback()
            raise
    return render_template('learner_change_password.html.j2', form=form, learner=learner, title="Change Password")

#
# Learner Change Email
# Purpose: To give an learner an easy way to change their email.
#
@learner.route('/learner_change_email/<int:id>', methods=['GET', 'POST'])
def learner_change_email(id):
    if not session.get('learner_logged_in') :
        return redirect(url_for('other.home'))

    try :
        learner = Learner.query.get(id)
    except :
        db.session.rollback()
        raise

    if not learner.name == session.get('learner_name') :
        return redirect(url_for('other.home'))

    form = LearnerForm(obj=learner)

    if form.validate_on_submit():
        try :
            learner.email = form.email.data

            db.session.commit()

            # redirect to the author dashboard
            return redirect(url_for('learner.learner_dashboard', id=learner.id))
        except :
            db.session.rollback()
            raise

    form.email.data = learner.email

    return render_template('learner_change_email.html.j2', form=form, learner=learner, title="Change Email")


#
# Learner Change Screenname
# Purpose: To give an learner an easy way to change their screenname.
#
@learner.route('/learner_change_screenname/<int:id>', methods=['GET', 'POST'])
def learner_change_screenname(id):
    if not session.get('learner_logged_in') :
        return redirect(url_for('other.home'))

    try :
        learner = Learner.query.get(id)
    except :
        db.session.rollback()
        raise

    if not learner.name == session.get('learner_name') :
        return redirect(url_for('other.home'))

    form = LearnerForm(obj=learner)

    if form.validate_on_submit():
        try :
            learner.screenname = form.screenname.data

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('learner.learner_dashboard', id=learner.id))
        except :
            db.session.rollback()
            raise

    form.screenname.data = learner.screenname

    return render_template('learner_change_screenname.html.j2', form=form, learner=learner, title="Change Screenname")


#
# Learner Favourites
# Purpose: A place for an learner to see all the different options with their account
# should have remove from favourites
#
@learner.route('/add_favourite/<int:learner_id>/<int:worksheet_id>', methods=['GET', 'POST'])
def add_favourite(learner_id, worksheet_id):
    if not session.get('learner_logged_in') :
        return redirect(url_for('other.home'))

    try :
        learner = Learner.query.get(learner_id)
    except :
        db.session.rollback()
        raise

    if not learner.name == session.get('learner_name') :
        return redirect(url_for('other.home'))

    try :
        worksheet = Worksheet.query.get(worksheet_id)

        learner.favourites.append(worksheet)

        db.session.commit()
    except :
        db.session.rollback()
        raise

    return redirect(url_for('worksheets.worksheets_page', author=worksheet.author_id, category=None, page=0))



#
# Learner Dashboard
# Purpose: A place for an learner to see all the different options with their account
#
@learner.route('/learner_dashboard/<int:id>', methods=['GET', 'POST'])
@learner.route('/learner_dashboard', defaults={'id': 0}, methods=['GET', 'POST'])
def learner_dashboard(id):
    if not session.get('learner_logged_in') :
        return redirect(url_for('other.home'))

    try :
        learner = Learner.query.filter_by(name=session.get('learner_name')).first()
    except :
        db.session.rollback()
        raise

    favourites = learner.favourites

    return render_template('learner_dashboard.html.j2', id=learner.id, favourites=favourites)


#
# Learner Login Signup Choice Page
# Purpose: A page allowing a learner to either signup or login
#
@learner.route('/learner_signup_login_choice', methods=['GET', 'POST'])
def learner_signup_login_choice():
    return render_template('learner_signup_login_choice.html.j2')

#
# Learner Signup
# Purpose: A page for learners to sign themselves up
#
@learner.route('/learner_signup', methods=['GET', 'POST'])
def learner_signup():
    form = LearnerForm()

    if form.validate_on_submit():
        try:
            new_learner = Learner(name=form.name.data, email=form.email.data,
                            screenname=form.screenname.data, password=generate_password_hash(form.password.data))
            db.session.add(new_learner)
            db.session.commit()
            return redirect(url_for('learner.learner_login'))

        except:
            db.session.rollback()
            raise

    return render_template('learner_signup.html.j2', form=form)
