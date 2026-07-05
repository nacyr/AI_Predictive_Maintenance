import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# ==========================================================
# DB PATH
# ==========================================================

DB_PATH = Path(__file__).resolve().parent / "work_orders.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==========================================================
# INIT TABLE
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

def create_work_order(machine, issue, priority="MEDIUM", created_by=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO work_orders (machine, issue, priority, created_by)
        VALUES (?, ?, ?, ?)
    """, (machine, issue, priority, created_by))

    conn.commit()
    conn.close()


# ==========================================================
# UPDATE WORK ORDER (CORE FIX)
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
# ALIASES (IMPORTANT FOR YOUR PAGES)
# ==========================================================

def update_work_order_status(work_order_id, status):
    return update_work_order(work_order_id, status=status)


# ==========================================================
# READ ALL
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


# ==========================================================
# ANALYTICS HELPERS (FIXES IMPORT ERRORS)
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
# AI WORK ORDER GENERATION SAFETY
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
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ==========================================================
# PROJECT ROOT
# ==========================================================

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# ==========================================================
# IMPORTS
# ==========================================================

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer

from database.work_orders import (
    get_work_orders,
    get_work_order_statistics,
    get_machine_failure_frequency,
    get_daily_work_order_trends,
    get_ai_vs_manual_breakdown,
    search_work_orders_by_machine,
    update_work_order_status
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Admin Dashboard",
    layout="wide",
    page_icon="🏭"
)

st.title("🏭 Admin Control Dashboard")

# ==========================================================
# AUTH CHECK
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

if user is None or user.get("role") != "Administrator":
    st.error("Access Denied")
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(user, "Admin Dashboard", "System Control & Analytics")
show_sidebar(user)

# ==========================================================
# LOAD DATA
# ==========================================================

stats = get_work_order_statistics()
df = get_work_orders()

# Safety fallback
if df is None:
    df = pd.DataFrame()

# ==========================================================
# KPI SECTION
# ==========================================================

st.subheader("📊 System Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total", stats.get("total", 0))
c2.metric("Pending", stats.get("pending", 0))
c3.metric("Approved", stats.get("approved", 0))
c4.metric("In Progress", stats.get("in_progress", 0))
c5.metric("Completed", stats.get("completed", 0))

st.divider()

# ==========================================================
# ANALYTICS
# ==========================================================

tab1, tab2, tab3 = st.tabs([
    "📈 Trends",
    "🔧 Machine Load",
    "🤖 AI Breakdown"
])

with tab1:
    st.subheader("Daily Work Orders")

    trends = get_daily_work_order_trends()

    if not trends.empty:
        st.line_chart(trends.set_index("date"))
    else:
        st.info("No trend data available")

with tab2:
    st.subheader("Machine Frequency")

    freq = get_machine_failure_frequency()

    if not freq.empty:
        st.bar_chart(freq.set_index("machine"))
    else:
        st.info("No machine data available")

with tab3:
    st.subheader("AI vs Manual Work Orders")

    breakdown = get_ai_vs_manual_breakdown()

    if breakdown:
        df_ai = pd.DataFrame({
            "Source": list(breakdown.keys()),
            "Count": list(breakdown.values())
        })

        st.bar_chart(df_ai.set_index("Source"))
    else:
        st.info("No AI data available")

# ==========================================================
# WORK ORDER SEARCH
# ==========================================================

st.divider()
st.subheader("🔍 Search Work Orders")

search = st.text_input("Search by machine")

if search:
    result = search_work_orders_by_machine(search)
else:
    result = df

st.dataframe(result, use_container_width=True)

# ==========================================================
# UPDATE STATUS (FIXED DUPLICATE ID ISSUE)
# ==========================================================

st.divider()
st.subheader("⚙ Update Work Order")

if not df.empty:

    order_id = st.selectbox(
        "Select Work Order ID",
        df["id"].tolist(),
        key="admin_order_select"
    )

    new_status = st.selectbox(
        "New Status",
        ["PENDING", "APPROVED", "IN_PROGRESS", "COMPLETED", "REJECTED"],
        key="admin_status_select"
    )

    if st.button("Update Status", key="admin_update_btn"):

        update_work_order_status(order_id, new_status)
        st.success("Updated successfully")
        st.rerun()

# ==========================================================
# FULL TABLE
# ==========================================================

st.divider()
st.subheader("📋 All Work Orders")

st.dataframe(df, use_container_width=True)

# ==========================================================
# FOOTER
# ==========================================================

show_footer()
