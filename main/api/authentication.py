from hashlib import pbkdf2_hmac
from hmac import compare_digest
from uuid import UUID
from urllib.parse import unquote

from django.db import connections
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed


def get_admin_id(request):
    fullname = request.COOKIES.get("fullname")
    key = request.COOKIES.get("key")
    uuid = request.COOKIES.get("uuid")
    if not all(isinstance(value, str) and value for value in (fullname, key, uuid)):
        raise AuthenticationFailed("Необходимы cookies fullname, key и uuid.")

    try:
        fullname = unquote(fullname, encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
        raise AuthenticationFailed("Неверный формат fullname.") from None

    with connections["user_info"].cursor() as cursor:
        cursor.execute(
            "SELECT id, uuid, hashed_password, salt FROM users WHERE username = %s",
            [fullname],
        )
        rows = cursor.fetchmany(2)
    if len(rows) != 1:
        raise AuthenticationFailed("Неверные данные пользователя.")

    admin_id, stored_uuid, hashed_password, salt = rows[0]
    try:
        uuid_matches = UUID(str(stored_uuid)) == UUID(uuid)
        expected_key = pbkdf2_hmac(
            "sha256", hashed_password.encode("utf-8"), bytes.fromhex(salt), 100000
        ).hex()
        key_matches = compare_digest(expected_key.encode("utf-8"), key.encode("utf-8"))
    except (ValueError, TypeError, AttributeError):
        raise AuthenticationFailed("Неверные данные пользователя.") from None
    if not uuid_matches or not key_matches:
        raise AuthenticationFailed("Неверные данные пользователя.")

    SessionAuthentication().enforce_csrf(request)
    return admin_id
