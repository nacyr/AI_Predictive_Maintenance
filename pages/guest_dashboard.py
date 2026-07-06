import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation
from utils.simulator import generate_sensor_data

from database.work_orders import get_work_orders

from components.live_status import show_live_status
from components.kpi_cards import show_kpi_cards
from components.live_machine_table import show_live_machine_table
from components.plant_health import show_plant_health
from components.alert_center import show_alert_center

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="👤 Guest Dashboard",
    icon="👤",
    subtitle="Industrial Monitoring (Read Only)",
    allowed_roles=[
        "Administrator",
        "Guest"
    ]
)

# ==========================================================
# AUTO REFRESH
# ==========================================================

refresh_count = st_autorefresh(
    interval=10000,
    key="guest_dashboard_refresh"
)

show_live_status(refresh_count)

st.divider()

# ==========================================================
# LOAD WORK ORDERS
# ==========================================================

orders = get_work_orders()

if orders is None:
    orders = pd.DataFrame()

# ==========================================================
# LIVE MACHINE DATA
# ==========================================================

machines = [
    "Pump A1",
    "Pump A2",
    "Compressor B1",
    "Compressor B2",
    "Motor C1",
    "Motor C2",
    "Generator D1",
    "Cooling Fan E1"
]

records = []

for machine in machines:

    sensor = generate_sensor_data()

    risk = min(
        100,
        round(
            sensor["temperature"] * 0.40 +
            sensor["vibration"] * 15 +
            sensor["pressure"] * 2,
            1
        )
    )

    if risk >= 70:
        status = "CRITICAL"
    elif risk >= 40:
        status = "WARNING"
    else:
        status = "NORMAL"

    records.append({

        "Machine": machine,

        "Temperature (°C)": round(sensor["temperature"], 2),

        "Pressure (bar)": round(sensor["pressure"], 2),

        "Vibration": round(sensor["vibration"], 2),

        "Current (A)": round(sensor["current"], 2),

        "RPM": round(sensor["rpm"], 0),

        "Running Hours": sensor["running_hours"],

        "Failure Risk (%)": risk,

        "Status": status

    })

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI CARDS
# ==========================================================

pending = (
    orders["status"] == "PENDING"
).sum() if not orders.empty else 0

completed = (
    orders["status"] == "COMPLETED"
).sum() if not orders.empty else 0

critical = (
    machine_df["Failure Risk (%)"] >= 70
).sum()

warning = (
    (machine_df["Failure Risk (%)"] >= 40)
    &
    (machine_df["Failure Risk (%)"] < 70)
).sum()

healthy = (
    machine_df["Failure Risk (%)"] < 40
).sum()

plant_health = round(
    healthy / len(machine_df) * 100,
    1
)

show_kpi_cards(
    total_orders=len(orders),
    pending=pending,
    completed=completed,
    critical=critical,
    warning=warning,
    healthy=healthy,
    plant_health=plant_health
)

st.divider()

# ==========================================================
# LIVE MACHINE MONITORING
# ==========================================================

show_live_machine_table(machine_df)

st.divider()

# ==========================================================
# RECENT WORK ORDERS
# ==========================================================

st.subheader("📋 Recent Work Orders")

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
# PLANT HEALTH
# ==========================================================

show_plant_health(machine_df)

st.divider()

# ==========================================================
# AI ALERT CENTER
# ==========================================================

show_alert_center(machine_df)

st.divider()

# ==========================================================
# WORK ORDER DISTRIBUTION
# ==========================================================

st.subheader("📊 Work Order Distribution")

if orders.empty:

    st.info("No work order statistics available.")

else:

    st.bar_chart(
        orders["status"].value_counts()
    )

st.divider()

# ==========================================================
# GUEST ACCESS PERMISSIONS
# ==========================================================

st.subheader("🔒 Guest Access Permissions")

left, right = st.columns(2)

with left:

    st.success("""
✅ View Live Machine Status

✅ View AI Predictions

✅ View Analytics

✅ View Work Orders

✅ View Plant Health

✅ View Dashboards
""")

with right:

    st.error("""
❌ Create Work Orders

❌ Update Work Orders

❌ Delete Work Orders

❌ Approve Maintenance

❌ Manage Users

❌ Change System Settings
""")

st.divider()

# ==========================================================
# PLANT STATUS
# ==========================================================

st.subheader("🟢 Plant Status")

if critical == 0:

    st.success(
        "All monitored equipment is operating within normal conditions."
    )

elif critical <= 2:

    st.warning(
        "Some equipment requires maintenance attention."
    )

else:

    st.error(
        "Critical equipment detected. Maintenance team has been notified."
    )

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=False,
    operations=True,
    admin=user.get("role") == "Administrator"
)

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

col1, col2 = st.columns(2)

with col1:

    st.info(f"""
**User:** {user.get('fullname', 'Guest')}

**Role:** {user.get('role', 'Guest')}
""")

with col2:

    st.info(f"""
**Dashboard:** Guest Dashboard

**Access Level:** Read Only

**Refresh Interval:** 10 Seconds

**Refresh Count:** {refresh_count}
""")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

end_page()