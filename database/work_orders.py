import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "work_orders.db"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_connection():
    """
    Returns a connection to the SQLite database.
    """
    return sqlite3.connect(DB_PATH)


# ==========================================================
# CREATE TABLE
# ==========================================================

def create_work_orders_table():
    """
    Creates the work_orders table if it does not exist.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_orders(
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
# CREATE WORK ORDER (MANUAL)
# ==========================================================

def create_work_order(machine, issue, priority="MEDIUM", created_by=None):
    """
    Creates a manual work order.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO work_orders(machine, issue, priority, created_by)
        VALUES (?, ?, ?, ?)
    """, (machine, issue, priority, created_by))

    conn.commit()
    conn.close()


# ==========================================================
# CHECK DUPLICATE AI WORK ORDER
# ==========================================================

def recent_ai_work_order_exists(machine, issue, minutes_window=30):
    """
    Prevents duplicate AI-generated work orders.
    """

    conn = get_connection()
    cursor = conn.cursor()

    time_limit = (
        datetime.now() - timedelta(minutes=minutes_window)
    ).isoformat()

    cursor.execute("""
        SELECT id
        FROM work_orders
        WHERE machine=?
          AND issue=?
          AND created_by='AI_SYSTEM'
          AND status='PENDING'
          AND created_at>=?
    """, (machine, issue, time_limit))

    exists = cursor.fetchone() is not None

    conn.close()
    return exists


# ==========================================================
# CREATE AI WORK ORDER
# ==========================================================

def create_work_order_from_prediction(machine, risk_score, sensor_data=None):
    """
    Automatically creates a work order from AI prediction.
    """

    if risk_score < 0.70:
        return False

    issue = f"AI detected high failure risk ({risk_score * 100:.1f}%)"

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


# ==========================================================
# GET ALL WORK ORDERS
# ==========================================================

def get_all_work_orders():
    """
    Returns all work orders (DataFrame).
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM work_orders
        ORDER BY datetime(created_at) DESC
    """, conn)

    conn.close()
    return df


# ==========================================================
# COMPATIBILITY ALIAS (FIXES YOUR ERROR)
# ==========================================================

def get_work_orders():
    """
    Alias for backward compatibility (used in Streamlit pages).
    """
    return get_all_work_orders()


# ==========================================================
# GET WORK ORDER BY ID
# ==========================================================

def get_work_order_by_id(work_order_id):
    """
    Returns a single work order.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM work_orders
        WHERE id=?
    """, (work_order_id,))

    row = cursor.fetchone()
    conn.close()

    return row


# ==========================================================
# FILTER BY STATUS
# ==========================================================

def get_work_orders_by_status(status):
    """
    Filter work orders by status.
    """

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM work_orders
        WHERE status=?
        ORDER BY datetime(created_at) DESC
    """, conn, params=(status,))

    conn.close()
    return df


def get_pending_work_orders():
    return get_work_orders_by_status("PENDING")


def get_completed_work_orders():
    return get_work_orders_by_status("COMPLETED")


# ==========================================================
# SEARCH FUNCTIONS
# ==========================================================

def search_work_orders_by_machine(machine_name):
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM work_orders
        WHERE machine LIKE ?
        ORDER BY datetime(created_at) DESC
    """, conn, params=(f"%{machine_name}%",))

    conn.close()
    return df


def search_work_orders_by_engineer(engineer_name):
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM work_orders
        WHERE assigned_to LIKE ?
        ORDER BY datetime(created_at) DESC
    """, conn, params=(f"%{engineer_name}%",))

    conn.close()
    return df


# ==========================================================
# UPDATE WORK ORDER
# ==========================================================

def update_work_order(work_order_id, **kwargs):
    """
    Flexible update function.
    """

    if not kwargs:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    fields = []
    values = []

    for key, value in kwargs.items():
        fields.append(f"{key}=?")
        values.append(value)

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
# ASSIGN ENGINEER
# ==========================================================

def assign_work_order(work_order_id, engineer_name):
    return update_work_order(
        work_order_id,
        assigned_to=engineer_name,
        status="ASSIGNED"
    )


# ==========================================================
# CHANGE STATUS
# ==========================================================

def change_work_order_status(work_order_id, status):
    return update_work_order(work_order_id, status=status)


# ==========================================================
# DELETE WORK ORDER
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

    return True


# ==========================================================
# BULK UPDATE
# ==========================================================

def bulk_update_status(work_order_ids, status):
    if not work_order_ids:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join(["?"] * len(work_order_ids))

    sql = f"""
        UPDATE work_orders
        SET status=?, updated_at=?
        WHERE id IN ({placeholders})
    """

    cursor.execute(
        sql,
        [status, datetime.now().isoformat()] + work_order_ids
    )

    conn.commit()
    conn.close()

    return True


# ==========================================================
# DASHBOARD STATISTICS
# ==========================================================

def get_work_order_statistics():
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    cursor.execute("SELECT COUNT(*) FROM work_orders")
    stats["total"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='PENDING'")
    stats["pending"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='ASSIGNED'")
    stats["assigned"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='IN_PROGRESS'")
    stats["in_progress"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='COMPLETED'")
    stats["completed"] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM work_orders WHERE status='REJECTED'")
    stats["rejected"] = cursor.fetchone()[0]

    conn.close()
    return stats
