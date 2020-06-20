from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileField, FileRequired
from ..models import Author, WorksheetCategory

#
# This function is designed to obtain choices for the categories in the PostForm.
#
def category_choices() :
    return WorksheetCategory.query

#
# This function is designed to obtain choices for authors in the WorksheetForm
#
def author_choices() :
    return Author.query

#
# WorksheetForm
#   Name: A string field for the user to enter the name of the worksheet
#
#   file upload field: to let the user upload a file
#
#   video_url: link to a video filling out the worksheet
#
#   category: A query select field like was done in the personal website
#
#   author: also use a queryselect field
#
class WorksheetForm(FlaskForm):
    """
    Form that lets the user add a new post
    """

    title = StringField('Title', validators=[DataRequired()])
    category = QuerySelectField('Category', validators=[DataRequired()], query_factory=category_choices)
    author = QuerySelectField('Author', validators=[DataRequired()], query_factory=author_choices)
    video_url = StringField('Video URL (optional)')
    worksheet_pdf = FileField('PDF File', validators=[FileRequired()])

    submit = SubmitField('Submit')



#
# EditWorksheetForm
#
class EditWorksheetForm(FlaskForm):
    """
    Form that lets the user add a new post
    """

    title = StringField('Title', validators=[DataRequired()])
    category = QuerySelectField('Category', validators=[DataRequired()], query_factory=category_choices)
    author = QuerySelectField('Author', validators=[DataRequired()], query_factory=author_choices)
    video_url = StringField('Video URL (optional)')

    submit = SubmitField('Submit')



#
# WorksheetCategoryForm
#   Name: A string field to allow the user to enter the name of the category
#
class WorksheetCategoryForm(FlaskForm) :
    """
    Form used to submit new subcategories
    """
    name = StringField('Name', validators=[DataRequired()])

    submit = SubmitField('Submit')
