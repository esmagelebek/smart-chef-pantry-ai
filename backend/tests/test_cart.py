def get_auth_headers(client):
    register_response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Cart",
            "last_name": "Tester",
            "email": "cart-test@example.com",
            "password": "TestPassword123"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "cart-test@example.com",
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_ingredient(client, headers, name="Domates", unit="adet"):
    response = client.post(
        "/api/ingredients/",
        headers=headers,
        json={
            "name": name,
            "category": "Sebze",
            "unit": unit
        }
    )

    assert response.status_code == 201

    return response.get_json()["ingredient"]["id"]


def test_get_empty_cart_success(client):
    headers = get_auth_headers(client)

    response = client.get(
        "/api/cart/",
        headers=headers
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["cart"]["items"] == []
    assert data["cart"]["item_count"] == 0


def test_get_cart_without_token(client):
    response = client.get("/api/cart/")

    assert response.status_code == 401
def test_add_item_to_cart_success(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["cart_item"]["ingredient_id"] == ingredient_id
    assert float(data["cart_item"]["quantity"]) == 2
    assert data["cart_item"]["unit"] == "adet"


def test_add_same_item_increases_quantity(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    first_response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    )

    second_response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 3,
            "unit": "adet"
        }
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 200

    data = second_response.get_json()

    assert data["success"] is True
    assert float(data["cart_item"]["quantity"]) == 5


def test_add_item_with_different_unit(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "kg"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_add_item_with_invalid_quantity(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 0,
            "unit": "adet"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_add_item_without_token(client):
    response = client.post(
        "/api/cart/items",
        json={
            "ingredient_id": 1,
            "quantity": 2,
            "unit": "adet"
        }
    )

    assert response.status_code == 401


def test_add_nonexistent_ingredient_to_cart(client):
    headers = get_auth_headers(client)

    response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": 9999,
            "quantity": 2,
            "unit": "adet"
        }
    )

    assert response.status_code == 404
    assert response.get_json()["success"] is False
def test_update_cart_item_success(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    add_response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    )

    item_id = add_response.get_json()["cart_item"]["id"]

    response = client.put(
        f"/api/cart/items/{item_id}",
        headers=headers,
        json={
            "quantity": 5
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert float(data["cart_item"]["quantity"]) == 5


def test_update_cart_item_with_invalid_quantity(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    add_response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    )

    item_id = add_response.get_json()["cart_item"]["id"]

    response = client.put(
        f"/api/cart/items/{item_id}",
        headers=headers,
        json={
            "quantity": 0
        }
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_update_cart_item_without_token(client):
    response = client.put(
        "/api/cart/items/1",
        json={
            "quantity": 5
        }
    )

    assert response.status_code == 401


def test_remove_cart_item_success(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    add_response = client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    )

    item_id = add_response.get_json()["cart_item"]["id"]

    response = client.delete(
        f"/api/cart/items/{item_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.get_json()["success"] is True

    cart_response = client.get(
        "/api/cart/",
        headers=headers
    )

    assert cart_response.get_json()["cart"]["items"] == []


def test_remove_cart_item_without_token(client):
    response = client.delete("/api/cart/items/1")

    assert response.status_code == 401


def test_remove_nonexistent_cart_item(client):
    headers = get_auth_headers(client)

    response = client.delete(
        "/api/cart/items/9999",
        headers=headers
    )

    assert response.status_code == 404
    assert response.get_json()["success"] is False
def test_clear_cart_success(client):
    headers = get_auth_headers(client)

    first_ingredient_id = create_ingredient(
        client,
        headers,
        name="Domates"
    )

    second_ingredient_id = create_ingredient(
        client,
        headers,
        name="Patates"
    )

    client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": first_ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    )

    client.post(
        "/api/cart/items",
        headers=headers,
        json={
            "ingredient_id": second_ingredient_id,
            "quantity": 3,
            "unit": "adet"
        }
    )

    response = client.delete(
        "/api/cart/",
        headers=headers
    )

    assert response.status_code == 200
    assert response.get_json()["success"] is True

    cart_response = client.get(
        "/api/cart/",
        headers=headers
    )

    assert cart_response.status_code == 200
    assert cart_response.get_json()["cart"]["items"] == []


def test_clear_cart_without_token(client):
    response = client.delete("/api/cart/")

    assert response.status_code == 401


def test_user_cannot_access_another_users_cart(client):
    first_user_headers = get_auth_headers(client)

    ingredient_id = create_ingredient(
        client,
        first_user_headers
    )

    add_response = client.post(
        "/api/cart/items",
        headers=first_user_headers,
        json={
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    )

    assert add_response.status_code == 201

    register_response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Second",
            "last_name": "User",
            "email": "second-cart@example.com",
            "password": "TestPassword123"
        }
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "second-cart@example.com",
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    second_token = login_response.get_json()["access_token"]

    second_user_headers = {
        "Authorization": f"Bearer {second_token}"
    }

    response = client.get(
        "/api/cart/",
        headers=second_user_headers
    )

    assert response.status_code == 200
    assert response.get_json()["cart"]["items"] == []

    second_delete_response = client.delete(
        f"/api/cart/items/{add_response.get_json()['cart_item']['id']}",
        headers=second_user_headers
    )

    assert second_delete_response.status_code == 404
def test_update_nonexistent_cart_item(client):
    headers = get_auth_headers(client)

    response = client.put(
        "/api/cart/items/9999",
        headers=headers,
        json={
            "quantity": 5
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False
    assert "bulunamadı" in data["message"].lower()