from . import worksheets
from flask import render_template, session, redirect, url_for, request, current_app
from ..models import WorksheetCategory, Worksheet, Author
from .forms import WorksheetForm, AuthorForm, WorksheetCategoryForm, EditWorksheetForm
from werkzeug.utils import secure_filename
import os
from .. import db

#
# Worksheets
#   will display the worksheets
#
# Note: will have to make a call to the database for each author so that the
#   template can distinguish
#
@worksheets.route('/worksheets_page/<int:worksheet>/<int:page>', defaults={'category': None, 'author': None}, methods=['GET', 'POST'])
@worksheets.route('/worksheets_page/<int:category>/<int:page>', defaults={'worksheet': None, 'author': None}, methods=['GET', 'POST'])
@worksheets.route('/worksheets_page/<int:author>/<int:page>', defaults={'worksheet': None, 'category': None}, methods=['GET', 'POST'])
@worksheets.route('/worksheets_page/<int:page>', defaults={'category': None, 'worksheet': None, 'author': None}, methods=['GET', 'POST'])
@worksheets.route('/worksheets_page', defaults={'category': None, 'worksheet': None, 'page': 0, 'author': None}, methods=['GET', 'POST'])
def worksheets_page(page, category, author, worksheet) :
    # The pagination may cause an error with the None trying to be an int
    #
    categories = WorksheetCategory.query.all()

    if not worksheet == None :
        # if a specific post has been selected this if statement will be ran
        worksheets = Worksheet.query.get(worksheet)

        return render_template('worksheets.html', worksheets=worksheets, categories=categories, next_url=None, prev_url=None)

    elif not author == None :
        # get the worksheets done by a specific author
        worksheets = Worksheet.query.filter_by(author_id=author).order_by(Worksheet.id.desc()).offset(page * 5).limit(5).all()

        more = Worksheet.query.filter_by(author_id=author).offset((page + 1) * 5).first()

        if page != 0 :
            prev_url = url_for('worksheets.worksheets_page', author=author, category=category, page=page - 1)
        else :
            prev_url = None

        if not more == None :
            next_url = url_for('worksheets.worksheets_page', author=author, category=category, page=page + 1)
        else :
            next_url = None

        return render_template('worksheets.html', worksheets=worksheets, categories=categories, next_url=next_url, prev_url=prev_url)

    elif not category == None:
        # get the worksheets from a specific category
        worksheets = Worksheet.query.filter_by(category_id=category).order_by(Worksheet.id.desc()).offset(page * 5).limit(5).all()

        more = Worksheet.query.filter_by(category_id=category).offset((page + 1) * 5).first()

        if page != 0 :
            prev_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page - 1)
        else :
            prev_url = None

        if not more == None :
            next_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page + 1)
        else :
            next_url = None

        return render_template('worksheets.html', worksheets=worksheets, categories=categories, next_url=next_url, prev_url=prev_url)

    else :
        # get all the worksheets
        # if a no specific photo or category has been selected this if statement will be ran
        worksheets = Worksheet.query.order_by(Worksheet.id.desc()).offset(page * 5).limit(5).all()

        more = Worksheet.query.offset((page + 1) * 5).first()

        if page != 0 :
            prev_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page - 1)
        else :
            prev_url = None

        if not more == None :
            next_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page + 1)
        else :
            next_url = None

        return render_template('worksheets.html', worksheets=worksheets, categories=categories, next_url=next_url, prev_url=prev_url)

#
# AddWorksheet
#   will handle the adding of worksheets
#   need to look up how file uploads are done
#
@worksheets.route('/add_worksheet', methods=['GET', 'POST'])
def add_worksheet():
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    # Cannot pass in 'request.form' to WorksheetForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause WorksheetForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    form = WorksheetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            file = request.files['worksheet_pdf']
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            new_worksheet = Worksheet(name=form.title.data, video_url=form.video_url.data,
                pdf_url=filename, category_id=form.category.data.id, category=form.category.data,
                author_id=form.author.data.id, author=form.author.data)

            db.session.add(new_worksheet)
            db.session.commit()

            return redirect(url_for('other.home'))
        else:
            return redirect(url_for('other.home'))

    return render_template('add_worksheet.html', form=form)

#
# EditWorksheet
#   will allow the user to edit an existing worksheet that is in the database
#
#   This function does not allow for the editing of the pdf
#
# @worksheets.route('/edit_worksheet/<int:id>', methods=['GET', 'POST'])
# def edit_worksheet(id):
#     # check if user is logged in
#     if not session.get('logged_in'):
#         return redirect(url_for('other.home'))
#
#     worksheet = Worksheet.query.get(id)
#     form = EditWorksheetForm(obj=worksheet)
#
#     if form.validate_on_submit():
#         # delete the current pdf of the worksheet
#         # add the new worksheet like how it is done in add worksheet
#         worksheet.name = form.title.data
#         worksheet.video_url = form.video_url.data
#         worksheet.category_id = form.category.data.id
#         worksheet.category = form.category.data
#         worksheet.category_id = form.author.data.id
#         worksheet.category = form.author.data
#
#         db.session.commit()
#
#         # redirect to the home page
#         return redirect(url_for('other.home'))
#
#     form.title.data = worksheet.name
#     form.video_url.data = worksheet.video_url
#     form.author.data = worksheet.author
#     form.category.data = worksheet.category
#
#     return render_template('edit_worksheet.html', form=form, worksheet=worksheet, title="Edit Worksheet Category")



#
# DeleteWorksheet
#   will delete a specified worksheet
#
@worksheets.route('/delete_worksheet/<int:id>', methods=['GET', 'POST'])
def delete_worksheet(id):
    """
    Delete a post from the database
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    worksheet = Worksheet.query.get(id)

    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], worksheet.pdf_url))

    db.session.delete(worksheet)
    db.session.commit()

    # redirect to the home page
    return redirect(url_for('other.home'))

#
# AddWorksheetCategory
#   will handle the adding of a worksheet category
#
@worksheets.route('/add_worksheet_category', methods=['GET', 'POST'])
def add_worksheet_category():
    """
    Add a category for worksheets
    """
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    form = WorksheetCategoryForm()

    if form.validate_on_submit():
        new_category = WorksheetCategory(name=form.name.data)

        try:
            db.session.add(new_category)
            db.session.commit()
        except:
            return redirect(url_for('other.home'))

        return redirect(url_for('other.home'))

    return render_template('add_worksheet_category.html', form=form)

#
# EditWorksheetCategory
#   will handle the editing of worksheet Categories
#
@worksheets.route('/edit_worksheet_category/<int:id>', methods=['GET', 'POST'])
def edit_worksheet_category(id) :
    """
    Edit a blog category
    """

    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    category = WorksheetCategory.query.get(id)
    form = WorksheetCategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data

        db.session.commit()

        # redirect to the home page
        return redirect(url_for('other.home'))

    form.name.data = category.name

    return render_template('edit_worksheet_category.html', form=form, category=category, title="Edit Worksheet Category")

#
# DeleteWorksheetCategory
#   will delete a worksheet category
#
@worksheets.route('/delete_worksheet_category/<int:id>', methods=['GET', 'POST'])
def delete_worksheet_category(id):
    """
    Delete a post from the database
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    category = WorksheetCategory.query.get(id)
    db.session.delete(category)
    db.session.commit()


    # redirect to the home page
    return redirect(url_for('other.home'))

#
# AddAuthor
#   Will add an author
#
@worksheets.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Add a category for worksheets
    """
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    form = AuthorForm()

    if form.validate_on_submit():
        new_author = Author(name=form.name.data, email=form.email.data, about=form.about.data)

        try:
            db.session.add(new_author)
            db.session.commit()

        except:
            return redirect(url_for('other.home'))

        return redirect(url_for('other.home'))

    return render_template('add_author.html', form=form)

#
# DeleteAuthor
#   Will delete an author
#
@worksheets.route('/delete_author/<int:id>', methods=['GET', 'POST'])
def delete_author(id):
    """
    Delete a post from the database
    """
    # check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    author = Author.query.get(id)
    db.session.delete(author)
    db.session.commit()

    # redirect to the home page
    return redirect(url_for('other.home'))

#
# EditAuthor
#   Will edit an author
#
@worksheets.route('/edit_author/<int:id>', methods=['GET', 'POST'])
def edit_author(id) :
    """
    Edit an Author
    """

    if not session.get('logged_in'):
        return redirect(url_for('other.home'))

    author = Author.query.get(id)
    form = AuthorForm(obj=author)

    if form.validate_on_submit():
        author.name = form.name.data
        author.email = form.email.data
        author.about = form.about.data

        db.session.commit()

        # redirect to the home page
        return redirect(url_for('other.home'))

    form.name.data = author.name
    form.name.data = author.email
    form.about.data = author.about

    return render_template('edit_author.html', form=form, author=author, title="Edit Author")
