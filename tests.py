from main import app
from app.models import User
from app.dependencies import get_current_user
from fastapi.testclient import TestClient

client = TestClient(app)

def mock_get_current_user():
    return User(
        username="John Doe",
        first_name="John",
        last_name="Doe",
        picture="https://example.com/john.jpg",
        email="john.doe@example.com"
    )

def test_get_user():
    app.dependency_overrides[get_current_user] = mock_get_current_user

    response = client.get('/users/me')
    
    assert response.status_code == 200
    assert response.json() == {
        "name": "John Doe",
        "given_name": "John",
        "family_name": "Doe",
        "picture": "https://example.com/john.jpg",
        "email": "john.doe@example.com"
    }
    
    del app.dependency_overrides[get_current_user]
