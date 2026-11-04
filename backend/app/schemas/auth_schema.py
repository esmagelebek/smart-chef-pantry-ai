
import re


def validate_register_data(data):
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek verisi.")

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not all([first_name, last_name, email, password]):
        raise ValueError("Ad, soyad, e-posta ve şifre alanları zorunludur.")

    if not all(isinstance(value, str) for value in [first_name, last_name, email, password]):
        raise ValueError("Tüm alanlar metin formatında olmalıdır.")

    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip().lower()

    if not first_name or not last_name:
        raise ValueError("Ad ve soyad boş bırakılamaz.")

    if len(first_name) > 100 or len(last_name) > 100:
        raise ValueError("Ad ve soyad en fazla 100 karakter olabilir.")

    if len(email) > 255 or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Geçerli bir e-posta adresi giriniz.")

    if len(password) < 8:
        raise ValueError("Şifre en az 8 karakter olmalıdır.")

    if len(password) > 128:
        raise ValueError("Şifre en fazla 128 karakter olabilir.")

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }


def validate_login_data(data):
    if not isinstance(data, dict):
        raise ValueError("Geçersiz istek verisi.")

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise ValueError("E-posta ve şifre alanları zorunludur.")

    if not isinstance(email, str) or not isinstance(password, str):
        raise ValueError("E-posta ve şifre metin formatında olmalıdır.")

    email = email.strip().lower()

    if not email or len(email) > 255:
        raise ValueError("Geçerli bir e-posta adresi giriniz.")

    if not password or len(password) > 128:
        raise ValueError("Geçerli bir şifre giriniz.")

    return {
        "email": email,
        "password": password
    }
