from app.extensions import db


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)

    cart_id = db.Column(
        db.Integer,
        db.ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False
    )

    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=1)

    unit = db.Column(db.String(50), nullable=True)

    cart = db.relationship("Cart", back_populates="items")
    ingredient = db.relationship("Ingredient")

    __table_args__ = (
        db.UniqueConstraint(
            "cart_id",
            "ingredient_id",
            name="uq_cart_ingredient"
        ),
    )

    def __repr__(self):
        return (
            f"<CartItem cart_id={self.cart_id}, "
            f"ingredient_id={self.ingredient_id}>"
        )