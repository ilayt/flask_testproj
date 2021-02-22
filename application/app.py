from flask import Flask

from flask_migrate import Migrate

from application.models import db
from application.models import User


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

    @app.route("/users")
    def users():
        num_users = User.query.count()
        return f"Number of users: {num_users}"

    return app
