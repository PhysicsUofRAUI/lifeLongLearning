from . import author
from flask import render_template, session, redirect, url_for, request, current_app, flash
from ..models import Author, Worksheet
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
            session['author_name'] = author.name

            return redirect(url_for('author.author_dashboard', id=author.id))
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
        session['author_name'] = None

    # redirect to the login page
    return redirect(url_for('other.home'))


#
# Author Change Screenname
# Purpose: To give an author an easy way to change their screenname.
#
@author.route('/author_change_screenname/<int:id>', methods=['GET', 'POST'])
def author_change_screenname(id):
    if not session.get('author_logged_in') :
        return redirect(url_for('other.home'))

    author = Author.query.get(id)

    if not author.name == session.get('author_name') :
        return redirect(url_for('other.home'))

    form = AuthorForm(obj=author)

    if form.validate_on_submit():
        try :
            author.screenname = form.screenname.data

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('author.author_dashboard', id=author.id))
        except :
            db.session.rollback()
            raise

    form.screenname.data = author.screenname

    return render_template('author_change_screenname.html', form=form, author=author, title="Change Screenname")


#
# Author Change Email
# Purpose: To give an author an easy way to change their email.
#
@author.route('/author_change_email/<int:id>', methods=['GET', 'POST'])
def author_change_email(id):
    if not session.get('author_logged_in') :
        return redirect(url_for('other.home'))

    author = Author.query.get(id)

    if not author.name == session.get('author_name') :
        return redirect(url_for('other.home'))

    form = AuthorForm(obj=author)

    if form.validate_on_submit():
        try :
            author.email = form.email.data

            db.session.commit()

            # redirect to the author dashboard
            return redirect(url_for('author.author_dashboard', id=author.id))
        except :
            db.session.rollback()
            raise

    form.screenname.data = author.screenname

    return render_template('author_change_email.html', form=form, author=author, title="Change Email")



#
# Author Change Password
# Purpose: To give an author an easy way to change their password.
#
@author.route('/author_change_password/<int:id>', methods=['GET', 'POST'])
def author_change_password(id):
    if not session.get('author_logged_in') :
        return redirect(url_for('other.home'))

    author = Author.query.get(id)
    if not author.name == session.get('author_name') :
        return redirect(url_for('other.home'))

    form = AuthorForm(obj=author)

    if form.validate_on_submit():
        try :
            author.password = generate_password_hash(form.password.data)

            db.session.commit()

            # redirect to the author dashboard
            return redirect(url_for('author.author_dashboard', id=author.id))
        except :
            db.session.rollback()
            raise
    return render_template('author_change_password.html', form=form, author=author, title="Change Password")



#
# Author Dashboard
# Purpose: A place for an author to see all the different options with their account
#
@author.route('/author_dashboard/<int:id>', methods=['GET', 'POST'])
@author.route('/author_dashboard', defaults={'id': 0}, methods=['GET', 'POST'])
def author_dashboard(id):
    if not session.get('author_logged_in') :
        return redirect(url_for('other.home'))
    if not id == 0:
        author = Author.query.get(id)
    else :
        author = Author.query.filter_by(name=session.get('author_name')).first()

    if not author.name == session.get('author_name'):
        return redirect(url_for('other.home'))

    worksheets = Worksheet.query.filter_by(author_id=author.id).order_by(Worksheet.id.desc()).all()


    return render_template('author_dashboard.html', id=author.id, worksheets=worksheets)
