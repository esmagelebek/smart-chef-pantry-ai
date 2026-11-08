
def get_auth_headers(client):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Recipe",
            "last_name": "Tester",
            "email": "recipe-test@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "recipe-test@example.com",
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.get_json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_ingredient(client, headers):
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

    return response.get_json()["ingredient"]["id"]


def create_recipe_payload():
    return {
        "title": "Domates Çorbası",
        "description": "Pratik ev yapımı çorba",
        "instructions": "Domatesleri doğrayın ve pişirin.",
        "preparation_time": 10,
        "cooking_time": 20,
        "servings": 4,
        "difficulty": "Kolay"
    }


def test_create_recipe_success(client):
    headers = get_auth_headers(client)

    response = client.post(
        "/api/recipes/",
        headers=headers,
        json=create_recipe_payload()
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["recipe"]["title"] == "Domates Çorbası"
    assert data["recipe"]["servings"] == 4
    assert data["recipe"]["preparation_time"] == 10
    assert data["recipe"]["cooking_time"] == 20
    assert data["recipe"]["ingredients"] == []

def test_create_recipe_with_ingredients(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    payload = create_recipe_payload()
    payload["ingredients"] = [
        {
            "ingredient_id": ingredient_id,
            "quantity": 3,
            "unit": "adet"
        }
    ]

    response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert len(data["recipe"]["ingredients"]) == 1
    assert data["recipe"]["ingredients"][0]["ingredient_id"] == ingredient_id
    assert data["recipe"]["ingredients"][0]["ingredient_name"] == "Domates"
    assert data["recipe"]["ingredients"][0]["quantity"] == 3.0
    assert data["recipe"]["ingredients"][0]["unit"] == "adet"
def test_create_recipe_without_token(client):
    response = client.post(
        "/api/recipes/",
        json=create_recipe_payload()
    )

    assert response.status_code == 401
def test_create_recipe_with_empty_title(client):
    headers = get_auth_headers(client)

    payload = create_recipe_payload()
    payload["title"] = ""

    response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False
def test_create_recipe_with_missing_required_field(client):
    headers = get_auth_headers(client)

    payload = create_recipe_payload()
    del payload["instructions"]

    response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False
def test_create_recipe_with_invalid_ingredient_id(client):
    headers = get_auth_headers(client)

    payload = create_recipe_payload()
    payload["ingredients"] = [
        {
            "ingredient_id": 9999,
            "quantity": 2,
            "unit": "adet"
        }
    ]

    response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False
    assert "9999" in response.get_json()["message"]
def test_create_recipe_with_duplicate_ingredients(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    payload = create_recipe_payload()
    payload["ingredients"] = [
        {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        },
        {
            "ingredient_id": ingredient_id,
            "quantity": 3,
            "unit": "adet"
        }
    ]

    response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert response.status_code == 400
    assert response.get_json()["success"] is False
def test_recipe_list(client):
    headers = get_auth_headers(client)

    payload = create_recipe_payload()

    create_response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert create_response.status_code == 201

    response = client.get("/api/recipes/")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["count"] == 1
    assert len(data["recipes"]) == 1
    assert data["recipes"][0]["title"] == "Domates Çorbası"
def test_get_recipe_by_id(client):
    headers = get_auth_headers(client)

    create_response = client.post(
        "/api/recipes/",
        headers=headers,
        json=create_recipe_payload()
    )

    assert create_response.status_code == 201

    recipe_id = create_response.get_json()["recipe"]["id"]

    response = client.get(f"/api/recipes/{recipe_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["recipe"]["id"] == recipe_id
    assert data["recipe"]["title"] == "Domates Çorbası"
def test_get_nonexistent_recipe(client):
    response = client.get("/api/recipes/9999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Tarif bulunamadı."
def test_update_recipe_success(client):
    headers = get_auth_headers(client)

    create_response = client.post(
        "/api/recipes/",
        headers=headers,
        json=create_recipe_payload()
    )

    assert create_response.status_code == 201

    recipe_id = create_response.get_json()["recipe"]["id"]

    response = client.put(
        f"/api/recipes/{recipe_id}",
        headers=headers,
        json={
            "title": "Güncellenmiş Domates Çorbası",
            "cooking_time": 30
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["recipe"]["title"] == "Güncellenmiş Domates Çorbası"
    assert data["recipe"]["cooking_time"] == 30
    assert data["recipe"]["servings"] == 4
def test_update_recipe_without_token(client):
    response = client.put(
        "/api/recipes/1",
        json={
            "title": "Yetkisiz Güncelleme"
        }
    )

    assert response.status_code == 401
def test_update_nonexistent_recipe(client):
    headers = get_auth_headers(client)

    response = client.put(
        "/api/recipes/9999",
        headers=headers,
        json={
            "title": "Olmayan Tarif"
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Tarif bulunamadı."
def test_update_recipe_ingredients(client):
    headers = get_auth_headers(client)

    first_ingredient_id = create_ingredient(client, headers)

    second_ingredient_response = client.post(
        "/api/ingredients/",
        headers=headers,
        json={
            "name": "Soğan",
            "category": "Sebze",
            "unit": "adet"
        }
    )

    assert second_ingredient_response.status_code == 201

    second_ingredient_id = (
        second_ingredient_response.get_json()["ingredient"]["id"]
    )

    payload = create_recipe_payload()
    payload["ingredients"] = [
        {
            "ingredient_id": first_ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    ]

    create_response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert create_response.status_code == 201

    recipe_id = create_response.get_json()["recipe"]["id"]

    update_response = client.put(
        f"/api/recipes/{recipe_id}",
        headers=headers,
        json={
            "ingredients": [
                {
                    "ingredient_id": second_ingredient_id,
                    "quantity": 3,
                    "unit": "adet"
                }
            ]
        }
    )

    assert update_response.status_code == 200

    updated_ingredients = update_response.get_json()["recipe"]["ingredients"]

    assert len(updated_ingredients) == 1
    assert updated_ingredients[0]["ingredient_id"] == second_ingredient_id
    assert updated_ingredients[0]["ingredient_name"] == "Soğan"
    assert updated_ingredients[0]["quantity"] == 3.0
def test_update_recipe_without_ingredients_keeps_existing(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    payload = create_recipe_payload()
    payload["ingredients"] = [
        {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    ]

    create_response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert create_response.status_code == 201

    recipe_id = create_response.get_json()["recipe"]["id"]

    update_response = client.put(
        f"/api/recipes/{recipe_id}",
        headers=headers,
        json={
            "title": "Güncellenmiş Domates Çorbası"
        }
    )

    assert update_response.status_code == 200

    updated_recipe = update_response.get_json()["recipe"]

    assert updated_recipe["title"] == "Güncellenmiş Domates Çorbası"
    assert len(updated_recipe["ingredients"]) == 1
    assert updated_recipe["ingredients"][0]["ingredient_id"] == ingredient_id
def test_update_recipe_with_empty_ingredients_clears_existing(client):
    headers = get_auth_headers(client)
    ingredient_id = create_ingredient(client, headers)

    payload = create_recipe_payload()
    payload["ingredients"] = [
        {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "adet"
        }
    ]

    create_response = client.post(
        "/api/recipes/",
        headers=headers,
        json=payload
    )

    assert create_response.status_code == 201

    recipe_id = create_response.get_json()["recipe"]["id"]

    update_response = client.put(
        f"/api/recipes/{recipe_id}",
        headers=headers,
        json={
            "ingredients": []
        }
    )

    assert update_response.status_code == 200

    updated_recipe = update_response.get_json()["recipe"]

    assert updated_recipe["ingredients"] == []
def test_delete_recipe_success(client):
    headers = get_auth_headers(client)

    create_response = client.post(
        "/api/recipes/",
        headers=headers,
        json=create_recipe_payload()
    )

    assert create_response.status_code == 201

    recipe_id = create_response.get_json()["recipe"]["id"]

    delete_response = client.delete(
        f"/api/recipes/{recipe_id}",
        headers=headers
    )

    assert delete_response.status_code == 200

    data = delete_response.get_json()

    assert data["success"] is True
    assert data["message"] == "Tarif başarıyla silindi."

    detail_response = client.get(f"/api/recipes/{recipe_id}")

    assert detail_response.status_code == 404
def test_delete_recipe_without_token(client):
    response = client.delete("/api/recipes/1")

    assert response.status_code == 401
def test_delete_nonexistent_recipe(client):
    headers = get_auth_headers(client)

    response = client.delete(
        "/api/recipes/9999",
        headers=headers
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["success"] is False
    assert data["message"] == "Tarif bulunamadı."