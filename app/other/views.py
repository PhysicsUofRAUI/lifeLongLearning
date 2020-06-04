from flask import render_template, current_app
from . import other
from .. import db
from ..models import Author, WorksheetCategory, PostCategory

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
    authors = Author.query.all()

    return render_template("contact.html", authors=authors)


#
# Admin:
#   renders a page to list all the not easily found webpages for admin functions
#
@other.route('/admin')
def admin() :
    worksheet_categories = WorksheetCategory.query.all()

    post_categories = PostCategory.query.all()

    return render_template("admin.html", worksheet_categories=worksheet_categories, post_categories=post_categories)
