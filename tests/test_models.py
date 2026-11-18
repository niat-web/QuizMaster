from app.models import Attempt, Question, Quiz
from app import db


def test_question_to_dict_excludes_correct_option(app):
    with app.app_context():
        quiz = Quiz(title="Sample Quiz")
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

        data = question.to_dict()
        assert "correct_option" not in data
        assert data["id"] == question.id
        assert data["text"] == "What is 2 + 2?"
        assert data["option_a"] == "3"
        assert data["option_b"] == "4"
        assert data["option_c"] == "5"
        assert data["option_d"] == "6"
        assert set(data.keys()) == {"id", "text", "option_a", "option_b", "option_c", "option_d"}


def test_quiz_to_dict_includes_question_count(app):
    with app.app_context():
        quiz = Quiz(
            title="Math Basics",
            description="Simple arithmetic",
            category="Math",
            difficulty="easy",
        )
        db.session.add(quiz)
        db.session.commit()

        # Add two questions
        for i in range(2):
            q = Question(
                quiz_id=quiz.id,
                text=f"Question {i}",
                option_a="A",
                option_b="B",
                option_c="C",
                option_d="D",
                correct_option="A",
            )
            db.session.add(q)
        db.session.commit()

        data = quiz.to_dict()
        assert data["id"] == quiz.id
        assert data["title"] == "Math Basics"
        assert data["description"] == "Simple arithmetic"
        assert data["category"] == "Math"
        assert data["difficulty"] == "easy"
        assert data["question_count"] == 2
        assert "created_at" in data
        assert isinstance(data["created_at"], str)


def test_attempt_to_dict(app):
    with app.app_context():
        quiz = Quiz(title="Sample")
        db.session.add(quiz)
        db.session.commit()

        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="Alice",
            score=8,
            total_questions=10,
            time_taken_seconds=45,
        )
        db.session.add(attempt)
        db.session.commit()

        data = attempt.to_dict()
        assert data["id"] == attempt.id
        assert data["player_name"] == "Alice"
        assert data["score"] == 8
        assert data["total_questions"] == 10
        assert data["time_taken_seconds"] == 45
        assert "created_at" in data
        assert isinstance(data["created_at"], str)
        assert set(data.keys()) == {
            "id",
            "player_name",
            "score",
            "total_questions",
            "time_taken_seconds",
            "created_at",
        }
