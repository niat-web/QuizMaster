from sqlalchemy import event, inspect
from app import db
from app.models import Quiz, Question, Attempt


def count_queries(app, client, url):
    queries = []

    def callback(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    with app.app_context():
        engine = db.engine
        event.listen(engine, "before_cursor_execute", callback)
        try:
            response = client.get(url)
        finally:
            event.remove(engine, "before_cursor_execute", callback)

    return response, len(queries)


def test_quiz_list_query_count_does_not_grow(client, app):
    with app.app_context():
        for i in range(5):
            quiz = Quiz(title=f"Quiz {i}", category="General", difficulty="easy")
            db.session.add(quiz)
            db.session.flush()
            for j in range(3):
                q = Question(
                    quiz_id=quiz.id,
                    text=f"Question {j}",
                    option_a="A",
                    option_b="B",
                    option_c="C",
                    option_d="D",
                    correct_option="A",
                )
                db.session.add(q)
        db.session.commit()

    response, count = count_queries(app, client, "/api/quizzes")
    assert response.status_code == 200
    quizzes = response.get_json()
    assert len(quizzes) == 5
    assert all(q["question_count"] == 3 for q in quizzes)
    assert count == 1


def test_stats_query_count_does_not_grow(client, app):
    with app.app_context():
        for i in range(5):
            quiz = Quiz(title=f"Quiz {i}", category="General", difficulty="easy")
            db.session.add(quiz)
            db.session.flush()
            for k in range(2):
                attempt = Attempt(
                    quiz_id=quiz.id,
                    player_name=f"Player {k}",
                    score=10,
                    total_questions=10,
                    time_taken_seconds=30,
                )
                db.session.add(attempt)
        db.session.commit()

    response, count = count_queries(app, client, "/api/stats")
    assert response.status_code == 200
    stats = response.get_json()
    assert stats["total_quizzes"] == 5
    assert stats["total_attempts"] == 10
    assert len(stats["quizzes"]) == 5
    assert count == 2


def test_indexes_exist_on_foreign_keys(app):
    with app.app_context():
        inspector = inspect(db.engine)

        question_indexes = inspector.get_indexes("question")
        question_cols = [col for idx in question_indexes for col in idx.get("column_names", [])]
        assert "quiz_id" in question_cols

        attempt_indexes = inspector.get_indexes("attempt")
        attempt_cols = [col for idx in attempt_indexes for col in idx.get("column_names", [])]
        assert "quiz_id" in attempt_cols
