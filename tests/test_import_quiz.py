import json

import pytest

from app.models import Quiz


@pytest.fixture
def cli_runner(app):
    return app.test_cli_runner()


def _write_json(tmp_path, data, name="quiz.json"):
    path = tmp_path / name
    path.write_text(json.dumps(data))
    return str(path)


VALID_QUIZ = {
    "title": "Import Test Quiz",
    "description": "Imported via CLI",
    "category": "Testing",
    "difficulty": "easy",
    "questions": [
        {
            "text": "What is 1 + 1?",
            "option_a": "1",
            "option_b": "2",
            "option_c": "3",
            "option_d": "4",
            "correct_option": "B",
        },
        {
            "text": "What colour is the sky?",
            "option_a": "Red",
            "option_b": "Green",
            "option_c": "Blue",
            "option_d": "Yellow",
            "correct_option": "C",
        },
    ],
}



#  success 

def test_valid_import_exits_zero(cli_runner, tmp_path):
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, VALID_QUIZ)])
    assert result.exit_code == 0


def test_valid_import_creates_quiz_and_questions(app, cli_runner, tmp_path):
    cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, VALID_QUIZ)])
    with app.app_context():
        quiz = Quiz.query.filter_by(title="Import Test Quiz").first()
        assert quiz is not None
        assert len(quiz.questions) == 2


def test_valid_import_prints_quiz_title(cli_runner, tmp_path):
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, VALID_QUIZ)])
    assert "Import Test Quiz" in result.output



#  invalid question — nothing saved 

def test_invalid_question_exits_nonzero(cli_runner, tmp_path):
    data = {**VALID_QUIZ, "questions": [
        {**VALID_QUIZ["questions"][0], "correct_option": "E"},
    ]}
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    assert result.exit_code != 0


def test_invalid_question_saves_nothing(app, cli_runner, tmp_path):
    data = {**VALID_QUIZ, "questions": [
        {**VALID_QUIZ["questions"][0]},                          # valid
        {**VALID_QUIZ["questions"][0], "correct_option": "E"},  # invalid
    ]}
    cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    with app.app_context():
        assert Quiz.query.filter_by(title="Import Test Quiz").first() is None


def test_error_message_names_bad_question_number(cli_runner, tmp_path):
    data = {**VALID_QUIZ, "questions": [
        {**VALID_QUIZ["questions"][0]},                          # q1 — valid
        {**VALID_QUIZ["questions"][0], "correct_option": "E"},  # q2 — invalid
    ]}
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    assert "2" in result.output  # error should mention question 2


def test_missing_question_text_saves_nothing(app, cli_runner, tmp_path):
    data = {**VALID_QUIZ, "questions": [
        {**VALID_QUIZ["questions"][0], "text": ""},
    ]}
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    assert result.exit_code != 0
    with app.app_context():
        assert Quiz.query.filter_by(title="Import Test Quiz").first() is None


# bad file 

def test_missing_file_exits_nonzero(cli_runner):
    result = cli_runner.invoke(args=["import-quiz", "does_not_exist.json"])
    assert result.exit_code != 0


def test_missing_file_error_message(cli_runner):
    result = cli_runner.invoke(args=["import-quiz", "does_not_exist.json"])
    assert "not found" in result.output.lower()


def test_invalid_json_exits_nonzero(cli_runner, tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{ not valid json }")
    result = cli_runner.invoke(args=["import-quiz", str(path)])
    assert result.exit_code != 0


def test_invalid_json_error_message(cli_runner, tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{ not valid json }")
    result = cli_runner.invoke(args=["import-quiz", str(path)])
    assert "invalid" in result.output.lower() or "json" in result.output.lower()



# bad quiz field

def test_missing_title_exits_nonzero(cli_runner, tmp_path):
    data = {k: v for k, v in VALID_QUIZ.items() if k != "title"}
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    assert result.exit_code != 0


def test_missing_title_error_message(cli_runner, tmp_path):
    data = {k: v for k, v in VALID_QUIZ.items() if k != "title"}
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    assert "title" in result.output.lower()


def test_wrong_difficulty_exits_nonzero(cli_runner, tmp_path):
    data = {**VALID_QUIZ, "difficulty": "impossible"}
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    assert result.exit_code != 0


def test_empty_questions_list_exits_nonzero(cli_runner, tmp_path):
    data = {**VALID_QUIZ, "questions": []}
    result = cli_runner.invoke(args=["import-quiz", _write_json(tmp_path, data)])
    assert result.exit_code != 0