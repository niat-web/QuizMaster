from app import db
from app.models import Attempt, Question, Quiz


def _make_question(text="Sample Question"):
    return Question(
        text=text,
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D",
        correct_option="A",
    )


def _make_attempt(player_name="Player 1"):
    return Attempt(
        player_name=player_name,
        score=1,
        total_questions=1,
        time_taken_seconds=30,
    )


def test_quiz_delete_cascades_questions_and_attempts(app):
    with app.app_context():
        quiz1 = Quiz(
            title="Quiz One",
            questions=[
                _make_question("Quiz 1 Question 1"),
                _make_question("Quiz 1 Question 2"),
            ],
            attempts=[
                _make_attempt("Player 1"),
                _make_attempt("Player 1 Retest"),
            ],
        )
        quiz2 = Quiz(
            title="Quiz Two",
            questions=[_make_question("Quiz 2 Question 1")],
            attempts=[_make_attempt("Player 2")],
        )
        db.session.add_all([quiz1, quiz2])
        db.session.commit()

        quiz1_id, quiz2_id = quiz1.id, quiz2.id

        db.session.delete(quiz1)
        db.session.commit()
        db.session.expire_all()

        assert db.session.get(Quiz, quiz1_id) is None
        assert Question.query.filter_by(quiz_id=quiz1_id).all() == []
        assert Attempt.query.filter_by(quiz_id=quiz1_id).all() == []

        persisted_quiz2 = db.session.get(Quiz, quiz2_id)
        assert persisted_quiz2 is not None
        assert persisted_quiz2.title == "Quiz Two"

        quiz2_questions = Question.query.filter_by(quiz_id=quiz2_id).all()
        assert len(quiz2_questions) == 1
        assert quiz2_questions[0].text == "Quiz 2 Question 1"

        quiz2_attempts = Attempt.query.filter_by(quiz_id=quiz2_id).all()
        assert len(quiz2_attempts) == 1
        assert quiz2_attempts[0].player_name == "Player 2"
