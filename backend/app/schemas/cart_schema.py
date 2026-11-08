from decimal import Decimal, InvalidOperation


def validate_add_cart_item_data(data):
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek verisi.")

    allowed_fields = {
        "ingredient_id",
        "quantity",
        "unit"
    }

    if not data:
        raise ValueError("İstek verisi boş olamaz.")

    if set(data.keys()) - allowed_fields:
        raise ValueError("Geçersiz alan gönderildi.")

    required_fields = {
        "ingredient_id",
        "quantity"
    }

    if required_fields - set(data.keys()):
        raise ValueError(
            "ingredient_id ve quantity alanları zorunludur."
        )

    ingredient_id = data["ingredient_id"]

    if (
        isinstance(ingredient_id, bool)
        or not isinstance(ingredient_id, int)
        or ingredient_id <= 0
    ):
        raise ValueError("Geçerli bir ingredient_id gönderilmelidir.")

    quantity = validate_quantity(data["quantity"])

    unit = data.get("unit")

    if unit is not None:
        if not isinstance(unit, str):
            raise ValueError("Malzeme birimi metin formatında olmalıdır.")

        unit = unit.strip()

        if not unit:
            unit = None

        elif len(unit) > 50:
            raise ValueError(
                "Malzeme birimi en fazla 50 karakter olabilir."
            )

    return {
        "ingredient_id": ingredient_id,
        "quantity": quantity,
        "unit": unit
    }


def validate_update_cart_item_data(data):
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek verisi.")

    if not data:
        raise ValueError("İstek verisi boş olamaz.")

    if set(data.keys()) != {"quantity"}:
        raise ValueError(
            "Yalnızca quantity alanı gönderilebilir."
        )

    return {
        "quantity": validate_quantity(data["quantity"])
    }


def validate_quantity(value):
    if isinstance(value, bool):
        raise ValueError("Malzeme miktarı sayısal olmalıdır.")

    try:
        quantity = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Malzeme miktarı sayısal olmalıdır.")

    if not quantity.is_finite():
        raise ValueError("Malzeme miktarı sonlu bir sayı olmalıdır.")

    if quantity <= 0:
        raise ValueError("Malzeme miktarı sıfırdan büyük olmalıdır.")

    if quantity.as_tuple().exponent < -2:
        raise ValueError(
            "Malzeme miktarı en fazla iki ondalık basamak içerebilir."
        )

    if quantity >= Decimal("100000000"):
        raise ValueError("Malzeme miktarı izin verilen sınırı aşıyor.")

    return quantity