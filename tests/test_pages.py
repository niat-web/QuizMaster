def test_how_to_play_page(client):
    response = client.get("/how-to-play")
    assert response.status_code == 200
    assert b"30 characters" in response.data
    assert b"unanswered" in response.data.lower()


def test_how_to_play_link_on_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"/how_to_play" in response.data