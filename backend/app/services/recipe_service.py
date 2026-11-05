
from app.extensions import db
from app.models.recipe import Recipe
from app.models.recipe_ingredient import RecipeIngredient
from app.models.ingredient import Ingredient


class RecipeIngredientNotFoundError(ValueError):
    """Tarifte kullanılan malzemelerden biri bulunamadı."""
    pass


def _set_recipe_ingredients(recipe, ingredients):
    ingredient_ids = [
        item["ingredient_id"]
        for item in ingredients
    ]

    existing_ids = {
        ingredient.id
        for ingredient in Ingredient.query.filter(
            Ingredient.id.in_(ingredient_ids)
        ).all()
    }

    missing_ids = set(ingredient_ids) - existing_ids

    if missing_ids:
        raise RecipeIngredientNotFoundError(
            f"Bulunamayan malzeme ID'leri: {sorted(missing_ids)}"
        )

    recipe.recipe_ingredients.clear()

    for item in ingredients:
        recipe_ingredient = RecipeIngredient(
            ingredient_id=item["ingredient_id"],
            quantity=item.get("quantity"),
            unit=item.get("unit")
        )

        recipe.recipe_ingredients.append(recipe_ingredient)


def create_recipe(data):
    recipe = Recipe(
        title=data["title"],
        description=data.get("description"),
        instructions=data["instructions"],
        preparation_time=data.get("preparation_time"),
        cooking_time=data.get("cooking_time"),
        servings=data.get("servings", 1),
        difficulty=data.get("difficulty"),
        image_url=data.get("image_url"),
        source_url=data.get("source_url"),
        youtube_url=data.get("youtube_url")
    )

    try:
        db.session.add(recipe)
        db.session.flush()

        if "ingredients" in data:
            _set_recipe_ingredients(recipe, data["ingredients"])

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return recipe


def get_all_recipes():
    return Recipe.query.order_by(Recipe.created_at.desc()).all()


def get_recipe_by_id(recipe_id):
    return db.session.get(Recipe, recipe_id)


def update_recipe(recipe, data):
    updatable_fields = [
        "title",
        "description",
        "instructions",
        "preparation_time",
        "cooking_time",
        "servings",
        "difficulty",
        "image_url",
        "source_url",
        "youtube_url"
    ]

    try:
        for field in updatable_fields:
            if field in data:
                setattr(recipe, field, data[field])

        if "ingredients" in data:
            _set_recipe_ingredients(recipe, data["ingredients"])

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return recipe


def delete_recipe(recipe):
    try:
        db.session.delete(recipe)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
