from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from ..models import Author

#
# AuthorForm
#   Name: A string field to allow the user to enter the name of the author
#   Email: A string field to hold an email address (optional)
#   about: short description of the author (optional)
#
class LearnerForm(FlaskForm) :
    """
    Form used to submit new authors
    """
    name = StringField('Name')
    email = StringField('Email')
    screenname = StringField('Screen-name')
    password = PasswordField('password')

    submit = SubmitField('Submit')


#
# AuthorLoginForm: Will be the form displayed when an author wants to login.
#
class LearnerLoginForm(FlaskForm):
    """
    Form used to login authors
    """
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
