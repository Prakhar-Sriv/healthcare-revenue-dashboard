from auth.db import get_connection
from auth.security import hash_password

def create_user(username, email, password, role, two_factor=False):

    conn = get_connection()
    cursor = conn.cursor()

    hashed = hash_password(password)

    cursor.execute(
        """
        INSERT INTO users (username,email,password_hash,role,two_factor_enabled)
        VALUES (?,?,?,?,?)
        """,
        (username, email, hashed, role, int(two_factor))
    )

    conn.commit()
    conn.close()