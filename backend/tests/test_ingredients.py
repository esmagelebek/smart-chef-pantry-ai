
from app.models.ingredient import Ingredient


def get_auth_headers(client):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "ingredient-test@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "ingredient-test@example.com",
            "password": "TestPassword123"
        }
    )

    token = login_response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_create_ingredient_success(client):
    headers = get_auth_headers(client)

    response = client.post(
        "/api/ingredients/",
        headers=headers,
        json={
            "name": "Domates",
            "category": "Sebze",
            "unit": "adet"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["ingredient"]["name"] == "Domates"


def test_create_duplicate_ingredient(client):
    headers = get_auth_headers(client)

    payload = {
        "name": "Domates",
        "category": "Sebze",
        "unit": "adet"
    }

    first_response = client.post(
        "/api/ingredients/",
        headers=headers,
        json=payload
    )

    second_response = client.post(
        "/api/ingredients/",
        headers=headers,
        json=payload
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    data = second_response.get_json()

    assert data["success"] is False
    assert data["message"] == "Bu malzeme zaten kayıtlı."


def test_create_ingredient_without_token(client):
    response = client.post(
        "/api/ingredients/",
        json={
            "name": "Salatalık",
            "category": "Sebze",
            "unit": "adet"
        }
    )

    assert response.status_code == 401


def test_update_ingredient_duplicate_name(client):
    headers = get_auth_headers(client)

    first = client.post(
        "/api/ingredients/",
        headers=headers,
        json={"name": "Domates"}
    )

    second = client.post(
        "/api/ingredients/",
        headers=headers,
        json={"name": "Salatalık"}
    )

    ingredient_id = second.get_json()["ingredient"]["id"]

    response = client.put(
        f"/api/ingredients/{ingredient_id}",
        headers=headers,
        json={"name": "Domates"}
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert response.status_code == 409


def test_update_nonexistent_ingredient(client):
    headers = get_auth_headers(client)

    response = client.put(
        "/api/ingredients/999",
        headers=headers,
        json={"name": "Yeni Malzeme"}
    )

    assert response.status_code == 404


def test_delete_ingredient_without_token(client):
    response = client.delete("/api/ingredients/1")

    assert response.status_code == 401


def test_ingredient_list(client):
    headers = get_auth_headers(client)

    client.post(
        "/api/ingredients/",
        headers=headers,
        json={"name": "Havuç"}
    )

    response = client.get("/api/ingredients/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["count"] == 1
    assert data["ingredients"][0]["name"] == "Havuç"
