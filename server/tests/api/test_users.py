def test_create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "new@example.com",
            "password": "StrongPass123!",
            "full_name": "Test User"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["full_name"] == "Test User"
    assert "password" not in data