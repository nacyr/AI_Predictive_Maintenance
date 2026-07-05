from pathlib import Path
import sys
from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# SAFE PROJECT ROOT (STREAMLIT CLOUD FIX)
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# SAFE IMPORTS
# ==========================================================

try:
    from components.header import show_header
    from components.sidebar import show_sidebar
    from components.footer import show_footer
except:
    def show_header(*args, **kwargs): pass
    def show_sidebar(*args, **kwargs): pass
    def show_footer(): pass

try:
    from utils.plant import plant_status
except:
    plant_status = None

try:
    import database.work_orders as wo
except Exception as e:
    st.error("Database import failed")
    st.code(str(e))
    st.stop()

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Guest Dashboard",
    page_icon="👤",
    layout="wide"
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="guest_dashboard_refresh"
)

# ==========================================================
# SESSION CHECK
# ==========================================================

if "user" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

if user is None:
    st.switch_page("app.py")
    st.stop()

# ==========================================================
# ROLE CHECK
# ==========================================================

allowed_roles = ["Administrator", "Guest"]

if user["role"] not in allowed_roles:
    st.error("Access Denied")
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "👤 Guest Dashboard",
    "Industrial AI Predictive Maintenance (Read Only)"
)

show_sidebar(user)

# ==========================================================
# LOAD DATA (SAFE)
# ==========================================================

try:
    plants = plant_status() if plant_status else pd.DataFrame()
except:
    plants = pd.DataFrame()

try:
    work_orders = wo.get_work_orders()
except:
    work_orders = pd.DataFrame()

# ==========================================================
# KPIS
# ==========================================================

total_plants = len(plants)
total_orders = len(work_orders)

# Plant status counters
normal = warning = critical = 0

if not plants.empty and "Status" in plants.columns:
    status = plants["Status"].astype(str)

    normal = status.str.contains("NORMAL", case=False, na=False).sum()
    warning = status.str.contains("WARNING", case=False, na=False).sum()
    critical = status.str.contains("CRITICAL", case=False, na=False).sum()

# Work order counters
pending = approved = completed = rejected = 0

if not work_orders.empty and "status" in work_orders.columns:
    pending = (work_orders["status"] == "PENDING").sum()
    approved = (work_orders["status"] == "APPROVED").sum()
    completed = (work_orders["status"] == "COMPLETED").sum()
    rejected = (work_orders["status"] == "REJECTED").sum()

# ==========================================================
# HEADER METRICS
# ==========================================================

st.subheader("📊 Enterprise Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Plants", total_plants)
c2.metric("Work Orders", total_orders)
c3.metric("Normal Assets", normal)
c4.metric("Critical Assets", critical)

st.divider()

# ==========================================================
# WORK ORDER METRICS
# ==========================================================

a1, a2, a3, a4 = st.columns(4)

a1.metric("Pending", pending)
a2.metric("Approved", approved)
a3.metric("Completed", completed)
a4.metric("Rejected", rejected)

st.divider()

# ==========================================================
# MAIN TABLES
# ==========================================================

left, right = st.columns([2, 1])

with left:

    st.subheader("🏭 Plant Status")

    if plants.empty:
        st.info("No plant data available")
    else:
        st.dataframe(plants, use_container_width=True, hide_index=True)

with right:

    st.subheader("📋 Work Order Summary")

    if work_orders.empty:
        st.info("No work orders available")
    else:
        summary = work_orders["status"].value_counts().reset_index()
        summary.columns = ["Status", "Count"]

        st.dataframe(summary, use_container_width=True, hide_index=True)

st.divider()

# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

st.subheader("🛠 Recent Work Orders")

if work_orders.empty:
    st.info("No maintenance data available")
else:

    cols = ["machine", "issue", "priority", "status", "created_at"]

    available_cols = [c for c in cols if c in work_orders.columns]

    st.dataframe(
        work_orders[available_cols].head(10),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# CHART
# ==========================================================

st.subheader("📊 Work Order Distribution")

if not work_orders.empty and "status" in work_orders.columns:
    st.bar_chart(work_orders["status"].value_counts())
else:
    st.info("No chart data available")

st.divider()

# ==========================================================
# AI STATUS
# ==========================================================

st.subheader("🤖 AI Monitoring Status")

if critical == 0:
    st.success("All systems operating normally")
elif critical <= 2:
    st.warning(f"{critical} critical asset(s) detected")
else:
    st.error("Immediate attention required")

if warning > 0:
    st.info(f"{warning} asset(s) under observation")

st.divider()

# ==========================================================
# PERMISSIONS INFO
# ==========================================================

st.subheader("🔒 Guest Permissions")

col1, col2 = st.columns(2)

with col1:
    st.success("""
✔ View dashboards  
✔ View plant status  
✔ View AI predictions  
✔ View work orders  
✔ View analytics  
""")

with col2:
    st.error("""
✖ Create work orders  
✖ Modify data  
✖ Delete records  
✖ Approve maintenance  
✖ Manage users  
""")

st.divider()

# ==========================================================
# NAVIGATION
# ==========================================================

st.subheader("⚡ Quick Navigation")

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("🤖 AI Prediction", use_container_width=True):
        st.switch_page("pages/prediction.py")

with q2:
    if st.button("📈 Analytics", use_container_width=True):
        st.switch_page("pages/analytics.py")

with q3:
    if st.button("🛠 Work Orders", use_container_width=True):
        st.switch_page("pages/maintenance_work_orders.py")

with q4:
    if st.button("🏠 Admin Dashboard", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")

st.divider()

# ==========================================================
# SESSION INFO
# ==========================================================

st.subheader("ℹ️ Session Info")

st.info(
    f"""
User: **{user['fullname']}**  
Role: **{user['role']}**  
Time: **{datetime.now().strftime('%d %b %Y %H:%M:%S')}**  
Auto-refresh: **10 seconds**
"""
)

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()