from app import create_app, db
from app.models import Quiz


def test_database_url_env_var(monkeypatch):
    test_url = "sqlite:///:memory:"
    monkeypatch.setenv("DATABASE_URL", test_url)

    app = create_app({"LOAD_SEED_DATA": False})
    with app.app_context():
        assert app.config["SQLALCHEMY_DATABASE_URI"] == test_url
        db.session.remove()
        db.drop_all()


def test_test_config_overrides_defaults():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "LOAD_SEED_DATA": False,
            "CUSTOM_SETTING": "custom_value",
        }
    )
    with app.app_context():
        assert app.config["TESTING"] is True
        assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
        assert app.config["LOAD_SEED_DATA"] is False
        assert app.config["CUSTOM_SETTING"] == "custom_value"
        db.session.remove()
        db.drop_all()


def test_load_seed_data_true_and_false():
    seeded_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "LOAD_SEED_DATA": True,
        }
    )
    with seeded_app.app_context():
        assert Quiz.query.count() > 0
        db.session.remove()
        db.drop_all()

    unseeded_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "LOAD_SEED_DATA": False,
        }
    )
    with unseeded_app.app_context():
        assert Quiz.query.count() == 0
        db.session.remove()
        db.drop_all()