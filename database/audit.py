import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd

# ==========================================================
# DATABASE PATH
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "audit.db"

# ==========================================================
# CONNECTION
# ==========================================================

def get_connection():
    return sqlite3.connect(DB_PATH)

# ==========================================================
# CREATE TABLE
# ==========================================================

def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT NOT NULL,

        action TEXT NOT NULL,

        timestamp TEXT NOT NULL

    )
    """)

    conn.commit()
    conn.close()

# ==========================================================
# ADD LOG
# ==========================================================

def add_log(username, action):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_logs(
            username,
            action,
            timestamp
        )
        VALUES(?,?,?)
    """, (

        username,
        action,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ))

    conn.commit()
    conn.close()

# ==========================================================
# GET LOGS
# ==========================================================

def get_logs():

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT
            id,
            username,
            action,
            timestamp

        FROM audit_logs

        ORDER BY id DESC

    """, conn)

    conn.close()

    return df

# ==========================================================
# SEARCH LOGS
# ==========================================================

def search_logs(keyword):

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM audit_logs

        WHERE
            username LIKE ?
            OR action LIKE ?

        ORDER BY id DESC

    """, conn, params=(

        f"%{keyword}%",
        f"%{keyword}%"

    ))

    conn.close()

    return df

# ==========================================================
# DELETE LOG
# ==========================================================

def delete_log(log_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM audit_logs

        WHERE id=?

    """, (log_id,))

    conn.commit()
    conn.close()

# ==========================================================
# CLEAR LOGS
# ==========================================================

def clear_logs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        DELETE FROM audit_logs

    """)

    conn.commit()
    conn.close()

# ==========================================================
# TOTAL LOGS
# ==========================================================

def total_logs():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        SELECT COUNT(*)

        FROM audit_logs

    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total

# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

create_table()