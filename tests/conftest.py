
import threading

import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from app import create_app, db


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
        "LOAD_SEED_DATA": False,
        "SUBMIT_RATE_LIMIT": "1000 per minute",
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def browser_app(tmp_path):
    db_path = tmp_path / "browser-test.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path.as_posix()}",
        "LOAD_SEED_DATA": False,
    })

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def live_server(browser_app):
    server = make_server("127.0.0.1", 0, browser_app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_port}"

    yield base_url

    server.shutdown()
    thread.join()


@pytest.fixture
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()
