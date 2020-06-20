from . import author
from flask import render_template, session, redirect, url_for, request, current_app
from ..models import Author
from .forms import AuthorForm
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash

#
# AddAuthor
#   Will add an author
#
@author.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Add a category for worksheets
    """
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    form = AuthorForm()

    if form.validate_on_submit():
        try:
            new_author = Author(name=form.name.data, email=form.email.data, about=form.about.data)
            db.session.add(new_author)
            db.session.commit()
            return redirect(url_for('other.home'))

        except:
            db.session.rollback()
            raise



    return render_template('add_author.html', form=form)


#
# DeleteAuthor
#   Will delete an author
#
@author.route('/delete_author/<int:id>', methods=['GET', 'POST'])
def delete_author(id):
    """
    Delete a post from the database
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    try :
        author = Author.query.get(id)
        db.session.delete(author)
        db.session.commit()

        # redirect to the home page
        return redirect(url_for('other.home'))
    except :
        db.session.rollback()
        raise

#
# EditAuthor
#   Will edit an author
#
@author.route('/edit_author/<int:id>', methods=['GET', 'POST'])
def edit_author(id) :
    """
    Edit an Author
    """

    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    author = Author.query.get(id)
    form = AuthorForm(obj=author)

    if form.validate_on_submit():
        try :
            author.name = form.name.data
            author.email = form.email.data
            author.about = form.about.data

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('other.home'))
        except :
            db.session.rollback()
            raise

    form.name.data = author.name
    form.name.data = author.email
    form.about.data = author.about

    return render_template('edit_author.html', form=form, author=author, title="Edit Author")
