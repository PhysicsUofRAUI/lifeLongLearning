from . import worksheets
from flask import render_template, session, redirect, url_for, request, current_app
from ..models import WorksheetCategory, Worksheet, Author, Learner
from .forms import WorksheetForm, WorksheetCategoryForm, EditWorksheetForm
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
@worksheets.route('/worksheets_page/<int:page>', methods=['GET', 'POST'])
@worksheets.route('/worksheets_page', defaults={'page': 0}, methods=['GET', 'POST'])
def worksheets_page(page) :
    try :
        categories = WorksheetCategory.query.all()
        author = request.args.get('author')
        category = request.args.get('category')
    except:
        db.session.rollback()
        raise

    if session.get('learner_logged_in') :
        try :
            learner = Learner.query.filter_by(name=session.get('learner_name')).first()
            favourites = learner.favourites
            learner_id = learner.id
        except :
            db.session.rollback()
            raise
    else :
        favourites = []
        learner_id = None

    if not author == None :
        try :
            # get the worksheets done by a specific author
            worksheets = Worksheet.query.filter_by(author_id=author).order_by(Worksheet.id.desc()).offset(page * 9).limit(9).all()

            more = Worksheet.query.filter_by(author_id=author).offset((page + 1) * 9).first()
        except:
            db.session.rollback()
            return redirect(url_for('other.home'))

        if page != 0 :
            prev_url = url_for('worksheets.worksheets_page', author=author, category=category, page=page - 1)
        else :
            prev_url = None

        if not more == None :
            next_url = url_for('worksheets.worksheets_page', author=author, category=category, page=page + 1)
        else :
            next_url = None

        return render_template('worksheets.html.j2', worksheets=worksheets, categories=categories, favourites=favourites, learner_id=learner_id, next_url=next_url, prev_url=prev_url)

    elif not category == None:
        try :
            # get the worksheets from a specific category
            worksheets = Worksheet.query.filter_by(category_id=category).order_by(Worksheet.id.desc()).offset(page * 9).limit(9).all()

            more = Worksheet.query.filter_by(category_id=category).offset((page + 1) * 9).first()
        except:
            db.session.rollback()
            raise

        if page != 0 :
            prev_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page - 1)
        else :
            prev_url = None

        if not more == None :
            next_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page + 1)
        else :
            next_url = None

        return render_template('worksheets.html.j2', worksheets=worksheets, categories=categories, favourites=favourites, learner_id=learner_id, next_url=next_url, prev_url=prev_url)
    else :
        try :
            # get all the worksheets
            # if a no specific worksheet or category has been selected this if statement will be ran
            worksheets = Worksheet.query.order_by(Worksheet.id.desc()).offset(page * 9).limit(9).all()

            more = Worksheet.query.offset((page + 1) * 9).first()
        except:
            db.session.rollback()
            raise

        if page != 0 :
            prev_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page - 1)
        else :
            prev_url = None

        if not more == None :
            next_url = url_for('worksheets.worksheets_page', category=category, author=author, page=page + 1)
        else :
            next_url = None

        return render_template('worksheets.html.j2', worksheets=worksheets, categories=categories, favourites=favourites, learner_id=learner_id, next_url=next_url, prev_url=prev_url)


#
# Specific Worksheet:
#   Displays a specified worksheet. It had to be added to make it easier to share
#   worksheets on Twitter.
#
@worksheets.route('/specific_worksheet/<int:id>', methods=['GET', 'POST'])
def specific_worksheet(id):
    try :
        worksheet = Worksheet.query.get(id)

        categories = WorksheetCategory.query.all()

        if not worksheet == None :
            return render_template('specific_worksheet.html.j2', worksheet=worksheet, categories=categories)
        else :
            return redirect(url_for('other.home'))
    except :
        db.session.rollback()
        raise

#
# Worksheet Count
#   Will increment the download count of a worksheet when one requests to view it.
#
@worksheets.route('/worksheets_count/<int:id>', methods=['GET', 'POST'])
def worksheets_count(id):
    try :
        worksheet = Worksheet.query.get(id)
        worksheet.count = worksheet.count + 1

        db.session.commit()

        return redirect(url_for('static', filename=worksheet.pdf_url))
    except :
        db.session.rollback()
        raise




#
# AddWorksheet
#   will handle the adding of worksheets
#   need to look up how file uploads are done
#
@worksheets.route('/add_worksheet', methods=['GET', 'POST'])
def add_worksheet():
    # check if user is logged in
    if not session.get('author_logged_in') :
        return redirect(url_for('other.home'))

    # Cannot pass in 'request.form' to WorksheetForm constructor, as this will cause 'request.files' to not be
    # sent to the form.  This will cause WorksheetForm to not see the file data.
    # Flask-WTF handles passing form data to the form, so not parameters need to be included.
    form = WorksheetForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            try :
                author = Author.query.filter_by(name=session.get('author_name')).first()

                file = request.files['worksheet_pdf']
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                new_worksheet = Worksheet(name=form.title.data, video_url=form.video_url.data,
                    pdf_url=filename, category_id=form.category.data.id, category=form.category.data,
                    author_id=author, author=author)
                db.session.add(new_worksheet)
                db.session.commit()
                return redirect(url_for('other.home'))
            except :
                db.session.rollback()
                raise
        else:
            return redirect(url_for('other.home'))

    return render_template('add_worksheet.html.j2', form=form)

#
# EditWorksheet
#   will allow the user to edit an existing worksheet that is in the database
#
@worksheets.route('/edit_worksheet/<int:id>', methods=['GET', 'POST'])
def edit_worksheet(id):
    # check if user is logged in
    if not session.get('author_logged_in') :
        return redirect(url_for('other.home'))

    worksheet = Worksheet.query.get(id)
    author = Author.query.get(worksheet.author_id)

    # check if user is logged in
    if not author.name == session.get('author_name') :
        return redirect(url_for('other.home'))

    form = EditWorksheetForm(obj=worksheet)

    if form.validate_on_submit():
        try :
            if 'worksheet_pdf' in request.files:
                if not request.files['worksheet_pdf'].filename == '':
                    # removing the old pdf
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], worksheet.pdf_url))

                    # adding the new pdf
                    file = request.files['worksheet_pdf']
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                    # updating the database values
                    worksheet.pdf_url = filename


            worksheet.name = form.title.data
            worksheet.video_url = form.video_url.data
            worksheet.category_id = form.category.data.id
            worksheet.category = form.category.data

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('other.home'))
        except :
            db.session.rollback()
            raise

    form.title.data = worksheet.name
    form.video_url.data = worksheet.video_url
    form.category.data = worksheet.category

    return render_template('edit_worksheet.html.j2', form=form, worksheet=worksheet, title="Edit Worksheet Category")



#
# DeleteWorksheet
#   will delete a specified worksheet
#
@worksheets.route('/delete_worksheet/<int:id>', methods=['GET', 'POST'])
def delete_worksheet(id):
    """
    Delete a post from the database
    """
    if not session.get('author_logged_in') :
        return redirect(url_for('other.home'))
    worksheet = Worksheet.query.get(id)
    author = Author.query.get(worksheet.author_id)

    # check if user is logged in
    if not author.name == session.get('author_name') :
        return redirect(url_for('other.home'))

    try :
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], worksheet.pdf_url))

        db.session.delete(worksheet)
        db.session.commit()

        # redirect to the home page
        return redirect(url_for('other.home'))
    except :
        db.session.rollback()
        raise

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
        try :
            new_category = WorksheetCategory(name=form.name.data)
            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('other.home'))
        except:
            db.session.rollback()
            raise

    return render_template('add_worksheet_category.html.j2', form=form)

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
        try :
            category.name = form.name.data

            db.session.commit()

            # redirect to the home page
            return redirect(url_for('other.home'))
        except :
            db.session.rollback()
            raise

    form.name.data = category.name

    return render_template('edit_worksheet_category.html.j2', form=form, category=category, title="Edit Worksheet Category")

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

    try :
        category = WorksheetCategory.query.get(id)
        db.session.delete(category)
        db.session.commit()


        # redirect to the home page
        return redirect(url_for('other.home'))
    except :
        db.session.rollback()
        raise
