import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///quizmaster.db"
    )
    app.config["LOAD_SEED_DATA"] = True
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app.routes import api, pages
    app.register_blueprint(api)
    app.register_blueprint(pages)

    from app.commands import import_quiz_command
    app.cli.add_command(import_quiz_command)

    with app.app_context():
        from app.seed import seed_data
        db.create_all()
        if app.config["LOAD_SEED_DATA"]:
            seed_data()

    return app
