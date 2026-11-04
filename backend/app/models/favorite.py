from datetime import datetime, timezone

from app.extensions import db


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship("User")
    recipe = db.relationship("Recipe")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "recipe_id",
            name="uq_user_favorite_recipe"
        ),
    )

    def __repr__(self):
        return (
            f"<Favorite user_id={self.user_id}, "
            f"recipe_id={self.recipe_id}>"
        )