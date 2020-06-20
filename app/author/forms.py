from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from ..models import Author

#
# AuthorForm
#   Name: A string field to allow the user to enter the name of the author
#   Email: A string field to hold an email address (optional)
#   about: short description of the author (optional)
#
class AuthorForm(FlaskForm) :
    """
    Form used to submit new subcategories
    """
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email')
    about = StringField('About')

    submit = SubmitField('Submit')
