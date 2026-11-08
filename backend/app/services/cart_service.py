from app.extensions import db
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.ingredient import Ingredient


class IngredientNotFoundError(ValueError):
    """Sepete eklenmek istenen malzeme bulunamadı."""
    pass


class CartItemNotFoundError(ValueError):
    """Sepette böyle bir malzeme bulunamadı."""
    pass


class CartUnitMismatchError(ValueError):
    """Mevcut ve yeni malzemenin birimleri uyuşmuyor."""
    pass


class InvalidCartQuantityError(ValueError):
    """Sepet miktarı geçersiz."""
    pass


def get_or_create_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()

    if cart:
        return cart

    cart = Cart(user_id=user_id)

    try:
        db.session.add(cart)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return cart
def add_item_to_cart(user_id, ingredient_id, quantity, unit=None):
    if quantity <= 0:
        raise InvalidCartQuantityError(
            "Malzeme miktarı sıfırdan büyük olmalıdır."
        )

    ingredient = db.session.get(Ingredient, ingredient_id)

    if not ingredient:
        raise IngredientNotFoundError("Malzeme bulunamadı.")

    ingredient_unit = ingredient.unit

    if ingredient_unit != unit:
        raise CartUnitMismatchError(
            f"Bu malzemenin birimi '{ingredient_unit}' olmalıdır."
        )

    try:
        cart = get_or_create_cart(user_id)

        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            ingredient_id=ingredient_id
        ).first()

        if existing_item:
            existing_item.quantity += quantity

            db.session.commit()

            return existing_item, False

        cart_item = CartItem(
            cart_id=cart.id,
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit
        )

        db.session.add(cart_item)
        db.session.commit()

        return cart_item, True

    except Exception:
        db.session.rollback()
        raise
def get_user_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        return None

    return cart
def update_cart_item(user_id, item_id, quantity):
    if quantity <= 0:
        raise InvalidCartQuantityError(
            "Malzeme miktarı sıfırdan büyük olmalıdır."
        )

    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        raise CartItemNotFoundError(
            "Sepet bulunamadı."
        )

    cart_item = CartItem.query.filter_by(
        id=item_id,
        cart_id=cart.id
    ).first()

    if not cart_item:
        raise CartItemNotFoundError(
            "Bu malzeme sepetinizde bulunamadı."
        )

    try:
        cart_item.quantity = quantity
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return cart_item
def remove_cart_item(user_id, item_id):
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        raise CartItemNotFoundError(
            "Sepet bulunamadı."
        )

    cart_item = CartItem.query.filter_by(
        id=item_id,
        cart_id=cart.id
    ).first()

    if not cart_item:
        raise CartItemNotFoundError(
            "Bu malzeme sepetinizde bulunamadı."
        )

    try:
        db.session.delete(cart_item)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
def clear_user_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()

    if not cart:
        return False

    try:
        CartItem.query.filter_by(
            cart_id=cart.id
        ).delete(synchronize_session=False)

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return True