
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.favorite import Favorite
from app.models.recipe import Recipe


class FavoriteAlreadyExistsError(ValueError):
    """Tarif zaten kullanıcının favorilerinde."""
    pass


class RecipeNotFoundError(ValueError):
    """Favoriye eklenmek istenen tarif bulunamadı."""
    pass


class FavoriteNotFoundError(ValueError):
    """Kullanıcının favorilerinde böyle bir kayıt bulunamadı."""
    pass


def add_favorite(user_id, recipe_id):
    recipe = db.session.get(Recipe, recipe_id)

    if not recipe:
        raise RecipeNotFoundError("Tarif bulunamadı.")

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id,
        recipe_id=recipe_id
    ).first()

    if existing_favorite:
        raise FavoriteAlreadyExistsError(
            "Bu tarif zaten favorilerinizde."
        )

    favorite = Favorite(
        user_id=user_id,
        recipe_id=recipe_id
    )

    try:
        db.session.add(favorite)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        raise FavoriteAlreadyExistsError(
            "Bu tarif zaten favorilerinizde."
        )

    except Exception:
        db.session.rollback()
        raise

    return favorite


def get_user_favorites(user_id):
    return (
        Favorite.query
        .filter_by(user_id=user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


def remove_favorite(user_id, recipe_id):
    favorite = Favorite.query.filter_by(
        user_id=user_id,
        recipe_id=recipe_id
    ).first()

    if not favorite:
        raise FavoriteNotFoundError(
            "Bu tarif favorilerinizde bulunamadı."
        )

    try:
        db.session.delete(favorite)
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise
