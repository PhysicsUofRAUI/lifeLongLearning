from flask import render_template, current_app
from . import other
from .. import db
from ..models import Author

#
# Home
# Purpose:
#     will display the home page of the website both '/' and '/home' are used
#     so that this is the first page shown and the page that is shown when home is
#     requested
#
# Method:
#     render the home page template
#     (next version may include a search for Photos to make it more dynamic)
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

    db.session.close()
    db.session.remove()
    db.session.rollback()

    return render_template("contact.html", authors=authors)
