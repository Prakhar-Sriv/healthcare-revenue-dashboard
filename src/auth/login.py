from auth.db import get_connection
from auth.security import verify_password


def authenticate_user(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username, email, role, password_hash, two_factor_enabled
        FROM users
        WHERE username=?
        """,
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "two_factor_enabled": user["two_factor_enabled"]
    }