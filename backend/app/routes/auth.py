
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from app.schemas.auth_schema import (
    validate_login_data,
    validate_register_data
)

from app.services.auth_service import (
    authenticate_user,
    register_user,
    DuplicateEmailError
)


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    try:
        data = validate_register_data(request.get_json(silent=True))

        user = register_user(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"]
        )

        return jsonify({
            "success": True,
            "message": "Kullanıcı başarıyla kaydedildi.",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        }), 201

    except DuplicateEmailError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 409

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Kayıt sırasında bir sunucu hatası oluştu."
        }), 500


@auth_bp.post("/login")
def login():
    try:
        data = validate_login_data(request.get_json(silent=True))

        user = authenticate_user(
            email=data["email"],
            password=data["password"]
        )

        if not user:
            return jsonify({
                "success": False,
                "message": "E-posta veya şifre hatalı."
            }), 401

        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "success": True,
            "message": "Giriş başarılı.",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        }), 200

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception:
        return jsonify({
            "success": False,
            "message": "Giriş sırasında bir sunucu hatası oluştu."
        }), 500


@auth_bp.get("/me")
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({
            "success": False,
            "message": "Kullanıcı bulunamadı."
        }), 404

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email
        }
    }), 200
