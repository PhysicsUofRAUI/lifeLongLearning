from flask import render_template
from . import errors


@errors.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html.j2')


@errors.app_errorhandler(500)
def page_not_found(e):
    return render_template('500.html.j2')
