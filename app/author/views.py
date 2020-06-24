from . import author
from flask import render_template, session, redirect, url_for, request, current_app, flash
from ..models import Author
from .forms import AuthorForm, AuthorLoginForm
from .. import db
from werkzeug.security import check_password_hash, generate_password_hash

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
            new_author = Author(name=form.name.data, email=form.email.data, password=generate_password_hash(form.password.data))
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
            author.password = generate_password_hash(form.password.data)

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


#
# Author Login
# Purpose: to allow authors to login with their permissions.
#   Will set a session variable called 'author_logged_in' to true.
#
@author.route('/author_login', methods=['GET', 'POST'])
def author_login():
    form = AuthorLoginForm()
    if form.validate_on_submit():
        author = Author.query.filter_by(name=form.username.data).first()
        if author == None :
            flash("Username does not exist")

            return redirect(request.url)
        elif check_password_hash(author.password, form.password.data):
            session['author_logged_in'] = True

            return redirect(url_for('other.home'))
        elif not check_password_hash(author.password, form.password.data) :
            flash("password was incorrect")
            return redirect(request.url)

    # load login template
    return render_template('author_login.html', form=form, title='Author Login')




#
# Author Logout
# Purpose: To unset a the 'author_logged_in'
#
@author.route('/author_logout')
def logout():
    if session.get('author_logged_in'):
        session['author_logged_in'] = False

    # redirect to the login page
    return redirect(url_for('other.home'))
