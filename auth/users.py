import bcrypt
from database.users import get_connection


def verify_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, password, fullname, role, status
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    if user[5] != "Active":
        return None

    if bcrypt.checkpw(password.encode(), user[2]):

        return {
            "id": user[0],
            "username": user[1],
            "fullname": user[3],
            "role": user[4]
        }

    return None