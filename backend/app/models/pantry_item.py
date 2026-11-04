from datetime import datetime, timezone

from app.extensions import db


class PantryItem(db.Model):
    __tablename__ = "pantry_items"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False
    )

    quantity = db.Column(db.Numeric(10, 2), nullable=False)

    unit = db.Column(db.String(50), nullable=True)

    expiration_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = db.relationship("User")
    ingredient = db.relationship("Ingredient")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "ingredient_id",
            name="uq_user_pantry_ingredient"
        ),
    )

    def __repr__(self):
        return (
            f"<PantryItem user_id={self.user_id}, "
            f"ingredient_id={self.ingredient_id}>"
        )