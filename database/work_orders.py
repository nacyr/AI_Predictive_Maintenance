import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# ==========================================================
# DATABASE PATH
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "work_orders.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# INIT DATABASE
# ==========================================================

def create_work_orders_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine TEXT NOT NULL,
            issue TEXT NOT NULL,
            priority TEXT DEFAULT 'MEDIUM',
            status TEXT DEFAULT 'PENDING',
            created_by TEXT,
            assigned_to TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==========================================================
# CREATE WORK ORDER
# ==========================================================

def create_work_order(machine, issue, priority="MEDIUM", created_by="SYSTEM", assigned_to=None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO work_orders (machine, issue, priority, created_by, assigned_to)
        VALUES (?, ?, ?, ?, ?)
    """, (machine, issue, priority, created_by, assigned_to))

    conn.commit()
    conn.close()


# ==========================================================
# UPDATE CORE FUNCTION
# ==========================================================

def update_work_order(work_order_id, **kwargs):

    if not kwargs:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    for k, v in kwargs.items():
        fields.append(f"{k}=?")
        values.append(v)

    fields.append("updated_at=?")
    values.append(datetime.now().isoformat())

    values.append(work_order_id)

    sql = f"""
        UPDATE work_orders
        SET {", ".join(fields)}
        WHERE id=?
    """

    cursor.execute(sql, values)
    conn.commit()
    conn.close()

    return True


# ==========================================================
# STATUS UPDATE (STANDARDIZED)
# ==========================================================

def update_work_order_status(work_order_id, status):
    return update_work_order(work_order_id, status=status)


# ==========================================================
# DELETE WORK ORDER (FIX YOU REQUESTED)
# ==========================================================

def delete_work_order(work_order_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM work_orders
        WHERE id=?
    """, (work_order_id,))

    conn.commit()
    conn.close()


# ==========================================================
# READ ALL WORK ORDERS
# ==========================================================

def get_work_orders():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT * FROM work_orders
        ORDER BY datetime(created_at) DESC
    """, conn)

    conn.close()
    return df


# ==========================================================
# SEARCH BY MACHINE
# ==========================================================

def search_work_orders_by_machine(machine_name):

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT * FROM work_orders
        WHERE machine LIKE ?
        ORDER BY datetime(created_at) DESC
    """, conn, params=(f"%{machine_name}%",))

    conn.close()
    return df


# ==========================================================
# STATISTICS
# ==========================================================

def get_work_order_statistics():

    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    cursor.execute("SELECT COUNT(*) FROM work_orders")
    stats["total"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='PENDING'")
    stats["pending"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='APPROVED'")
    stats["approved"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='IN_PROGRESS'")
    stats["in_progress"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='COMPLETED'")
    stats["completed"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='REJECTED'")
    stats["rejected"] = cursor.fetchone()[0]

    conn.close()
    return stats


# ==========================================================
# ANALYTICS HELPERS
# ==========================================================

def get_machine_failure_frequency():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT machine, COUNT(*) as count
        FROM work_orders
        GROUP BY machine
        ORDER BY count DESC
    """, conn)

    conn.close()
    return df


def get_daily_work_order_trends():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM work_orders
        GROUP BY DATE(created_at)
        ORDER BY date
    """, conn)

    conn.close()
    return df


def get_ai_vs_manual_breakdown():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT created_by, COUNT(*)
        FROM work_orders
        GROUP BY created_by
    """)

    rows = cursor.fetchall()
    conn.close()

    return {
        (r[0] if r[0] else "MANUAL"): r[1]
        for r in rows
    }


# ==========================================================
# AI SAFETY SYSTEM
# ==========================================================

def recent_ai_work_order_exists(machine, issue, minutes_window=30):

    conn = get_connection()
    cursor = conn.cursor()

    time_limit = (
        datetime.now() - timedelta(minutes=minutes_window)
    ).isoformat()

    cursor.execute("""
        SELECT id FROM work_orders
        WHERE machine=?
        AND issue=?
        AND created_by='AI_SYSTEM'
        AND created_at>=?
    """, (machine, issue, time_limit))

    exists = cursor.fetchone() is not None

    conn.close()
    return exists


def create_work_order_from_prediction(machine, risk_score, sensor_data=None):

    if risk_score < 0.70:
        return False

    issue = f"AI detected failure risk ({risk_score*100:.1f}%)"

    if recent_ai_work_order_exists(machine, issue):
        return False

    priority = "HIGH" if risk_score >= 0.85 else "MEDIUM"

    create_work_order(
        machine=machine,
        issue=issue,
        priority=priority,
        created_by="AI_SYSTEM"
    )

    return True