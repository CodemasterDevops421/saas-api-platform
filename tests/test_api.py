from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import crud, schemas
from app.core import security

def test_create_user(client: TestClient, test_db: Session):
    data = {"email": "test@example.com", "password": "testpassword"}
    response = client.post("/api/v1/users/", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == data["email"]
    assert "id" in content

def test_create_api_key(client: TestClient, test_db: Session):
    # First create a user
    user_data = {"email": "test@example.com", "password": "testpassword"}
    user = crud.create_user(test_db, schemas.UserCreate(**user_data))
    
    # Create API key
    headers = {"Authorization": f"Bearer {security.create_access_token(user.id)}"}
    data = {"name": "Test Key"}
    response = client.post("/api/v1/users/api-keys", json=data, headers=headers)
    
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert "key" in content

def test_subscription_creation(client: TestClient, test_db: Session):
    # Create user and plan
    user_data = {"email": "test@example.com", "password": "testpassword"}
    user = crud.create_user(test_db, schemas.UserCreate(**user_data))
    
    plan_data = {
        "name": "Basic",
        "price_monthly": 10.0,
        "stripe_price_id": "price_test"
    }
    plan = crud.create_plan(test_db, schemas.PlanCreate(**plan_data))
    
    # Create subscription
    headers = {"Authorization": f"Bearer {security.create_access_token(user.id)}"}
    data = {"plan_id": plan.id}
    response = client.post("/api/v1/payment/create-subscription", json=data, headers=headers)
    
    assert response.status_code == 200
    content = response.json()
    assert "subscription_id" in content
    assert "client_secret" in content