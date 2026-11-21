def test_custom_404_page(client):
    response = client.get("/hello")
    assert response.status_code == 404
    assert b"404" in response.data
    assert b'href="/"' in response.data


def test_api_404_returns_json(client):
    response = client.get("/api/hello")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}


def test_favicon_linked_in_base_template(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'rel="icon"' in response.data
    assert b'favicon.ico' in response.data


def test_favicon_static_file_accessible(client):
    response = client.get("/static/favicon.ico")
    assert response.status_code == 200
    assert len(response.data) > 0
    assert response.data[:4] == b"\x00\x00\x01\x00"
