
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from app.schemas.recipe_schema import validate_recipe_data

from app.services.recipe_service import (
    create_recipe,
    get_all_recipes,
    get_recipe_by_id,
    update_recipe,
    delete_recipe,
    RecipeIngredientNotFoundError
)


recipe_bp = Blueprint(
    "recipes",
    __name__,
    url_prefix="/api/recipes"
)


def recipe_to_dict(recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "instructions": recipe.instructions,
        "preparation_time": recipe.preparation_time,
        "cooking_time": recipe.cooking_time,
        "servings": recipe.servings,
        "difficulty": recipe.difficulty,
        "image_url": recipe.image_url,
        "source_url": recipe.source_url,
        "youtube_url": recipe.youtube_url,
        "ingredients": [
            {
                "ingredient_id": item.ingredient_id,
                "ingredient_name": item.ingredient.name,
                "quantity": (
                    float(item.quantity)
                    if item.quantity is not None
                    else None
                ),
                "unit": item.unit
            }
            for item in recipe.recipe_ingredients
        ],
        "created_at": recipe.created_at.isoformat(),
        "updated_at": recipe.updated_at.isoformat()
    }


@recipe_bp.post("/")
@jwt_required()
def create():
    try:
        data = validate_recipe_data(request.get_json(silent=True))
        recipe = create_recipe(data)

        return jsonify({
            "success": True,
            "message": "Tarif başarıyla eklendi.",
            "recipe": recipe_to_dict(recipe)
        }), 201

    except RecipeIngredientNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Veritabanı kısıtlaması nedeniyle tarif eklenemedi."
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Tarif eklenirken sunucu hatası oluştu."
        }), 500


@recipe_bp.get("/")
def list_recipes():
    recipes = get_all_recipes()

    return jsonify({
        "success": True,
        "count": len(recipes),
        "recipes": [
            recipe_to_dict(recipe)
            for recipe in recipes
        ]
    }), 200


@recipe_bp.get("/<int:recipe_id>")
def get_detail(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        return jsonify({
            "success": False,
            "message": "Tarif bulunamadı."
        }), 404

    return jsonify({
        "success": True,
        "recipe": recipe_to_dict(recipe)
    }), 200


@recipe_bp.put("/<int:recipe_id>")
@jwt_required()
def update(recipe_id):
    try:
        data = validate_recipe_data(
            request.get_json(silent=True),
            partial=True
        )

        recipe = get_recipe_by_id(recipe_id)

        if not recipe:
            return jsonify({
                "success": False,
                "message": "Tarif bulunamadı."
            }), 404

        recipe = update_recipe(recipe, data)

        return jsonify({
            "success": True,
            "message": "Tarif başarıyla güncellendi.",
            "recipe": recipe_to_dict(recipe)
        }), 200

    except RecipeIngredientNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Veritabanı kısıtlaması nedeniyle tarif güncellenemedi."
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Tarif güncellenirken sunucu hatası oluştu."
        }), 500


@recipe_bp.delete("/<int:recipe_id>")
@jwt_required()
def delete(recipe_id):
    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        return jsonify({
            "success": False,
            "message": "Tarif bulunamadı."
        }), 404

    try:
        delete_recipe(recipe)

        return jsonify({
            "success": True,
            "message": "Tarif başarıyla silindi."
        }), 200

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Tarif silinirken veritabanı kısıtlaması oluştu."
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Tarif silinirken sunucu hatası oluştu."
        }), 500
