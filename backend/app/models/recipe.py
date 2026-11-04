from datetime import datetime, timezone

from app.extensions import db


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    instructions = db.Column(db.Text, nullable=False)

    preparation_time = db.Column(db.Integer, nullable=True)
    cooking_time = db.Column(db.Integer, nullable=True)

    servings = db.Column(db.Integer, nullable=False, default=1)

    difficulty = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)

    source_url = db.Column(db.String(500), nullable=True)
    youtube_url = db.Column(db.String(500), nullable=True)

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

    def __repr__(self):
        return f"<Recipe {self.title}>"