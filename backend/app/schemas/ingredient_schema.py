
def validate_ingredient_data(data, partial=False):
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek verisi.")

    allowed_fields = {"name", "category", "unit", "image_url"}

    if not data:
        raise ValueError("En az bir alan gönderilmelidir.")

    unknown_fields = set(data.keys()) - allowed_fields

    if unknown_fields:
        raise ValueError("Geçersiz alan gönderildi.")

    if not partial and "name" not in data:
        raise ValueError("Malzeme adı zorunludur.")

    validated_data = {}

    if "name" in data:
        name = data["name"]

        if not isinstance(name, str):
            raise ValueError("Malzeme adı metin formatında olmalıdır.")

        name = name.strip()

        if not name:
            raise ValueError("Malzeme adı boş bırakılamaz.")

        if len(name) > 150:
            raise ValueError("Malzeme adı en fazla 150 karakter olabilir.")

        validated_data["name"] = name

    for field, max_length in [
        ("category", 100),
        ("unit", 50),
        ("image_url", 500)
    ]:
        if field in data:
            value = data[field]

            if value is not None and not isinstance(value, str):
                raise ValueError(f"{field} metin formatında olmalıdır.")

            if value is not None:
                value = value.strip()

                if not value:
                    value = None

                elif len(value) > max_length:
                    raise ValueError(
                        f"{field} en fazla {max_length} karakter olabilir."
                    )

            validated_data[field] = value

    return validated_data
