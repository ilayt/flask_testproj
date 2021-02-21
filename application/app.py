from flask import Flask

from application.models import db
from flask_migrate import Migrate


def create_app(config_name):

    app = Flask(__name__)
    config_module = f"application.config.{config_name.capitalize()}Config"
    app.config.from_object(config_module)

    db.init_app(app)

    migrate = Migrate()
    migrate.init_app(app, db)

    @app.route("/")
    def hello_world():
        print('request came')
        return "Hello, World!"

    return app
