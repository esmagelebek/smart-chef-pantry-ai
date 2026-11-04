
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from app.schemas.ingredient_schema import validate_ingredient_data
from app.services.ingredient_service import (
    create_ingredient,
    get_all_ingredients,
    get_ingredient_by_id,
    update_ingredient,
    delete_ingredient
)


ingredient_bp = Blueprint(
    "ingredients",
    __name__,
    url_prefix="/api/ingredients"
)


def ingredient_to_dict(ingredient):
    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "category": ingredient.category,
        "unit": ingredient.unit,
        "image_url": ingredient.image_url,
        "created_at": ingredient.created_at.isoformat()
    }


@ingredient_bp.post("/")
@jwt_required()
def create():
    try:
        data = validate_ingredient_data(request.get_json(silent=True))
        ingredient = create_ingredient(data)

        return jsonify({
            "success": True,
            "message": "Malzeme başarıyla eklendi.",
            "ingredient": ingredient_to_dict(ingredient)
        }), 201

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Bu malzeme zaten kayıtlı veya ilişkili bir veri kısıtlaması oluştu."
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Malzeme eklenirken sunucu hatası oluştu."
        }), 500


@ingredient_bp.get("/")
def list_ingredients():
    ingredients = get_all_ingredients()

    return jsonify({
        "success": True,
        "count": len(ingredients),
        "ingredients": [
            ingredient_to_dict(ingredient)
            for ingredient in ingredients
        ]
    }), 200


@ingredient_bp.get("/<int:ingredient_id>")
def get_detail(ingredient_id):
    ingredient = get_ingredient_by_id(ingredient_id)

    if not ingredient:
        return jsonify({
            "success": False,
            "message": "Malzeme bulunamadı."
        }), 404

    return jsonify({
        "success": True,
        "ingredient": ingredient_to_dict(ingredient)
    }), 200


@ingredient_bp.put("/<int:ingredient_id>")
@jwt_required()
def update(ingredient_id):
    try:
        data = validate_ingredient_data(
            request.get_json(silent=True),
            partial=True
        )

        ingredient = get_ingredient_by_id(ingredient_id)

        if not ingredient:
            return jsonify({
                "success": False,
                "message": "Malzeme bulunamadı."
            }), 404

        ingredient = update_ingredient(ingredient, data)

        return jsonify({
            "success": True,
            "message": "Malzeme başarıyla güncellendi.",
            "ingredient": ingredient_to_dict(ingredient)
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Malzeme güncellenemedi. Veritabanı kısıtlaması oluştu."
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Malzeme güncellenirken sunucu hatası oluştu."
        }), 500


@ingredient_bp.delete("/<int:ingredient_id>")
@jwt_required()
def delete(ingredient_id):
    ingredient = get_ingredient_by_id(ingredient_id)

    if not ingredient:
        return jsonify({
            "success": False,
            "message": "Malzeme bulunamadı."
        }), 404

    try:
        delete_ingredient(ingredient)

        return jsonify({
            "success": True,
            "message": "Malzeme başarıyla silindi."
        }), 200

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Bu malzeme başka kayıtlar tarafından kullanıldığı için silinemez."
        }), 409

    except Exception:
        return jsonify({
            "success": False,
            "message": "Malzeme silinirken sunucu hatası oluştu."
        }), 500
