from flask import render_template, current_app, session, redirect, url_for
from . import other
from .. import db
from ..models import Author, PostCategory, WorksheetCategory, Learner

#
# Home
# Purpose:
#     will display the home page of the website both '/' and '/home' are used
#     so that this is the first page shown and the page that is shown when home is
#     requested
#
# Method:
#     render the home page template
#
@other.route('/')
@other.route('/home')
def home():
    return render_template("home.html", title='Home')

#
# Contact/About
#   will present the Contact/About page
#
@other.route('/contact')
def contact():
    try :
        authors = Author.query.all()
    except:
        db.session.rollback()
        return redirect(url_for('other.home'))

    return render_template("contact.html", authors=authors)

@other.route('/admin', methods=['GET', 'POST'])
def admin() :
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    try :
        learners = Learner.query.all()

        worksheetCategories = WorksheetCategory.query.all()

        postCategories = PostCategory.query.all()
    except:
        db.session.rollback()
        return redirect(url_for('other.home'))

    return render_template('admin.html', worksheet_categories=worksheetCategories, post_categories=postCategories, learners=learners)

@other.route('/building')
def building():
    return render_template("building.html")
