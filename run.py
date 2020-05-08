from flask import Flask

import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)
app.app_context().push()

if __name__ == '__main__':
    app.run()
