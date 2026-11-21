from contextlib import contextmanager
from sqlalchemy import event

from app import db
from app.models import Attempt


def create_quiz_with_questions(
    client, title, difficulty="easy", category="General", question_count=0
):
    res = client.post("/api/quizzes", json={
        "title": title,
        "difficulty": difficulty,
        "category": category,
    })
    quiz_id = res.get_json()["id"]
    for i in range(question_count):
        client.post(f"/api/quizzes/{quiz_id}/questions", json={
            "text": f"Question {i + 1} for {title}",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "A",
        })
    return quiz_id


@contextmanager
def count_select_queries(app):
    queries = []

    def capture(conn, cursor, statement, parameters, context, executemany):
        if statement.strip().upper().startswith("SELECT"):
            queries.append(statement)

    with app.app_context():
        engine = db.engine
    event.listen(engine, "before_cursor_execute", capture)
    try:
        yield queries
    finally:
        event.remove(engine, "before_cursor_execute", capture)


def test_list_quizzes_question_counts_and_zero_questions(client):
    q1_id = create_quiz_with_questions(client, "Quiz Alpha", question_count=3)
    q2_id = create_quiz_with_questions(client, "Quiz Beta", question_count=0)
    q3_id = create_quiz_with_questions(client, "Quiz Gamma", question_count=1)

    response = client.get("/api/quizzes")
    assert response.status_code == 200
    quizzes = response.get_json()

    assert len(quizzes) == 3
    assert [q["id"] for q in quizzes] == [q1_id, q2_id, q3_id]
    assert [q["question_count"] for q in quizzes] == [3, 0, 1]

    expected_keys = {
        "id", "title", "description", "category",
        "difficulty", "question_count", "created_at"
    }
    for q in quizzes:
        assert set(q.keys()) == expected_keys


def test_list_quizzes_filters_with_question_counts(client):
    create_quiz_with_questions(
        client, "Sci Easy", "easy", "Science", question_count=2
    )
    create_quiz_with_questions(
        client, "Sci Hard", "hard", "Science", question_count=4
    )
    create_quiz_with_questions(
        client, "Hist Easy", "easy", "History", question_count=1
    )

    res_cat = client.get("/api/quizzes?category=Science")
    assert res_cat.status_code == 200
    sci_quizzes = res_cat.get_json()
    assert len(sci_quizzes) == 2
    assert [q["question_count"] for q in sci_quizzes] == [2, 4]

    res_comb = client.get("/api/quizzes?category=Science&difficulty=hard")
    assert res_comb.status_code == 200
    comb_quizzes = res_comb.get_json()
    assert len(comb_quizzes) == 1
    assert comb_quizzes[0]["title"] == "Sci Hard"
    assert comb_quizzes[0]["question_count"] == 4


def test_stats_multiple_attempts_and_zero_attempts(client):
    q1_id = create_quiz_with_questions(client, "Maths", question_count=2)
    q2_id = create_quiz_with_questions(client, "Literature", question_count=1)

    q1_details = client.get(f"/api/quizzes/{q1_id}").get_json()
    q1, q2 = [str(q["id"]) for q in q1_details["questions"]]

    # Submit 3 attempts with scores 1, 2, 1 -> avg = 4/3 = 1.333... -> 1.33
    client.post(f"/api/quizzes/{q1_id}/submit", json={
        "player_name": "P1",
        "answers": {q1: "A"},
        "time_taken_seconds": 10,
    })
    client.post(f"/api/quizzes/{q1_id}/submit", json={
        "player_name": "P2",
        "answers": {q1: "A", q2: "A"},
        "time_taken_seconds": 20,
    })
    client.post(f"/api/quizzes/{q1_id}/submit", json={
        "player_name": "P3",
        "answers": {q1: "A", q2: "B"},
        "time_taken_seconds": 15,
    })

    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()

    assert data["total_quizzes"] == 2
    assert data["total_attempts"] == 3
    assert len(data["quizzes"]) == 2

    q1_stat = next(s for s in data["quizzes"] if s["quiz_id"] == q1_id)
    assert q1_stat["attempts"] == 3
    assert q1_stat["average_score"] == 1.33

    q2_stat = next(s for s in data["quizzes"] if s["quiz_id"] == q2_id)
    assert q2_stat["attempts"] == 0
    assert q2_stat["average_score"] == 0


def test_stats_counts_orphan_attempts(app, client):
    q_id = create_quiz_with_questions(client, "History Quiz", question_count=1)
    client.post(f"/api/quizzes/{q_id}/submit", json={
        "player_name": "Player 1",
        "answers": {},
        "time_taken_seconds": 10,
    })

    with app.app_context():
        orphan = Attempt(
            quiz_id=9999,
            player_name="Orphan",
            score=0,
            total_questions=1,
            time_taken_seconds=5,
        )
        db.session.add(orphan)
        db.session.commit()

    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()

    assert data["total_quizzes"] == 1
    assert data["total_attempts"] == 2
    assert len(data["quizzes"]) == 1
    assert data["quizzes"][0]["quiz_id"] == q_id


def test_query_count_constant_for_quiz_list(app, client):
    for i in range(5):
        create_quiz_with_questions(client, f"Quiz {i}", question_count=2)

    with count_select_queries(app) as queries:
        with app.app_context():
            db.session.remove()
        res = client.get("/api/quizzes")
        assert res.status_code == 200
        assert len(res.get_json()) == 5
        assert len(queries) == 1

        for i in range(5, 15):
            create_quiz_with_questions(client, f"Quiz {i}", question_count=2)

        with app.app_context():
            db.session.remove()
        queries.clear()
        res15 = client.get("/api/quizzes")
        assert res15.status_code == 200
        assert len(res15.get_json()) == 15
        assert len(queries) == 1


def test_query_count_constant_for_stats(app, client):
    for i in range(5):
        q_id = create_quiz_with_questions(
            client, f"Quiz {i}", question_count=1
        )
        client.post(f"/api/quizzes/{q_id}/submit", json={
            "player_name": f"P{i}",
            "answers": {},
            "time_taken_seconds": 10,
        })

    with count_select_queries(app) as queries:
        with app.app_context():
            db.session.remove()
        res = client.get("/api/stats")
        assert res.status_code == 200
        assert res.get_json()["total_quizzes"] == 5
        assert len(queries) == 2

        for i in range(5, 15):
            q_id = create_quiz_with_questions(
                client, f"Quiz {i}", question_count=1
            )
            client.post(f"/api/quizzes/{q_id}/submit", json={
                "player_name": f"P{i}",
                "answers": {},
                "time_taken_seconds": 10,
            })

        with app.app_context():
            db.session.remove()
        queries.clear()
        res15 = client.get("/api/stats")
        assert res15.status_code == 200
        assert res15.get_json()["total_quizzes"] == 15
        assert len(queries) == 2
