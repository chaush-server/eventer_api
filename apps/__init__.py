import os

from flask import Flask
from apps.api import api_bp
from apps.config import Config
from apps.models.models import Role
from extensions import db, jwt
from extensions.migrate import migrate


# from tests.database_mock import create_role


def register_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(api_bp)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:
            raise e

    @app.teardown_request
    def shutdown_session(exception):
        db.session.remove()


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_DATABASE_URL')
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
