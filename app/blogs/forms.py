from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import PostCategory

#
# This function is designed to obtain choices for the categories in the PostForm.
#
def category_choices() :
    return PostCategory.query



#
# PostForm
# Purpose:
#     Gives the user a way to input information into the post table.
#
# Fields:
#     Title: String Field (Required)
#     Category: QuerySelectField (Required)
#       Obtains the categories from the database. As of right now there exists
#       only two categories (Travel and Projects)
#
#     Content: Text Field (Required)
#     Submit: Submit Field
#
class PostForm(FlaskForm):
    """
    Form that lets the user add a new post
    """

    title = StringField('Title', validators=[DataRequired()])
    category = QuerySelectField('Category', validators=[DataRequired()], query_factory=category_choices)
    content = TextAreaField('Content', validators=[DataRequired()])

    submit = SubmitField('Submit')


#
# PostCategoryForm
# Purpose:
#     allows user to add new subcategories
#
# Fields:
#     Name: String Field (Required)
#     Submit: SubmitField
#
class PostCategoryForm(FlaskForm) :
    """
    Form used to submit new subcategories
    """
    name = StringField('Name', validators=[DataRequired()])

    submit = SubmitField('Submit')
