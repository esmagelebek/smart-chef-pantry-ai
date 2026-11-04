from datetime import datetime, timezone

from app.extensions import db


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True
    )

    category = db.Column(db.String(100), nullable=True)

    unit = db.Column(db.String(50), nullable=True)

    image_url = db.Column(db.String(500), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<Ingredient {self.name}>"