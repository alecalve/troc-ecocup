import os
from flask import Flask
from helpers import register_blueprints
from database import db
import conf


def create_app(create_db=False):
    """Creates an app by registering blueprints in the modules directory
    and loading the configuration

    """

    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    register_blueprints(app, "modules", ["modules"])

    app.config["SQLALCHEMY_DATABASE_URI"] = conf.DB
    # Maximum 3Mo pour les images
    app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024

    db.init_app(app)
    db.app = app

    if create_db:
        db.create_all()

    return app
