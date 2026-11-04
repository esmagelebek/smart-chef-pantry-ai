from app.extensions import db


class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"

    id = db.Column(db.Integer, primary_key=True)

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False
    )

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False
    )

    quantity = db.Column(db.Numeric(10, 2), nullable=True)

    unit = db.Column(db.String(50), nullable=True)

    recipe = db.relationship(
        "Recipe",
        backref=db.backref("recipe_ingredients", cascade="all, delete-orphan")
    )

    ingredient = db.relationship("Ingredient")

    __table_args__ = (
        db.UniqueConstraint(
            "recipe_id",
            "ingredient_id",
            name="uq_recipe_ingredient"
        ),
    )

    def __repr__(self):
        return (
            f"<RecipeIngredient "
            f"recipe_id={self.recipe_id}, "
            f"ingredient_id={self.ingredient_id}>"
        )