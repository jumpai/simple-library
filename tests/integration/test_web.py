def test_root_endpoint(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        assert response.json() == {"message": "Simple Library API"}
    else:
        assert "text/html" in content_type


def test_rest_api_lifecycle(api_client):
    # Default catalog seeded on first run
    response = api_client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert len(books) >= 5

    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    payload = {"isbn": "9780143128540", "title": "Sapiens", "author": "Yuval Noah Harari"}
    response = api_client.post("/books", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["isbn"] == "9780143128540"
    assert data["available"] is True

    response = api_client.get("/books")
    assert response.status_code == 200
    books = response.json()
    assert any(book["title"] == "Sapiens" for book in books)

    response = api_client.post("/books/9780143128540/borrow", json={"borrower": "Alice"})
    assert response.status_code == 200
    assert response.json()["available"] is False

    response = api_client.get("/books", params={"available_only": True})
    assert response.status_code == 200
    available_books = response.json()
    assert all(book["available"] for book in available_books)
    assert not any(book["isbn"] == "9780143128540" for book in available_books)

    response = api_client.post("/books/9780143128540/return")
    assert response.status_code == 200
    assert response.json()["available"] is True

    response = api_client.get("/summary")
    assert response.status_code == 200

