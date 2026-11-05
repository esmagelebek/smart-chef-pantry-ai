from flask import Flask, jsonify
from app.routes.favorite import favorite_bp
from app.config import Config
from app.extensions import cors, db, jwt, migrate
from app import models
from app.routes.recipe import recipe_bp

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": "*"}}
    )

    @app.get("/api/health")
    def health_check():
        return jsonify({
            "success": True,
            "message": "Smart Chef & Pantry AI API is running."
        }), 200
    from app.routes.auth import auth_bp
    from app.routes.ingredient import ingredient_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ingredient_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(favorite_bp)

    return app