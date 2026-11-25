import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_limiter.errors import RateLimitExceeded
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

db = SQLAlchemy()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///quizmaster.db"
    )
    app.config["LOAD_SEED_DATA"] = True
    app.config["SUBMIT_RATE_LIMIT"] = os.environ.get(
        "SUBMIT_RATE_LIMIT", "10 per minute"
    )
    app.config["RATELIMIT_STORAGE_URI"] = os.environ.get(
        "RATELIMIT_STORAGE_URI", "memory://"
    )
    app.config["RATELIMIT_HEADERS_ENABLED"] = True
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    limiter.init_app(app)

    from app.routes import api, pages
    app.register_blueprint(api)
    app.register_blueprint(pages)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(error):
        response = jsonify({
            "error": "Too many submissions. Please try again later."
        })
        response.status_code = 429
        retry_after = getattr(error, "retry_after", None)
        if retry_after is not None:
            response.headers["Retry-After"] = str(max(1, int(retry_after)))
        return response

    with app.app_context():
        from app.seed import seed_data
        db.create_all()
        if app.config["LOAD_SEED_DATA"]:
            seed_data()

    return app
