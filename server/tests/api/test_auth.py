import pytest
from app.core.security import get_password_hash
from app.models.user import User

def test_login(client, db_session):
    # Create test user
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/login",
        data={"username": "test@example.com", "password": "password123"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()