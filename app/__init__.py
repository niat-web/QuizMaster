import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

db = SQLAlchemy()

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
)


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///quizmaster.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["LOAD_SEED_DATA"] = True

    # Rate limiting configuration
    app.config["SUBMIT_RATE_LIMIT"] = "2 per minute"

    app.config["RATELIMIT_HEADERS_ENABLED"] = True

    app.config["RATELIMIT_STORAGE_URI"] = os.environ.get(
        "RATELIMIT_STORAGE_URI", "memory://"
    )

    if test_config:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    limiter.init_app(app)

    # Custom JSON response for rate limit errors
    @app.errorhandler(429)
    def ratelimit_error(error):
        response = error.get_response()

        response.set_data(
            app.json.dumps({
                "error": "Too many quiz submissions. Please try again later."
            })
        )

        response.content_type = "application/json"

        return response

    from app.routes import api, pages

    app.register_blueprint(api)
    app.register_blueprint(pages)

    with app.app_context():
        from app.seed import seed_data

        db.create_all()

        if app.config["LOAD_SEED_DATA"] and not app.config["TESTING"]:
            seed_data()

    return app