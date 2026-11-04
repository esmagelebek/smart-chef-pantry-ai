
from app.extensions import db
from app.models.user import User


def test_register_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True

    user = User.query.filter_by(email="test@example.com").first()

    assert user is not None
    assert user.password_hash != "TestPassword123"


def test_register_duplicate_email(client):
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "duplicate@example.com",
        "password": "TestPassword123"
    }

    first_response = client.post(
        "/api/auth/register",
        json=payload
    )

    second_response = client.post(
        "/api/auth/register",
        json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    data = second_response.get_json()

    assert data["success"] is False
    assert data["message"] == "Bu e-posta adresi zaten kayıtlı."


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "login@example.com",
            "password": "TestPassword123"
        }
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert "access_token" in data


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "wrongpass@example.com",
            "password": "TestPassword123"
        }
    )

    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401

    data = response.get_json()

    assert data["success"] is False
