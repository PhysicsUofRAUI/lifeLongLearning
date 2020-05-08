from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

#
# Purpose: This from will be used to collect the information for the user logging
#     and logging out.
#
# Fields:
#     Password: The password to validate the user
#     Username: This contains the name that a user has chosen to represent them
#     Submit: This is the field that the user uses to signal that everything has been
#         filled out.
#
# Returns:
#     All the material that the user filled out (bassically all the fields but filled
#         out).
#
class LoginForm(FlaskForm):
    """
    Form for users to login
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
