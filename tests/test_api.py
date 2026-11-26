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
def add_true_false_question(client, quiz_id, correct_option="A"):
    return client.post(f"/api/quizzes/{quiz_id}/questions", json={
        "text": "The Earth revolves around the Sun.",
        "question_type": "true_false",
        "option_a": "True",
        "option_b": "False",
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


def test_filter_quizzes_by_category(client):
    create_quiz(client, "Physics Quiz", "medium", "Science")
    create_quiz(client, "Chemistry Quiz", "easy", "Science")
    create_quiz(client, "World History", "medium", "History")

    response = client.get("/api/quizzes?category=Science")
    assert response.status_code == 200
    quizzes = response.get_json()
    assert len(quizzes) == 2
    assert all(q["category"] == "Science" for q in quizzes)
    assert [q["title"] for q in quizzes] == ["Physics Quiz", "Chemistry Quiz"]


def test_filter_quizzes_combined(client):
    create_quiz(client, "Quantum Physics", "hard", "Science")
    create_quiz(client, "Basic Biology", "easy", "Science")
    create_quiz(client, "Ancient Rome", "hard", "History")
    create_quiz(client, "World Capitals", "easy", "Geography")

    response = client.get("/api/quizzes?category=Science&difficulty=hard")
    assert response.status_code == 200
    quizzes = response.get_json()
    assert len(quizzes) == 1
    assert quizzes[0]["title"] == "Quantum Physics"
    assert quizzes[0]["category"] == "Science"
    assert quizzes[0]["difficulty"] == "hard"


def test_filter_quizzes_no_matching_results(client):
    create_quiz(client, "Physics Quiz", "medium", "Science")
    create_quiz(client, "World History", "easy", "History")

    response = client.get("/api/quizzes?category=Art")
    assert response.status_code == 200
    assert response.get_json() == []

    response_combined = client.get("/api/quizzes?category=Science&difficulty=hard")
    assert response_combined.status_code == 200
    assert response_combined.get_json() == []


def test_get_quiz_not_found(client):
    response = client.get("/api/quizzes/999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Quiz not found"}


def test_update_quiz(client):
    quiz_id = create_quiz(client)
    response = client.put(f"/api/quizzes/{quiz_id}", json={
        "title": "Updated Quiz",
        "description": "Updated description",
        "category": "Science",
        "difficulty": "hard",
    })
    assert response.status_code == 200
    assert response.get_json()["title"] == "Updated Quiz"

    response = client.get(f"/api/quizzes/{quiz_id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Updated Quiz"


def test_update_quiz_empty_title(client):
    quiz_id = create_quiz(client)
    response = client.put(f"/api/quizzes/{quiz_id}", json={"title": "  "})
    assert response.status_code == 400


def test_update_quiz_not_found(client):
    response = client.put("/api/quizzes/999", json={"title": "Updated Quiz"})
    assert response.status_code == 404
    assert response.get_json() == {"error": "Quiz not found"}


def test_delete_quiz(client):
    quiz_id = create_quiz(client)

    response = client.delete(f"/api/quizzes/{quiz_id}")
    assert response.status_code == 200
    assert client.get(f"/api/quizzes/{quiz_id}").status_code == 404


def test_delete_quiz_not_found(client):
    response = client.delete("/api/quizzes/999")
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


def test_add_true_false_question(client):
    quiz_id = create_quiz(client)
    response = add_true_false_question(client, quiz_id)

    assert response.status_code == 201

    question = response.get_json()
    assert question["question_type"] == "true_false"
    assert question["option_a"] == "True"
    assert question["option_b"] == "False"
    assert "option_c" not in question
    assert "option_d" not in question
    assert "correct_option" not in question


def test_add_question_wrong_option_letter(client):
    quiz_id = create_quiz(client)
    response = add_question(client, quiz_id, correct_option="E")
    assert response.status_code == 400


def test_add_question_invalid_type(client):
    quiz_id = create_quiz(client)

    response = client.post(f"/api/quizzes/{quiz_id}/questions", json={
        "text": "Test question",
        "question_type": "essay",
        "option_a": "A",
        "option_b": "B",
        "correct_option": "A",
    })

    assert response.status_code == 400


def test_add_true_false_question_missing_option(client):
    quiz_id = create_quiz(client)

    response = client.post(f"/api/quizzes/{quiz_id}/questions", json={
        "text": "The Earth revolves around the Sun.",
        "question_type": "true_false",
        "option_a": "True",
        "correct_option": "A",
    })

    assert response.status_code == 400


def test_add_true_false_question_invalid_correct_option(client):
    quiz_id = create_quiz(client)
    response = add_true_false_question(
        client, quiz_id, correct_option="C"
    )

    assert response.status_code == 400


def test_add_true_false_question_rejects_extra_options(client):
    quiz_id = create_quiz(client)

    response = client.post(f"/api/quizzes/{quiz_id}/questions", json={
        "text": "The Earth revolves around the Sun.",
        "question_type": "true_false",
        "option_a": "True",
        "option_b": "False",
        "option_c": "Maybe",
        "correct_option": "A",
    })

    assert response.status_code == 400

def test_add_multiple_choice_question_missing_option(client):
    quiz_id = create_quiz(client)

    response = client.post(f"/api/quizzes/{quiz_id}/questions", json={
        "text": "What is 1 + 1?",
        "question_type": "multiple_choice",
        "option_a": "1",
        "option_b": "2",
        "option_c": "3",
        "correct_option": "B",
    })

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

def test_submit_quiz_scores_mixed_question_types(client):
    quiz_id = create_quiz(client)

    add_question(client, quiz_id, correct_option="B")
    add_true_false_question(client, quiz_id, correct_option="A")

    questions = client.get(
        f"/api/quizzes/{quiz_id}"
    ).get_json()["questions"]

    answers = {
        str(questions[0]["id"]): "B",
        str(questions[1]["id"]): "A",
    }

    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Asha",
        "answers": answers,
        "time_taken_seconds": 20,
    })

    assert response.status_code == 200

    result = response.get_json()
    assert result["score"] == 2
    assert result["wrong"] == 0


def test_submit_quiz_scores_incorrect_mixed_answers(client):
    quiz_id = create_quiz(client)

    add_question(client, quiz_id, correct_option="B")
    add_true_false_question(client, quiz_id, correct_option="A")

    questions = client.get(
        f"/api/quizzes/{quiz_id}"
    ).get_json()["questions"]

    answers = {
        str(questions[0]["id"]): "A",
        str(questions[1]["id"]): "B",
    }

    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Asha",
        "answers": answers,
    })

    assert response.status_code == 200

    result = response.get_json()
    assert result["score"] == 0
    assert result["wrong"] == 2


def test_submit_quiz_rejects_boolean_time_taken(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id, "B")
    question_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]

    for bool_value in [True, False]:
        response = client.post(f"/api/quizzes/{quiz_id}/submit", json={
            "player_name": "Asha",
            "answers": {str(question_id): "B"},
            "time_taken_seconds": bool_value,
        })
        assert response.status_code == 400
        assert response.get_json() == {
            "error": "time_taken_seconds must be a positive number"
        }


def test_submit_quiz_missing_player_name(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id)
    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={"answers": {}})
    assert response.status_code == 400

def test_submit_quiz_rejects_31_char_name(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id)
    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "a" * 31,
        "answers": {}
    })
    assert response.status_code == 400

def test_submit_quiz_accepts_30_char_name(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id)
    response = client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "a" * 30,
        "answers": {}
    })
    assert response.status_code == 200

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


def test_player_attempts_empty_name(client):
    response_spaces = client.get("/api/players/%20%20/attempts")
    assert response_spaces.status_code == 400
    assert response_spaces.get_json()["error"] == "Player name is required"


def test_player_attempts_unknown_player(client):
    response = client.get("/api/players/UnknownPlayer/attempts")
    assert response.status_code == 200
    assert response.get_json() == []


def test_player_attempts_single_attempt(client):
    quiz_id = create_quiz(client, title="Science Quiz")
    add_question(client, quiz_id, "B")
    q_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]
    client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Alice",
        "answers": {str(q_id): "B"},
        "time_taken_seconds": 15,
    })

    response = client.get("/api/players/Alice/attempts")
    assert response.status_code == 200
    attempts = response.get_json()
    assert len(attempts) == 1
    attempt = attempts[0]
    assert attempt["player_name"] == "Alice"
    assert attempt["quiz_title"] == "Science Quiz"
    assert attempt["score"] == 1
    assert attempt["total_questions"] == 1
    assert attempt["time_taken_seconds"] == 15
    assert attempt["created_at"] is not None


def test_player_attempts_multiple_newest_first(client):
    quiz1 = create_quiz(client, title="History Quiz")
    quiz2 = create_quiz(client, title="Geography Quiz")
    add_question(client, quiz1, "A")
    add_question(client, quiz2, "B")
    q1 = client.get(f"/api/quizzes/{quiz1}").get_json()["questions"][0]["id"]
    q2 = client.get(f"/api/quizzes/{quiz2}").get_json()["questions"][0]["id"]

    client.post(f"/api/quizzes/{quiz1}/submit", json={
        "player_name": "Alice",
        "answers": {str(q1): "A"},
        "time_taken_seconds": 10,
    })
    client.post(f"/api/quizzes/{quiz2}/submit", json={
        "player_name": "Alice",
        "answers": {str(q2): "B"},
        "time_taken_seconds": 20,
    })
    client.post(f"/api/quizzes/{quiz1}/submit", json={
        "player_name": "Alice",
        "answers": {str(q1): "B"},  # wrong
        "time_taken_seconds": 5,
    })

    response = client.get("/api/players/Alice/attempts")
    assert response.status_code == 200
    attempts = response.get_json()
    assert len(attempts) == 3
    # Check newest first
    assert attempts[0]["quiz_title"] == "History Quiz"
    assert attempts[0]["score"] == 0
    assert attempts[1]["quiz_title"] == "Geography Quiz"
    assert attempts[1]["score"] == 1
    assert attempts[2]["quiz_title"] == "History Quiz"
    assert attempts[2]["score"] == 1
    assert attempts[0]["id"] > attempts[1]["id"] > attempts[2]["id"]


def test_player_attempts_case_insensitive(client):
    quiz_id = create_quiz(client, title="Case Test")
    add_question(client, quiz_id, "B")
    q_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]
    client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Bob",
        "answers": {str(q_id): "B"},
    })

    for name_variant in ["bob", "BOB", "bOb", "Bob"]:
        response = client.get(f"/api/players/{name_variant}/attempts")
        assert response.status_code == 200
        attempts = response.get_json()
        assert len(attempts) == 1
        assert attempts[0]["player_name"] == "Bob"


def test_player_attempts_spaces_handling(client):
    quiz_id = create_quiz(client, title="Spaces Test")
    add_question(client, quiz_id, "B")
    q_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]
    client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Charlie Brown",
        "answers": {str(q_id): "B"},
    })

    response = client.get("/api/players/Charlie%20Brown/attempts")
    assert response.status_code == 200
    assert len(response.get_json()) == 1

    # Search with leading and trailing spaces
    response_trimmed = client.get("/api/players/%20Charlie%20Brown%20/attempts")
    assert response_trimmed.status_code == 200
    assert len(response_trimmed.get_json()) == 1


def test_player_attempts_isolation(client):
    quiz_id = create_quiz(client)
    add_question(client, quiz_id)
    q_id = client.get(f"/api/quizzes/{quiz_id}").get_json()["questions"][0]["id"]
    client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Eve",
        "answers": {str(q_id): "B"},
    })
    client.post(f"/api/quizzes/{quiz_id}/submit", json={
        "player_name": "Frank",
        "answers": {str(q_id): "B"},
    })

    eve_attempts = client.get("/api/players/Eve/attempts").get_json()
    assert len(eve_attempts) == 1
    assert eve_attempts[0]["player_name"] == "Eve"


def test_history_page_rendered(client):
    response = client.get("/history")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "History" in html
    assert 'id="history-form"' in html
    assert 'id="player-name"' in html
    assert 'id="history-table"' in html


def test_navigation_includes_history(client):
    for endpoint in ["/", "/leaderboard", "/history"]:
        response = client.get(endpoint)
        assert response.status_code == 200
        html = response.data.decode("utf-8")
        assert 'href="/history"' in html
