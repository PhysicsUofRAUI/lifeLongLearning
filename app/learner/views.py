from . import learner
from flask import render_template, session, redirect, url_for, request, current_app, flash
from ..models import Learner
from .forms import LearnerForm, LearnerLoginForm
from .. import db
from werkzeug.security import check_password_hash, generate_password_hash

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

                return redirect(url_for('learner.learner_dashboard', id=author.id))
            elif not check_password_hash(learner.password, form.password.data) :
                flash("password was incorrect")
                return redirect(request.url)
        except :
            db.session.rollback()

    # load login template
    return render_template('learner_login.html', form=form, title='Learner Login')


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
    return render_template('learner_change_password.html', form=form, learner=learner, title="Change Password")



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
# Learner Dashboard
# Purpose: A place for an learner to see all the different options with their account
#
@learner.route('/learner_dashboard/<int:id>', methods=['GET', 'POST'])
@learner.route('/learner_dashboard', defaults={'id': 0}, methods=['GET', 'POST'])
def learner_dashboard(id):
    if not session.get('learner_logged_in') :
        return redirect(url_for('other.home'))

    return render_template('learner_dashboard.html', id=id, favourites=None)
