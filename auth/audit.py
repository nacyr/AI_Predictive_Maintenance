import sqlite3
from pathlib import Path
from datetime import datetime

# ==========================================================
# DATABASE
# ==========================================================

DB_PATH = (
    Path(__file__).resolve().parent
    / "users.db"
)

# ==========================================================
# CONNECTION
# ==========================================================

def get_connection():

    return sqlite3.connect(DB_PATH)

# ==========================================================
# CREATE TABLE
# ==========================================================

def create_audit_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT,

            action TEXT,

            details TEXT,

            timestamp TEXT

        )
    """)

    conn.commit()
    conn.close()

# ==========================================================
# ADD LOG
# ==========================================================

def add_log(
    username,
    action,
    details
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_logs(
            username,
            action,
            details,
            timestamp
        )

        VALUES(?,?,?,?)
        """,
        (
            username,
            action,
            details,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()
    conn.close()

# ==========================================================
# INITIALIZE
# ==========================================================

create_audit_table()