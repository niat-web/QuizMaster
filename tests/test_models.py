
from datetime import datetime

from app import db
from app.models import Attempt, Question, Quiz


def test_question_to_dict_excludes_correct_option(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Math Quiz")
        db.session.add(quiz)
        db.session.commit()

        question = Question(
            quiz_id=quiz.id,
            text="What is 2 + 2?",
            option_a="1",
            option_b="2",
            option_c="3",
            option_d="4",
            correct_option="D",
        )
        db.session.add(question)
        db.session.commit()

        data = question.to_dict()

        assert "correct_option" not in data
        assert data["id"] == question.id
        assert data["text"] == "What is 2 + 2?"
        assert data["option_a"] == "1"
        assert data["option_b"] == "2"
        assert data["option_c"] == "3"
        assert data["option_d"] == "4"
        assert set(data.keys()) == {
            "id",
            "text",
            "question_type",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
        }


def test_quiz_to_dict_includes_all_fields(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(
            title="Python Basics",
            description="Test your Python knowledge",
            category="Programming",
            difficulty="easy",
        )
        db.session.add(quiz)
        db.session.commit()

        data = quiz.to_dict()

        assert data["id"] == quiz.id
        assert data["title"] == "Python Basics"
        assert data["description"] == "Test your Python knowledge"
        assert data["category"] == "Programming"
        assert data["difficulty"] == "easy"
        assert data["question_count"] == 0
        assert data["created_at"] == quiz.created_at.isoformat()
        assert set(data.keys()) == {
            "id",
            "title",
            "description",
            "category",
            "difficulty",
            "question_count",
            "created_at",
        }

        q1 = Question(
            quiz_id=quiz.id,
            text="Which keyword defines a function?",
            option_a="def",
            option_b="func",
            option_c="function",
            option_d="define",
            correct_option="A",
        )
        q2 = Question(
            quiz_id=quiz.id,
            text="What does len() return?",
            option_a="Length",
            option_b="Type",
            option_c="Index",
            option_d="Value",
            correct_option="A",
        )
        db.session.add_all([q1, q2])
        db.session.commit()

        updated_data = quiz.to_dict()
        assert updated_data["question_count"] == 2


def test_quiz_to_dict_defaults(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Minimal Quiz")
        db.session.add(quiz)
        db.session.commit()

        data = quiz.to_dict()

        assert data["title"] == "Minimal Quiz"
        assert data["description"] == ""
        assert data["category"] == "General"
        assert data["difficulty"] == "easy"
        assert data["question_count"] == 0


def test_attempt_to_dict(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Science Quiz")
        db.session.add(quiz)
        db.session.commit()

        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="Asha",
            score=3,
            total_questions=5,
            time_taken_seconds=45,
        )
        db.session.add(attempt)
        db.session.commit()

        data = attempt.to_dict()

        assert data["id"] == attempt.id
        assert data["quiz_id"] == quiz.id
        assert data["quiz_title"] == "Science Quiz"
        assert data["player_name"] == "Asha"
        assert data["score"] == 3
        assert data["total_questions"] == 5
        assert data["time_taken_seconds"] == 45
        assert data["created_at"] == attempt.created_at.isoformat()
        assert set(data.keys()) == {
            "id",
            "quiz_id",
            "quiz_title",
            "player_name",
            "score",
            "total_questions",
            "time_taken_seconds",
            "created_at",
        }


def test_question_to_dict_options_and_no_leak_all_letters(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Options Quiz")
        db.session.add(quiz)
        db.session.commit()

        for letter in ["A", "B", "C", "D"]:
            question = Question(
                quiz_id=quiz.id,
                text=f"Question with correct {letter}",
                option_a="Alpha <tag>",
                option_b="Beta & symbols",
                option_c="Gamma 123",
                option_d="Delta 🎉",
                correct_option=letter,
            )
            db.session.add(question)
            db.session.commit()

            data = question.to_dict()

            assert "correct_option" not in data
            assert data["option_a"] == "Alpha <tag>"
            assert data["option_b"] == "Beta & symbols"
            assert data["option_c"] == "Gamma 123"
            assert data["option_d"] == "Delta 🎉"
            assert set(data.keys()) == {
                "id",
                "text",
                "question_type",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
            }


def test_attempt_to_dict_zero_score_and_time(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Tough Quiz")
        db.session.add(quiz)
        db.session.commit()

        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="PlayerZero",
            score=0,
            total_questions=10,
            time_taken_seconds=0,
        )
        db.session.add(attempt)
        db.session.commit()

        data = attempt.to_dict()

        assert data["score"] == 0
        assert data["time_taken_seconds"] == 0
        assert data["total_questions"] == 10
        assert data["player_name"] == "PlayerZero"


def test_models_created_at_is_valid_isoformat(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Time Quiz")
        db.session.add(quiz)
        db.session.commit()

        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="Timer",
            score=2,
            total_questions=2,
        )
        db.session.add(attempt)
        db.session.commit()

        quiz_dict = quiz.to_dict()
        attempt_dict = attempt.to_dict()

        dt_quiz = datetime.fromisoformat(quiz_dict["created_at"])
        dt_attempt = datetime.fromisoformat(attempt_dict["created_at"])

        assert dt_quiz is not None
        assert dt_attempt is not None


def test_quiz_to_dict_with_no_questions(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Empty Quiz")
        db.session.add(quiz)
        db.session.commit()

        result = quiz.to_dict()

        assert result["question_count"] == 0


def test_attempt_to_dict_default_time(app):
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Test Quiz")
        db.session.add(quiz)
        db.session.commit()

        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="Bob",
            score=5,
            total_questions=10,
        )
        db.session.add(attempt)
        db.session.commit()

        result = attempt.to_dict()

        assert result["time_taken_seconds"] == 0
