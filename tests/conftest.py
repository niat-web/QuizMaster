import pytest

from app import create_app, db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "LOAD_SEED_DATA": False,

        # Use a high limit for normal tests
        "SUBMIT_RATE_LIMIT": "100 per minute",
    })

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()