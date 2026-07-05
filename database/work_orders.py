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


# ==========================================================
# CREATE WORK ORDER
# ==========================================================

def create_work_order(
    machine,
    issue,
    priority="MEDIUM",
    created_by=None,
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
            assigned_to
        )
        VALUES (?, ?, ?, 'PENDING', ?, ?)
        """,
        (
            machine,
            issue,
            priority,
            created_by,
            assigned_to
        )
    )

    conn.commit()
    conn.close()

    return True


# ==========================================================
# READ ALL WORK ORDERS
# ==========================================================

def get_work_orders():

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM work_orders
        ORDER BY datetime(created_at) DESC
        """,
        conn
    )

    conn.close()

    return df


# Compatibility alias
get_all_work_orders = get_work_orders


# ==========================================================
# GET SINGLE WORK ORDER
# ==========================================================

def get_work_order(work_order_id):

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
# UPDATE WORK ORDER
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
# UPDATE STATUS
# ==========================================================

def update_work_order_status(work_order_id, status):

    return update_work_order(
        work_order_id,
        status=status
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


# Compatibility alias

change_work_order_status = update_work_order_status


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
    conn.close()

    return True
# ==========================================================
# SEARCH
# ==========================================================

def search_work_orders_by_machine(machine_name):

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM work_orders
        WHERE machine LIKE ?
        ORDER BY datetime(created_at) DESC
        """,
        conn,
        params=(f"%{machine_name}%",)
    )

    conn.close()

    return df


# ==========================================================
# WORK ORDER STATISTICS
# ==========================================================

def get_work_order_statistics():

    orders = get_work_orders()

    if orders.empty:

        return {
            "total": 0,
            "pending": 0,
            "approved": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0,
            "rejected": 0
        }

    status = orders["status"].astype(str).str.upper()

    return {

        "total": len(orders),

        "pending": (status == "PENDING").sum(),

        "approved": (status == "APPROVED").sum(),

        "assigned": (status == "ASSIGNED").sum(),

        "in_progress": (status == "IN_PROGRESS").sum(),

        "completed": (status == "COMPLETED").sum(),

        "rejected": (status == "REJECTED").sum()
    }


# ==========================================================
# MACHINE FAILURE FREQUENCY
# ==========================================================

def get_machine_failure_frequency():

    orders = get_work_orders()

    if orders.empty:

        return pd.DataFrame(
            columns=[
                "machine",
                "count"
            ]
        )

    df = (
        orders.groupby("machine")
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False
        )
    )

    return df


# ==========================================================
# DAILY WORK ORDER TRENDS
# ==========================================================

def get_daily_work_order_trends():

    orders = get_work_orders()

    if orders.empty:

        return pd.DataFrame(
            columns=[
                "date",
                "count"
            ]
        )

    orders["date"] = pd.to_datetime(
        orders["created_at"]
    ).dt.date

    trends = (
        orders.groupby("date")
        .size()
        .reset_index(name="count")
        .sort_values("date")
    )

    return trends


# ==========================================================
# AI vs MANUAL BREAKDOWN
# ==========================================================

def get_ai_vs_manual_breakdown():

    orders = get_work_orders()

    if orders.empty:

        return {
            "AI_SYSTEM": 0,
            "MANUAL": 0
        }

    ai = (
        orders["created_by"]
        .fillna("")
        .eq("AI_SYSTEM")
        .sum()
    )

    manual = len(orders) - ai

    return {
        "AI_SYSTEM": int(ai),
        "MANUAL": int(manual)
    }
# ==========================================================
# AI DUPLICATE CHECK
# ==========================================================

def recent_ai_work_order_exists(
    machine,
    issue,
    minutes_window=30
):

    conn = get_connection()

    cutoff = (
        datetime.now() - timedelta(minutes=minutes_window)
    ).strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM work_orders
        WHERE machine=?
        AND issue=?
        AND created_by='AI_SYSTEM'
        AND created_at>=?
        LIMIT 1
        """,
        (
            machine,
            issue,
            cutoff
        )
    )

    exists = cursor.fetchone() is not None

    conn.close()

    return exists


# ==========================================================
# CREATE WORK ORDER FROM AI PREDICTION
# ==========================================================

def create_work_order_from_prediction(
    machine,
    risk_score,
    sensor_data=None
):

    # Ignore safe machines
    if risk_score < 0.70:
        return False

    issue = (
        f"AI detected possible failure "
        f"({risk_score * 100:.1f}% risk)"
    )

    # Prevent duplicates
    if recent_ai_work_order_exists(
        machine,
        issue
    ):
        return False

    if risk_score >= 0.90:
        priority = "HIGH"

    elif risk_score >= 0.80:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    create_work_order(
        machine=machine,
        issue=issue,
        priority=priority,
        created_by="AI_SYSTEM"
    )

    return True


# ==========================================================
# PENDING WORK ORDERS
# ==========================================================

def get_pending_work_orders():

    orders = get_work_orders()

    if orders.empty:
        return orders

    return orders[
        orders["status"] == "PENDING"
    ]


# ==========================================================
# APPROVED WORK ORDERS
# ==========================================================

def get_approved_work_orders():

    orders = get_work_orders()

    if orders.empty:
        return orders

    return orders[
        orders["status"] == "APPROVED"
    ]


# ==========================================================
# COMPLETED WORK ORDERS
# ==========================================================

def get_completed_work_orders():

    orders = get_work_orders()

    if orders.empty:
        return orders

    return orders[
        orders["status"] == "COMPLETED"
    ]


# ==========================================================
# ASSIGNED WORK ORDERS
# ==========================================================

def get_assigned_work_orders(engineer=None):

    orders = get_work_orders()

    if orders.empty:
        return orders

    assigned = orders[
        orders["status"] == "ASSIGNED"
    ]

    if engineer:

        assigned = assigned[
            assigned["assigned_to"] == engineer
        ]

    return assigned
# ==========================================================
# ENGINEER WORK ORDERS
# ==========================================================

def get_engineer_work_orders(engineer):

    orders = get_work_orders()

    if orders.empty:
        return orders

    if "assigned_to" not in orders.columns:
        return pd.DataFrame(columns=orders.columns)

    return orders[
        orders["assigned_to"] == engineer
    ]


# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

def get_recent_work_orders(limit=10):

    orders = get_work_orders()

    if orders.empty:
        return orders

    return orders.head(limit)


# ==========================================================
# DATABASE INFORMATION
# ==========================================================

def work_order_count():

    return len(get_work_orders())


# ==========================================================
# RESET DATABASE (OPTIONAL)
# ==========================================================

def delete_all_work_orders():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM work_orders"
    )

    conn.commit()
    conn.close()


# ==========================================================
# COMPATIBILITY ALIASES
# ==========================================================

change_work_order_status = update_work_order_status

assign_engineer = assign_work_order

get_all_work_orders = get_work_orders


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

create_work_orders_table()