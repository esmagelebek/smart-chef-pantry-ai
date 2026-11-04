from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    """Kullanıcının şifresini güvenli biçimde hashler."""
    return generate_password_hash(password, method="scrypt")


def verify_password(password: str, password_hash: str) -> bool:
    """Girilen şifrenin kayıtlı hash ile eşleşmesini kontrol eder."""
    return check_password_hash(password_hash, password)