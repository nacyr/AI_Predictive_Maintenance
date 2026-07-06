import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# ==========================================================
# DATABASE
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "work_orders.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# INITIALIZE DATABASE
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
# CREATE
# ==========================================================

def create_work_order(
    machine,
    issue,
    priority="MEDIUM",
    created_by="SYSTEM",
    assigned_to=None
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO work_orders
        (
            machine,
            issue,
            priority,
            created_by,
            assigned_to
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        machine,
        issue,
        priority,
        created_by,
        assigned_to
    ))

    conn.commit()
    conn.close()

    return True


# ==========================================================
# READ
# ==========================================================

def get_work_orders():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM work_orders
        ORDER BY datetime(created_at) DESC
    """, conn)

    conn.close()

    return df


def get_all_work_orders():
    """Backward compatibility"""
    return get_work_orders()


# ==========================================================
# SEARCH
# ==========================================================

def search_work_orders_by_machine(machine):

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM work_orders
        WHERE machine LIKE ?
        ORDER BY datetime(created_at) DESC
    """, conn, params=(f"%{machine}%",))

    conn.close()

    return df


# ==========================================================
# UPDATE CORE
# ==========================================================

def update_work_order(work_order_id, **kwargs):

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
    values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    values.append(work_order_id)

    cursor.execute(f"""
        UPDATE work_orders
        SET {", ".join(fields)}
        WHERE id=?
    """, values)

    conn.commit()
    conn.close()

    return True


# ==========================================================
# STATUS
# ==========================================================

def update_work_order_status(work_order_id, status):

    return update_work_order(
        work_order_id,
        status=status
    )


def change_work_order_status(work_order_id, status):
    """Backward compatibility"""
    return update_work_order_status(
        work_order_id,
        status
    )


# ==========================================================
# ASSIGN ENGINEER
# ==========================================================

def assign_work_order(work_order_id, engineer):

    return update_work_order(
        work_order_id,
        assigned_to=engineer
    )


# ==========================================================
# DELETE
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
# STATISTICS
# ==========================================================

def get_work_order_statistics():

    orders = get_work_orders()

    if orders.empty:

        return {
            "total": 0,
            "pending": 0,
            "approved": 0,
            "in_progress": 0,
            "completed": 0,
            "rejected": 0
        }

    return {

        "total": len(orders),

        "pending": (orders["status"] == "PENDING").sum(),

        "approved": (orders["status"] == "APPROVED").sum(),

        "in_progress": (orders["status"] == "IN_PROGRESS").sum(),

        "completed": (orders["status"] == "COMPLETED").sum(),

        "rejected": (orders["status"] == "REJECTED").sum()
    }


# ==========================================================
# ANALYTICS
# ==========================================================

def get_machine_failure_frequency():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            machine,
            COUNT(*) AS count
        FROM work_orders
        GROUP BY machine
        ORDER BY count DESC
    """, conn)

    conn.close()

    return df


def get_daily_work_order_trends():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            DATE(created_at) AS date,
            COUNT(*) AS count
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
        SELECT
            COALESCE(created_by,'MANUAL'),
            COUNT(*)
        FROM work_orders
        GROUP BY created_by
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        row[0]: row[1]
        for row in rows
    }


# ==========================================================
# AI DUPLICATE PROTECTION
# ==========================================================

def recent_ai_work_order_exists(
    machine,
    issue,
    minutes_window=30
):

    conn = get_connection()
    cursor = conn.cursor()

    cutoff = (
        datetime.now() -
        timedelta(minutes=minutes_window)
    ).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        SELECT id
        FROM work_orders
        WHERE machine=?
        AND issue=?
        AND created_by='AI_SYSTEM'
        AND created_at>=?
    """, (
        machine,
        issue,
        cutoff
    ))

    exists = cursor.fetchone() is not None

    conn.close()

    return exists


# ==========================================================
# CREATE FROM AI
# ==========================================================

def create_work_order_from_prediction(
    machine,
    risk_score,
    sensor_data=None
):

    if risk_score < 0.70:
        return False

    issue = (
        f"AI detected failure risk "
        f"({risk_score * 100:.1f}%)"
    )

    if recent_ai_work_order_exists(
        machine,
        issue
    ):
        return False

    priority = (
        "HIGH"
        if risk_score >= 0.85
        else "MEDIUM"
    )

    create_work_order(
        machine=machine,
        issue=issue,
        priority=priority,
        created_by="AI_SYSTEM"
    )

    return True


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

create_work_orders_table()