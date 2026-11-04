
from sqlalchemy import func

from app.extensions import db
from app.models.ingredient import Ingredient


class DuplicateIngredientError(ValueError):
    """Malzeme adı başka bir kayıtta zaten mevcut."""
    pass


def create_ingredient(data):
    normalized_name = data["name"].strip()

    existing_ingredient = Ingredient.query.filter(
        func.lower(Ingredient.name) == normalized_name.lower()
    ).first()

    if existing_ingredient:
        raise DuplicateIngredientError("Bu malzeme zaten kayıtlı.")

    ingredient = Ingredient(
        name=normalized_name,
        category=data.get("category"),
        unit=data.get("unit"),
        image_url=data.get("image_url")
    )

    try:
        db.session.add(ingredient)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return ingredient


def get_all_ingredients():
    return Ingredient.query.order_by(Ingredient.name.asc()).all()


def get_ingredient_by_id(ingredient_id):
    return db.session.get(Ingredient, ingredient_id)


def update_ingredient(ingredient, data):
    if "name" in data:
        normalized_name = data["name"].strip()

        existing_ingredient = Ingredient.query.filter(
            func.lower(Ingredient.name) == normalized_name.lower(),
            Ingredient.id != ingredient.id
        ).first()

        if existing_ingredient:
            raise DuplicateIngredientError(
                "Bu malzeme adı başka bir kayıtta kullanılıyor."
            )

        ingredient.name = normalized_name

    if "category" in data:
        ingredient.category = data["category"]

    if "unit" in data:
        ingredient.unit = data["unit"]

    if "image_url" in data:
        ingredient.image_url = data["image_url"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return ingredient


def delete_ingredient(ingredient):
    try:
        db.session.delete(ingredient)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
