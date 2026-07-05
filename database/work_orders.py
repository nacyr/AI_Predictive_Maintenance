import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd

# ==========================================================
# DATABASE PATH
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "work_orders.db"

# ==========================================================
# CONNECTION
# ==========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================================
# CREATE TABLE
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


# Create table automatically when imported
create_work_orders_table()
# ==========================================================
# CREATE WORK ORDER
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

    cursor.execute(
        """
        INSERT INTO work_orders
        (
            machine,
            issue,
            priority,
            status,
            created_by,
            assigned_to,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            machine,
            issue,
            priority,
            "PENDING",
            created_by,
            assigned_to,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    work_order_id = cursor.lastrowid
    conn.close()

    return work_order_id


# ==========================================================
# GET ALL WORK ORDERS
# ==========================================================

def get_work_orders():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM work_orders
        ORDER BY id DESC
        """,
        conn
    )

    conn.close()

    return df


# Compatibility alias for old dashboards
def get_all_work_orders():
    return get_work_orders()


# ==========================================================
# GET SINGLE WORK ORDER
# ==========================================================

def get_work_order_by_id(work_order_id):

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM work_orders
        WHERE id=?
        """,
        conn,
        params=(work_order_id,)
    )

    conn.close()

    if df.empty:
        return None

    return df.iloc[0].to_dict()


# ==========================================================
# DELETE WORK ORDER
# ==========================================================

def delete_work_order(work_order_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM work_orders
        WHERE id=?
        """,
        (work_order_id,)
    )

    conn.commit()
    deleted = cursor.rowcount > 0

    conn.close()

    return deleted
# ==========================================================
# UPDATE WORK ORDER (GENERIC)
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
    values.append(datetime.now().isoformat())

    values.append(work_order_id)

    sql = f"""
        UPDATE work_orders
        SET {", ".join(fields)}
        WHERE id=?
    """

    cursor.execute(sql, values)

    conn.commit()

    success = cursor.rowcount > 0

    conn.close()

    return success


# ==========================================================
# UPDATE STATUS
# ==========================================================

def update_work_order_status(work_order_id, status):

    return update_work_order(
        work_order_id,
        status=status
    )


# ==========================================================
# COMPATIBILITY ALIAS
# (Older dashboards use this name)
# ==========================================================

def change_work_order_status(work_order_id, status):

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

        assigned_to=engineer,

        status="ASSIGNED"

    )


# ==========================================================
# SEARCH
# ==========================================================

def search_work_orders_by_machine(machine):

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM work_orders
        WHERE LOWER(machine) LIKE LOWER(?)
        ORDER BY id DESC
        """,
        conn,
        params=(f"%{machine}%",)
    )

    conn.close()

    return df
# ==========================================================
# WORK ORDER STATISTICS
# ==========================================================

def get_work_order_statistics():

    df = get_work_orders()

    if df.empty:
        return {
            "total": 0,
            "pending": 0,
            "approved": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0,
            "rejected": 0,
        }

    stats = {
        "total": len(df),
        "pending": int((df["status"] == "PENDING").sum()),
        "approved": int((df["status"] == "APPROVED").sum()),
        "assigned": int((df["status"] == "ASSIGNED").sum()),
        "in_progress": int((df["status"] == "IN_PROGRESS").sum()),
        "completed": int((df["status"] == "COMPLETED").sum()),
        "rejected": int((df["status"] == "REJECTED").sum()),
    }

    return stats


# ==========================================================
# MACHINE FAILURE FREQUENCY
# ==========================================================

def get_machine_failure_frequency():

    df = get_work_orders()

    if df.empty:
        return pd.DataFrame(columns=["machine", "count"])

    return (
        df.groupby("machine")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


# ==========================================================
# DAILY WORK ORDER TRENDS
# ==========================================================

def get_daily_work_order_trends():

    df = get_work_orders()

    if df.empty:
        return pd.DataFrame(columns=["date", "count"])

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    df["date"] = df["created_at"].dt.date

    return (
        df.groupby("date")
        .size()
        .reset_index(name="count")
        .sort_values("date")
    )


# ==========================================================
# AI VS MANUAL BREAKDOWN
# ==========================================================

def get_ai_vs_manual_breakdown():

    df = get_work_orders()

    if df.empty:
        return {
            "AI_SYSTEM": 0,
            "MANUAL": 0
        }

    ai = int(
        (df["created_by"] == "AI_SYSTEM").sum()
    )

    manual = len(df) - ai

    return {
        "AI_SYSTEM": ai,
        "MANUAL": manual
    }


# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

def get_recent_work_orders(limit=10):

    df = get_work_orders()

    if df.empty:
        return df

    return df.head(limit)
# ==========================================================
# AI DUPLICATE PROTECTION
# ==========================================================

def recent_ai_work_order_exists(
    machine,
    issue,
    minutes_window=30
):
    df = get_work_orders()

    if df.empty:
        return False

    if "created_at" not in df.columns:
        return False

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    cutoff = datetime.now() - timedelta(
        minutes=minutes_window
    )

    recent = df[

        (df["machine"] == machine)
        &
        (df["issue"] == issue)
        &
        (df["created_by"] == "AI_SYSTEM")
        &
        (df["created_at"] >= cutoff)

    ]

    return not recent.empty


# ==========================================================
# CREATE AI WORK ORDER
# ==========================================================

def create_work_order_from_prediction(
    machine,
    risk_score,
    sensor_data=None
):

    if risk_score < 0.70:
        return False

    issue = (
        f"AI detected high failure risk "
        f"({risk_score * 100:.1f}%)"
    )

    if recent_ai_work_order_exists(
        machine,
        issue
    ):
        return False

    priority = (
        "CRITICAL"
        if risk_score >= 0.90
        else "HIGH"
    )

    create_work_order(
        machine=machine,
        issue=issue,
        priority=priority,
        created_by="AI_SYSTEM"
    )

    return True


# ==========================================================
# COMPATIBILITY ALIASES
# ==========================================================

def get_all_work_orders():
    return get_work_orders()


def change_status(
    work_order_id,
    status
):
    return update_work_order_status(
        work_order_id,
        status
    )


def assign_engineer(
    work_order_id,
    engineer
):
    return assign_work_order(
        work_order_id,
        engineer
    )