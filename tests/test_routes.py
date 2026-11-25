def test_custom_404_page(client):
    response = client.get("/hello")
    assert response.status_code == 404
    assert b"404" in response.data
    assert b'href="/"' in response.data


def test_api_404_returns_json(client):
    response = client.get("/api/hello")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}
