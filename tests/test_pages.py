def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_quiz_page(client):
    response = client.get("/quiz/1")
    assert response.status_code == 200


def test_result_page(client):
    response = client.get("/result")
    assert response.status_code == 200


def test_leaderboard_page(client):
    response = client.get("/leaderboard")
    assert response.status_code == 200
