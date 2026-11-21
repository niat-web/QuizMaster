import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import ALL_OPTIONS, Attempt, DIFFICULTIES, OPTIONS, Question, Quiz


def test_quiz_valid_difficulties(app):
    with app.app_context():
        for diff in DIFFICULTIES:
            quiz = Quiz(title=f"Quiz {diff}", difficulty=diff)
            db.session.add(quiz)
        db.session.commit()
        assert Quiz.query.count() == len(DIFFICULTIES)


def test_quiz_invalid_difficulty_rejected(app):
    with app.app_context():
        quiz = Quiz(title="Invalid Quiz", difficulty="extreme")
        db.session.add(quiz)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_question_valid_options(app):
    with app.app_context():
        quiz = Quiz(title="Sample Quiz")
        db.session.add(quiz)
        db.session.commit()

        for opt in ALL_OPTIONS:
            q = Question(
                quiz_id=quiz.id,
                text=f"Question for {opt}",
                option_a="1",
                option_b="2",
                option_c="3",
                option_d="4",
                correct_option=opt,
            )
            db.session.add(q)
        db.session.commit()
        assert Question.query.count() == len(ALL_OPTIONS)


def test_question_invalid_correct_option_rejected(app):
    with app.app_context():
        quiz = Quiz(title="Sample Quiz")
        db.session.add(quiz)
        db.session.commit()

        q = Question(
            quiz_id=quiz.id,
            text="Invalid option question",
            option_a="1",
            option_b="2",
            option_c="3",
            option_d="4",
            correct_option="E",
        )
        db.session.add(q)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_attempt_valid_scores(app):
    with app.app_context():
        quiz = Quiz(title="Sample Quiz")
        db.session.add(quiz)
        db.session.commit()

        # Score at minimum boundary (0)
        a1 = Attempt(quiz_id=quiz.id, player_name="Player 1", score=0, total_questions=5)
        # Score in middle
        a2 = Attempt(quiz_id=quiz.id, player_name="Player 2", score=3, total_questions=5)
        # Score at maximum boundary (total_questions)
        a3 = Attempt(quiz_id=quiz.id, player_name="Player 3", score=5, total_questions=5)

        db.session.add_all([a1, a2, a3])
        db.session.commit()
        assert Attempt.query.count() == 3


def test_attempt_score_greater_than_total_rejected(app):
    with app.app_context():
        quiz = Quiz(title="Sample Quiz")
        db.session.add(quiz)
        db.session.commit()

        # Score > total_questions
        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="Cheater",
            score=6,
            total_questions=5,
        )
        db.session.add(attempt)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_attempt_negative_score_rejected(app):
    with app.app_context():
        quiz = Quiz(title="Sample Quiz")
        db.session.add(quiz)
        db.session.commit()

        # Score < 0
        attempt = Attempt(
            quiz_id=quiz.id,
            player_name="Negative",
            score=-1,
            total_questions=5,
        )
        db.session.add(attempt)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
