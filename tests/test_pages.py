import re
from pathlib import Path
import pytest


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_page(client):
    response = client.get("/create")
    assert response.status_code == 200


def test_history_page(client):
    response = client.get("/history")
    assert response.status_code == 200


def test_quiz_page(client):
    response = client.get("/quiz/1")
    assert response.status_code == 200


def test_result_page(client):
    response = client.get("/result")
    assert response.status_code == 200


def test_leaderboard_page(client):
    response = client.get("/leaderboard")
    assert response.status_code == 200


PAGES_WITH_SCRIPTS = [
    ("create.html", "create.js"),
    ("history.html", "history.js"),
    ("index.html", "index.js"),
    ("leaderboard.html", "leaderboard.js"),
    ("quiz.html", "quiz.js"),
    ("result.html", "result.js"),
]


def find_missing_element_ids(template_content, script_content):
    ids_in_script = set(re.findall(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)', script_content))
    ids_in_template = set(re.findall(r'\s+id\s*=\s*["\']([^"\']+)["\']', template_content))
    return sorted(ids_in_script - ids_in_template)


@pytest.mark.parametrize("template_name, script_name", PAGES_WITH_SCRIPTS)
def test_page_template_contains_element_ids_used_by_script(template_name, script_name):
    base_dir = Path(__file__).resolve().parent.parent
    templates_dir = base_dir / "app" / "templates"
    js_dir = base_dir / "app" / "static" / "js"

    template_path = templates_dir / template_name
    script_path = js_dir / script_name

    assert template_path.exists(), f"Template '{template_name}' not found"
    assert script_path.exists(), f"Script '{script_name}' not found"

    script_content = script_path.read_text(encoding="utf-8")
    template_content = template_path.read_text(encoding="utf-8")
    base_template_content = (templates_dir / "base.html").read_text(encoding="utf-8")

    combined_html = template_content + "\n" + base_template_content
    missing_ids = find_missing_element_ids(combined_html, script_content)

    assert not missing_ids, (
        f"Template '{template_name}' is missing element IDs required by '{script_name}': {missing_ids}"
    )


def test_missing_id_detection():
    sample_script = 'const btn = document.getElementById("submit-btn");'
    sample_template = '<div id="other-btn"></div>'
    missing = find_missing_element_ids(sample_template, sample_script)
    assert missing == ["submit-btn"]
