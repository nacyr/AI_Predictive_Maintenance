import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation

from database.work_orders import get_work_orders
from utils.simulator import generate_sensor_data

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="👤 Guest Dashboard",
    icon="👤",
    subtitle="Industrial Monitoring (Read Only)",
    allowed_roles=["Administrator", "Guest"]
)

# ==========================================================
# LOAD DATA
# ==========================================================

orders = get_work_orders()

if orders is None:
    orders = pd.DataFrame()

# Simulated machine data for guest view
machines = ["Pump A1", "Compressor B2", "Motor C3"]

machine_records = []

for m in machines:
    sensor = generate_sensor_data()

    machine_records.append({
        "Machine": m,
        "Temperature": sensor["temperature"],
        "Pressure": sensor["pressure"],
        "Vibration": sensor["vibration"],
        "Status": "RUNNING"
    })

machine_df = pd.DataFrame(machine_records)

# ==========================================================
# WELCOME SECTION
# ==========================================================

st.success(f"Welcome, {user.get('fullname', 'Guest')}")

st.info(
    "Guest users have read-only access to system monitoring. "
    "No modifications are allowed."
)

st.divider()

# ==========================================================
# KPIs
# ==========================================================

st.subheader("📊 Work Order Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Orders", len(orders))
col2.metric(
    "Pending",
    (orders["status"] == "PENDING").sum() if not orders.empty else 0
)
col3.metric(
    "Completed",
    (orders["status"] == "COMPLETED").sum() if not orders.empty else 0
)

st.divider()

# ==========================================================
# MACHINE STATUS
# ==========================================================

st.subheader("🏭 Live Machine Status")

st.dataframe(machine_df, use_container_width=True, hide_index=True)

st.bar_chart(machine_df.set_index("Machine")[["Temperature", "Pressure", "Vibration"]])

st.divider()

# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

st.subheader("🛠 Recent Maintenance Activities")

if orders.empty:
    st.info("No work orders available.")
else:
    st.dataframe(
        orders.head(10),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# WORK ORDER STATUS DISTRIBUTION
# ==========================================================

st.subheader("📈 Work Order Distribution")

if not orders.empty:
    st.bar_chart(orders["status"].value_counts())
else:
    st.info("No statistics available.")

st.divider()

# ==========================================================
# PERMISSIONS DISPLAY
# ==========================================================

st.subheader("🔒 Guest Permissions")

col1, col2 = st.columns(2)

with col1:
    st.success("""
✔ View Machine Status  
✔ View Work Orders  
✔ View Analytics  
✔ View System Dashboard  
""")

with col2:
    st.error("""
✖ Create Work Orders  
✖ Update Work Orders  
✖ Delete Work Orders  
✖ Manage Users  
""")

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=False,
    admin=(user.get("role") == "Administrator")
)

st.divider()

# ==========================================================
# SESSION INFO
# ==========================================================

st.subheader("👤 Session Information")

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
**User:** {user.get('fullname', 'Guest')}  
**Role:** {user.get('role', 'Guest')}
""")

with col2:
    st.info("""
**Dashboard:** Guest View  
**Access:** Read Only  
**Mode:** Monitoring System
""")

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

if not machine_df.empty:
    st.subheader("🟢 System Status")
    st.success("All systems operational")

# ==========================================================
# END PAGE
# ==========================================================

end_page()