from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.favorite_service import (
    add_favorite,
    get_user_favorites,
    remove_favorite,
    FavoriteAlreadyExistsError,
    RecipeNotFoundError,
    FavoriteNotFoundError
)


favorite_bp = Blueprint(
    "favorites",
    __name__,
    url_prefix="/api/favorites"
)


def favorite_to_dict(favorite):
    return {
        "id": favorite.id,
        "recipe_id": favorite.recipe_id,
        "recipe": {
            "id": favorite.recipe.id,
            "title": favorite.recipe.title,
            "description": favorite.recipe.description,
            "image_url": favorite.recipe.image_url,
            "preparation_time": favorite.recipe.preparation_time,
            "cooking_time": favorite.recipe.cooking_time,
            "difficulty": favorite.recipe.difficulty
        },
        "created_at": favorite.created_at.isoformat()
    }


@favorite_bp.get("/")
@jwt_required()
def list_favorites():
    user_id = int(get_jwt_identity())

    favorites = get_user_favorites(user_id)

    return jsonify({
        "success": True,
        "count": len(favorites),
        "favorites": [
            favorite_to_dict(favorite)
            for favorite in favorites
        ]
    }), 200


@favorite_bp.post("/<int:recipe_id>")
@jwt_required()
def create_favorite(recipe_id):
    user_id = int(get_jwt_identity())

    try:
        favorite = add_favorite(user_id, recipe_id)

        return jsonify({
            "success": True,
            "message": "Tarif favorilere eklendi.",
            "favorite": favorite_to_dict(favorite)
        }), 201

    except RecipeNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 404

    except FavoriteAlreadyExistsError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Tarif favorilere eklenirken sunucu hatası oluştu."
        }), 500


@favorite_bp.delete("/<int:recipe_id>")
@jwt_required()
def delete_favorite(recipe_id):
    user_id = int(get_jwt_identity())

    try:
        remove_favorite(user_id, recipe_id)

        return jsonify({
            "success": True,
            "message": "Tarif favorilerden kaldırıldı."
        }), 200

    except FavoriteNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 404

    except Exception:
        return jsonify({
            "success": False,
            "message": "Tarif favorilerden kaldırılırken sunucu hatası oluştu."
        }), 500