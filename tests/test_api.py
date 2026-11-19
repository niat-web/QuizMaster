def create_quiz(client, title="Test Quiz", difficulty="easy", category="General"):
    response = client.post("/api/quizzes", json={
        "title": title,
        "difficulty": difficulty,
        "category": category,
    })
    return response.get_json()["id"]


def add_question(client, quiz_id, correct_option="B"):
    return client.post(f"/api/quizzes/{quiz_id}/questions", json={
        "text": "What is 1 + 1?",
        "option_a": "1",
        "option_b": "2",
        "option_c": "3",
        "option_d": "4",
        "correct_option": correct_option,
    })


def test_list_quizzes_empty(client):
    response = client.get("/api/quizzes")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_quiz(client):
    response = client.post("/api/quizzes", json={"title": "Maths"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Maths"
    assert data["difficulty"] == "easy"


def test_create_quiz_empty_title(client):
    response = client.post("/api/quizzes", json={"title": "  "})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_quiz_wrong_difficulty(client):
    response = client.post("/api/quizzes", json={
        "title": "Maths",
        "difficulty": "impossible",
    })
    assert response.status_code == 400


def test_create_quiz_duplicate_title(client):
    response1 = client.post("/api/quizzes", json={"title": "Geography"})
    assert response1.status_code == 201

    response2 = client.post("/api/quizzes", json={"title": "Geography"})
    assert response2.status_code == 400
    assert response2.get_json()["error"] == "A quiz with this title already exists"


def test_create_quiz_duplicate_title_case_insensitive(client):
    response1 = client.post("/api/quizzes", json={"title": "Science"})
    assert response1.status_code == 201

    response2 = client.post("/api/quizzes", json={"title": "science"})
    assert response2.status_code == 400
    assert response2.get_json()["error"] == "A quiz with this title already exists"

    response3 = client.post("/api/quizzes", json={"title": "History"})
    assert response3.status_code == 201


def test_filter_quizzes_by_difficulty(client):
    create_quiz(client, "Easy One", "easy")
    create_quiz(client, "Hard One", "hard")
    response = client.get("/api/quizzes?difficulty=hard")
    quizzes = response.get_json()
    assert len(quizzes) == 1
    assert quizzes[0]["title"] == "Hard One"


def test_get_quiz_not_found(client):
    response = client.get("/api/quizzes/999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Quiz not found"}


def test_get_quiz_hides_correct_answers(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id)
    response = client.get(f"/api/quizzes/{quiz_id}")
    questions = response.get_json()["questions"]
    assert len(questions) == 1
    assert "correct_option" not in questions[0]


def test_add_question(client):
    quiz_id = create_quiz(client)
    response = add_question(client, quiz_id)
    assert response.status_code == 201
    assert response.get_json()["text"] == "What is 1 + 1?"


def test_add_question_wrong_option_letter(client):
    quiz_id = create_quiz(client)
    response = add_question(client, quiz_id, correct_option="E")
    assert response.status_code == 400


def test_add_question_quiz_not_found(client):
    response = add_question(client, 999)
    assert response.status_code == 404


def test_submit_quiz_scores_answers(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id, "B")
    question_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]

    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Asha",
        "answers": {str(question_id): "B"},
        "time_taken_seconds": 12,
    })
    assert response.status_code == 200
    result = response.get_json()
    assert result["score"] == 1
    assert result["wrong"] == 0
    assert result["time_taken_seconds"] == 12


def test_submit_quiz_missing_player_name(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id)
    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={"answers": {}})
    assert response.status_code == 400


def test_submit_quiz_not_found(client):
    response = client.post("/api/quizzes/999/submit", json={
        "player_name": "Asha",
        "answers": {},
    })
    assert response.status_code == 404


def test_submit_quiz_rate_limit(client, app):
    app.config["SUBMIT_RATE_LIMIT"] = "2 per minute"
    quiz_id = create_quiz(client)
    add_question(client, quiz_id)
    question_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]
    payload = {
        "player_name": "Asha",
        "answers": {str(question_id): "B"},
    }

    assert client.post(f"/api/quizzes/{quiz_id}/submit", json=payload).status_code == 200
    assert client.post(f"/api/quizzes/{quiz_id}/submit", json=payload).status_code == 200
    response = client.post(f"/api/quizzes/{quiz_id}/submit", json=payload)

    assert response.status_code == 429
    assert response.get_json() == {
        "error": "Too many submissions. Please try again later."
    }
    assert response.headers["Retry-After"].isdigit()


def test_leaderboard_is_sorted_and_limited(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id, "B")
    question_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]
    for i in range(12):
        # Even numbered players answer correctly
        answer = "B" if i % 2 == 0 else "A"
        client.post(f"/api/quizzes/{quiz_id}/submit", json={
            "player_name": f"Player {i}",
            "answers": {str(question_id): answer},
        })

    response = client.get(f"/api/quizzes/{quiz_id}/leaderboard")
    entries = response.get_json()
    assert len(entries) == 10
    assert entries[0]["score"] == 1
    assert entries[-1]["score"] == 0


def test_stats(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id, "B")
    question_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]
    client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Asha",
        "answers": {str(question_id): "B"},
    })

    stats = client.get("/api/stats").get_json()
    assert stats["total_quizzes"] == 1
    assert stats["total_attempts"] == 1
    assert stats["quizzes"][0]["average_score"] == 1
