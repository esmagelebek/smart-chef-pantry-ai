
def validate_recipe_data(data, partial=False):
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek verisi.")

    allowed_fields = {
        "title",
        "description",
        "instructions",
        "preparation_time",
        "cooking_time",
        "servings",
        "difficulty",
        "image_url",
        "source_url",
        "youtube_url",
        "ingredients"
    }

    if not data:
        raise ValueError("En az bir alan gönderilmelidir.")

    unknown_fields = set(data.keys()) - allowed_fields

    if unknown_fields:
        raise ValueError("Geçersiz alan gönderildi.")

    required_fields = {"title", "instructions"}

    if not partial:
        missing_fields = required_fields - set(data.keys())

        if missing_fields:
            raise ValueError("Tarif başlığı ve yapılışı zorunludur.")

    validated_data = {}

    # Metin alanlarının doğrulanması.
    text_fields = {
        "title": 200,
        "description": None,
        "instructions": None,
        "difficulty": 50,
        "image_url": 500,
        "source_url": 500,
        "youtube_url": 500
    }

    for field, max_length in text_fields.items():
        if field not in data:
            continue

        value = data[field]

        if not isinstance(value, str):
            raise ValueError(f"{field} metin formatında olmalıdır.")

        value = value.strip()

        if field in required_fields and not value:
            raise ValueError(f"{field} boş bırakılamaz.")

        if max_length is not None and len(value) > max_length:
            raise ValueError(
                f"{field} en fazla {max_length} karakter olabilir."
            )

        validated_data[field] = value or None

    # Sayısal alanların doğrulanması.
    integer_fields = {
        "preparation_time": 0,
        "cooking_time": 0,
        "servings": 1
    }

    for field, minimum in integer_fields.items():
        if field not in data:
            continue

        value = data[field]

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field} pozitif tam sayı formatında olmalıdır.")

        if value < minimum:
            raise ValueError(f"{field} en az {minimum} olmalıdır.")

        validated_data[field] = value

    # Tarif malzemelerinin doğrulanması.
    if "ingredients" in data:
        ingredients = data["ingredients"]

        if not isinstance(ingredients, list):
            raise ValueError("ingredients liste formatında olmalıdır.")

        validated_ingredients = []
        ingredient_ids = set()

        for item in ingredients:
            if not isinstance(item, dict):
                raise ValueError("Her malzeme bir nesne olmalıdır.")

            allowed_ingredient_fields = {
                "ingredient_id",
                "quantity",
                "unit"
            }

            if set(item.keys()) - allowed_ingredient_fields:
                raise ValueError("Geçersiz malzeme alanı gönderildi.")

            ingredient_id = item.get("ingredient_id")

            if (
                isinstance(ingredient_id, bool)
                or not isinstance(ingredient_id, int)
                or ingredient_id <= 0
            ):
                raise ValueError("Geçerli bir ingredient_id gönderilmelidir.")

            if ingredient_id in ingredient_ids:
                raise ValueError("Aynı malzeme tarife birden fazla eklenemez.")

            ingredient_ids.add(ingredient_id)

            quantity = item.get("quantity")

            if quantity is not None:
                if isinstance(quantity, bool):
                    raise ValueError("Malzeme miktarı sayısal olmalıdır.")

                try:
                    quantity = float(quantity)
                except (TypeError, ValueError):
                    raise ValueError("Malzeme miktarı sayısal olmalıdır.")

                if quantity <= 0:
                    raise ValueError("Malzeme miktarı sıfırdan büyük olmalıdır.")

            unit = item.get("unit")

            if unit is not None:
                if not isinstance(unit, str):
                    raise ValueError("Malzeme birimi metin formatında olmalıdır.")

                unit = unit.strip()

                if not unit:
                    unit = None

                elif len(unit) > 50:
                    raise ValueError("Malzeme birimi en fazla 50 karakter olabilir.")

            validated_ingredients.append({
                "ingredient_id": ingredient_id,
                "quantity": quantity,
                "unit": unit
            })

        validated_data["ingredients"] = validated_ingredients

    return validated_data
