
def get_auth_headers(client):
    client.post(
        "/api/auth/register",
        json={
            "first_name": "Favorite",
            "last_name": "Tester",
            "email": "favorite-test@example.com",
            "password": "TestPassword123"
        }
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "favorite-test@example.com",
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_recipe(client, headers):
    response = client.post(
        "/api/recipes/",
        headers=headers,
        json={
            "title": "Domates Çorbası",
            "description": "Pratik ev yapımı çorba",
            "instructions": "Domatesleri doğrayın ve pişirin.",
            "preparation_time": 10,
            "cooking_time": 20,
            "servings": 4,
            "difficulty": "Kolay"
        }
    )

    assert response.status_code == 201

    return response.get_json()["recipe"]["id"]


def test_add_favorite_success(client):
    headers = get_auth_headers(client)
    recipe_id = create_recipe(client, headers)

    response = client.post(
        f"/api/favorites/{recipe_id}",
        headers=headers
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["favorite"]["recipe_id"] == recipe_id
    assert data["favorite"]["recipe"]["title"] == "Domates Çorbası"


def test_add_favorite_without_token(client):
    response = client.post("/api/favorites/1")

    assert response.status_code == 401


def test_add_nonexistent_recipe_to_favorites(client):
    headers = get_auth_headers(client)

    response = client.post(
        "/api/favorites/9999",
        headers=headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False

def test_add_duplicate_favorite(client):
    headers = get_auth_headers(client)
    recipe_id = create_recipe(client, headers)

    first_response = client.post(
        f"/api/favorites/{recipe_id}",
        headers=headers
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/favorites/{recipe_id}",
        headers=headers
    )

    assert second_response.status_code == 409

    data = second_response.get_json()

    assert data["success"] is False


def test_list_favorites_success(client):
    headers = get_auth_headers(client)
    recipe_id = create_recipe(client, headers)

    client.post(
        f"/api/favorites/{recipe_id}",
        headers=headers
    )

    response = client.get(
        "/api/favorites/",
        headers=headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["count"] == 1
    assert len(data["favorites"]) == 1
    assert data["favorites"][0]["recipe_id"] == recipe_id
    assert data["favorites"][0]["recipe"]["title"] == "Domates Çorbası"


def test_list_favorites_without_token(client):
    response = client.get("/api/favorites/")

    assert response.status_code == 401

def test_remove_favorite_success(client):
    headers = get_auth_headers(client)
    recipe_id = create_recipe(client, headers)

    client.post(
        f"/api/favorites/{recipe_id}",
        headers=headers
    )

    response = client.delete(
        f"/api/favorites/{recipe_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.get_json()["success"] is True

    favorites_response = client.get(
        "/api/favorites/",
        headers=headers
    )

    assert favorites_response.get_json()["count"] == 0


def test_remove_favorite_without_token(client):
    response = client.delete("/api/favorites/1")

    assert response.status_code == 401


def test_remove_nonexistent_favorite(client):
    headers = get_auth_headers(client)

    response = client.delete(
        "/api/favorites/9999",
        headers=headers
    )

    assert response.status_code == 404

    assert response.get_json()["success"] is False


def test_user_cannot_remove_another_users_favorite(client):
    first_user_headers = get_auth_headers(client)
    recipe_id = create_recipe(client, first_user_headers)

    add_response = client.post(
        f"/api/favorites/{recipe_id}",
        headers=first_user_headers
    )

    assert add_response.status_code == 201

    register_response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Second",
            "last_name": "User",
            "email": "second-favorite@example.com",
            "password": "TestPassword123"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "second-favorite@example.com",
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    second_token = login_response.get_json()["access_token"]
    second_user_headers = {
        "Authorization": f"Bearer {second_token}"
    }

    delete_response = client.delete(
        f"/api/favorites/{recipe_id}",
        headers=second_user_headers
    )

    assert delete_response.status_code == 404

    second_user_favorites = client.get(
        "/api/favorites/",
        headers=second_user_headers
    )

    assert second_user_favorites.get_json()["count"] == 0

    first_user_favorites = client.get(
        "/api/favorites/",
        headers=first_user_headers
    )

    assert first_user_favorites.get_json()["count"] == 1
