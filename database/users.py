import sqlite3
import bcrypt
from pathlib import Path
import pandas as pd

# ==========================================================
# DATABASE PATH
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "users.db"

# ==========================================================
# CONNECTION
# ==========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)

# ==========================================================
# CREATE TABLE
# ==========================================================

def create_users_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        password BLOB NOT NULL,

        fullname TEXT NOT NULL,

        role TEXT NOT NULL,

        email TEXT,

        status TEXT DEFAULT 'Active',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        last_login TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()

# ==========================================================
# ADD USER
# ==========================================================

def add_user(username, password, fullname, role, email):

    conn = get_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:

        cursor.execute("""
            INSERT INTO users(
                username,
                password,
                fullname,
                role,
                email
            )
            VALUES(?,?,?,?,?)
        """, (
            username,
            hashed,
            fullname,
            role,
            email
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()

# ==========================================================
# GET USERS
# ==========================================================

def get_users():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            username,
            fullname,
            role,
            email,
            status,
            created_at,
            last_login
        FROM users
        ORDER BY fullname
    """, conn)

    conn.close()

    return df

# ==========================================================
# GET USER
# ==========================================================

def get_user(user_id):

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM users
        WHERE id=?
    """, conn, params=(user_id,))

    conn.close()

    return df

# ==========================================================
# UPDATE USER
# ==========================================================

def update_user(user_id, fullname, role, email):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET
            fullname=?,
            role=?,
            email=?
        WHERE id=?
    """, (
        fullname,
        role,
        email,
        user_id
    ))

    conn.commit()
    conn.close()

# ==========================================================
# UPDATE STATUS
# ==========================================================

def update_status(user_id, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET status=?
        WHERE id=?
    """, (
        status,
        user_id
    ))

    conn.commit()
    conn.close()

# ==========================================================
# ENABLE USER
# ==========================================================

def enable_user(user_id):

    update_status(user_id, "Active")

# ==========================================================
# DISABLE USER
# ==========================================================

def disable_user(user_id):

    update_status(user_id, "Disabled")

# ==========================================================
# RESET PASSWORD
# ==========================================================

def reset_password(user_id, new_password):

    conn = get_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    )

    cursor.execute("""
        UPDATE users
        SET password=?
        WHERE id=?
    """, (
        hashed,
        user_id
    ))

    conn.commit()
    conn.close()

# ==========================================================
# DELETE USER
# ==========================================================

def delete_user(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM users
        WHERE id=?
    """, (user_id,))

    conn.commit()
    conn.close()

# ==========================================================
# TOTAL USERS
# ==========================================================

def total_users():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total

# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

create_users_table()

# ==========================================================
# CREATE DEFAULT USERS
# ==========================================================

DEFAULT_USERS = [

    ("admin", "admin123", "System Administrator", "Administrator", "admin@plant.com"),

    ("maintenance", "maint123", "Maintenance Engineer", "Maintenance Engineer", "maintenance@plant.com"),

    ("operations", "ops123", "Operations Engineer", "Operations Engineer", "operations@plant.com"),

    ("supervisor", "super123", "Plant Supervisor", "Supervisor", "supervisor@plant.com"),

    ("guest", "guest123", "Guest User", "Guest", "guest@plant.com"),
]

for user in DEFAULT_USERS:
    add_user(*user)