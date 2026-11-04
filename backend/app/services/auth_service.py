
from app.extensions import db
from app.models.user import User
from app.utils.security import hash_password, verify_password


class DuplicateEmailError(ValueError):
    """Kayıt sırasında kullanılan e-posta adresi zaten mevcut."""
    pass


def register_user(first_name, last_name, email, password):
    email = email.strip().lower()

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        raise DuplicateEmailError("Bu e-posta adresi zaten kayıtlı.")

    user = User(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email,
        password_hash=hash_password(password)
    )

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return user


def authenticate_user(email, password):
    email = email.strip().lower()

    user = User.query.filter_by(email=email).first()

    if not user or not verify_password(password, user.password_hash):
        return None

    return user
