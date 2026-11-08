from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.schemas.cart_schema import (
    validate_add_cart_item_data,
    validate_update_cart_item_data
)

from app.services.cart_service import (
    add_item_to_cart,
    get_user_cart,
    update_cart_item,
    remove_cart_item,
    clear_user_cart,
    IngredientNotFoundError,
    CartItemNotFoundError,
    CartUnitMismatchError
)


cart_bp = Blueprint(
    "cart",
    __name__,
    url_prefix="/api/cart"
)


def cart_item_to_dict(cart_item):
    return {
        "id": cart_item.id,
        "ingredient_id": cart_item.ingredient_id,
        "ingredient": {
            "id": cart_item.ingredient.id,
            "name": cart_item.ingredient.name,
            "category": cart_item.ingredient.category,
            "unit": cart_item.ingredient.unit
        },
        "quantity": float(cart_item.quantity),
        "unit": cart_item.unit
    }


def cart_to_dict(cart):
    items = [
        cart_item_to_dict(item)
        for item in cart.items
    ]

    return {
        "id": cart.id,
        "items": items,
        "item_count": len(items),
        "created_at": cart.created_at.isoformat(),
        "updated_at": cart.updated_at.isoformat()
    }


@cart_bp.get("/")
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())

    try:
        cart = get_user_cart(user_id)

        if not cart:
            return jsonify({
                "success": True,
                "cart": {
                    "items": [],
                    "item_count": 0
                }
            }), 200

        return jsonify({
            "success": True,
            "cart": cart_to_dict(cart)
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Sepet görüntülenirken sunucu hatası oluştu."
        }), 500


@cart_bp.post("/items")
@jwt_required()
def create_cart_item():
    user_id = int(get_jwt_identity())

    try:
        data = validate_add_cart_item_data(request.get_json())

        cart_item, created = add_item_to_cart(
            user_id=user_id,
            ingredient_id=data["ingredient_id"],
            quantity=data["quantity"],
            unit=data["unit"]
        )

        return jsonify({
            "success": True,
            "message": (
                "Malzeme sepete eklendi."
                if created
                else "Malzeme miktarı sepette güncellendi."
            ),
            "cart_item": cart_item_to_dict(cart_item)
        }), 201 if created else 200

    except IngredientNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 404

    except CartUnitMismatchError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Malzeme sepete eklenirken sunucu hatası oluştu."
        }), 500


@cart_bp.put("/items/<int:item_id>")
@jwt_required()
def edit_cart_item(item_id):
    user_id = int(get_jwt_identity())

    try:
        data = validate_update_cart_item_data(request.get_json())

        cart_item = update_cart_item(
            user_id=user_id,
            item_id=item_id,
            quantity=data["quantity"]
        )

        return jsonify({
            "success": True,
            "message": "Sepet malzemesi güncellendi.",
            "cart_item": cart_item_to_dict(cart_item)
        }), 200

    except CartItemNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 404

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Sepet malzemesi güncellenirken sunucu hatası oluştu."
        }), 500


@cart_bp.delete("/items/<int:item_id>")
@jwt_required()
def delete_cart_item(item_id):
    user_id = int(get_jwt_identity())

    try:
        remove_cart_item(user_id, item_id)

        return jsonify({
            "success": True,
            "message": "Malzeme sepetten kaldırıldı."
        }), 200

    except CartItemNotFoundError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 404

    except Exception:
        return jsonify({
            "success": False,
            "message": "Malzeme sepetten kaldırılırken sunucu hatası oluştu."
        }), 500


@cart_bp.delete("/")
@jwt_required()
def delete_cart():
    user_id = int(get_jwt_identity())

    try:
        clear_user_cart(user_id)

        return jsonify({
            "success": True,
            "message": "Sepet temizlendi."
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Sepet temizlenirken sunucu hatası oluştu."
        }), 500