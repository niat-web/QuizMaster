import pytest

from app import db
from app.models import Quiz, Question, Attempt


def test_question_to_dict_excludes_correct_option(app):
    """Test that Question.to_dict does not include correct_option"""
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Test Quiz")
        db.session.add(quiz)
        db.session.commit()

        question = Question(
            quiz_id=quiz.id,
            text="What is 2 + 2?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            correct_option="B",
        )
        db.session.add(question)
        db.session.commit()

        result = question.to_dict()

        # Check that correct_option is NOT included
        assert "correct_option" not in result

        # Check that other fields are included
        assert result["id"] == question.id
        assert result["text"] == "What is 2 + 2?"
        assert result["option_a"] == "3"
        assert result["option_b"] == "4"
        assert result["option_c"] == "5"
        assert result["option_d"] == "6"


def test_quiz_to_dict_includes_all_fields(app):
    """Test that Quiz.to_dict includes all expected fields and question_count"""
    with app.app_context():
        db.create_all()

        quiz = Quiz(
            title="History Quiz",
            description="Test your history knowledge",
            category="History",
            difficulty="medium",
        )
        db.session.add(quiz)
        db.session.commit()

        # Add some questions
        for i in range(3):
            question = Question(
                quiz_id=quiz.id,
                text=f"Question {i + 1}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="A",
            )
            db.session.add(question)
        db.session.commit()

        result = quiz.to_dict()

        # Check all required fields
        assert result["id"] == quiz.id
        assert result["title"] == "History Quiz"
        assert result["description"] == "Test your history knowledge"
        assert result["category"] == "History"
        assert result["difficulty"] == "medium"
        assert result["question_count"] == 3
        assert "created_at" in result


def test_attempt_to_dict(app):
    """Test that Attempt.to_dict includes all expected fields"""
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Test Quiz")
        db.session.add(quiz)
        db.session.commit()

        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="Alice",
            score=8,
            total_questions=10,
            time_taken_seconds=120,
        )
        db.session.add(attempt)
        db.session.commit()

        result = attempt.to_dict()

        # Check all required fields
        assert result["id"] == attempt.id
        assert result["player_name"] == "Alice"
        assert result["score"] == 8
        assert result["total_questions"] == 10
        assert result["time_taken_seconds"] == 120
        assert "created_at" in result


def test_quiz_to_dict_with_no_questions(app):
    """Test that Quiz.to_dict returns question_count=0 when there are no questions"""
    with app.app_context():
        db.create_all()

        quiz = Quiz(title="Empty Quiz")
        db.session.add(quiz)
        db.session.commit()

        result = quiz.to_dict()

        assert result["question_count"] == 0


def test_attempt_to_dict_default_time(app):
    """Test that Attempt.to_dict handles default time_taken_seconds"""
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
            # time_taken_seconds not provided, should default to 0
        )
        db.session.add(attempt)
        db.session.commit()

        result = attempt.to_dict()

        assert result["time_taken_seconds"] == 0
