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

    from flask import jsonify, render_template_string

    from app.openapi import OPENAPI_SPEC

    def openapi_spec():
        return jsonify(OPENAPI_SPEC)

    def api_docs():
        return render_template_string("""<!doctype html>
<html><head><title>QuizMaster API docs</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"></head>
<body><div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>SwaggerUIBundle({url: "/api/openapi.json", dom_id: "#swagger-ui"});</script>
</body></html>""")

    app.add_url_rule(
        "/api/openapi.json", "openapi_spec", openapi_spec, methods=["GET"]
    )
    app.add_url_rule(
        "/api/docs", "api_docs", api_docs, methods=["GET"]
    )

    with app.app_context():
        from app.seed import seed_data
        db.create_all()
        if app.config["LOAD_SEED_DATA"]:
            seed_data()

    return app
