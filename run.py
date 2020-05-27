from flask import Flask
from config import ProductionConfiguration

import os

from app import create_app

app = create_app(ProductionConfiguration)
app.app_context().push()

if __name__ == '__main__':
    app.run()
