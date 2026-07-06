import streamlit as st
import pandas as pd

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation
from utils.simulator import generate_sensor_data

from database.work_orders import get_work_orders

# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="👨‍💼 Supervisor Dashboard",
    icon="👨‍💼",
    subtitle="Maintenance Supervision & Operations",
    allowed_roles=[
        "Administrator",
        "Supervisor"
    ]
)

# ==========================================================
# LOAD WORK ORDERS
# ==========================================================

orders = get_work_orders()

if orders is None:
    orders = pd.DataFrame()

# ==========================================================
# GENERATE LIVE MACHINE DATA
# ==========================================================

machines = [
    "Pump A1",
    "Pump A2",
    "Compressor B1",
    "Compressor B2",
    "Motor C1",
    "Generator D1"
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
        "Temperature (°C)": sensor["temperature"],
        "Pressure (bar)": sensor["pressure"],
        "Vibration": sensor["vibration"],
        "Current (A)": sensor["current"],
        "RPM": sensor["rpm"],
        "Failure Risk (%)": risk,
        "Status": status
    })

machine_df = pd.DataFrame(records)

# ==========================================================
# KPI SECTION
# ==========================================================

st.subheader("📊 Work Order Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total", len(orders))

c2.metric(
    "Pending",
    (orders["status"] == "PENDING").sum()
    if not orders.empty else 0
)

c3.metric(
    "Approved",
    (orders["status"] == "APPROVED").sum()
    if not orders.empty else 0
)

c4.metric(
    "Completed",
    (orders["status"] == "COMPLETED").sum()
    if not orders.empty else 0
)

st.divider()

# ==========================================================
# LIVE MACHINE STATUS
# ==========================================================

st.subheader("🏭 Live Machine Status")

st.dataframe(
    machine_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# PENDING WORK ORDERS
# ==========================================================

st.subheader("📝 Pending Work Orders")

pending = (
    orders[orders["status"] == "PENDING"]
    if not orders.empty
    else pd.DataFrame()
)

if pending.empty:
    st.success("There are no pending work orders.")
else:
    st.dataframe(
        pending,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# APPROVED WORK ORDERS
# ==========================================================

st.subheader("✅ Approved Work Orders")

approved = (
    orders[orders["status"] == "APPROVED"]
    if not orders.empty
    else pd.DataFrame()
)

if approved.empty:
    st.info("No approved work orders.")
else:
    st.dataframe(
        approved,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# COMPLETED WORK ORDERS
# ==========================================================

st.subheader("✔ Completed Work Orders")

completed = (
    orders[orders["status"] == "COMPLETED"]
    if not orders.empty
    else pd.DataFrame()
)

if completed.empty:
    st.info("No completed work orders.")
else:
    st.dataframe(
        completed,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# WORK ORDER DISTRIBUTION
# ==========================================================

st.subheader("📈 Work Order Distribution")

if orders.empty:
    st.info("No work order data available.")
else:
    st.bar_chart(
        orders["status"].value_counts()
    )

st.divider()

# ==========================================================
# MACHINE HEALTH
# ==========================================================

st.subheader("💚 Machine Health")

health = machine_df.copy()

health["Health (%)"] = (
    100 - health["Failure Risk (%)"]
).clip(lower=0)

st.dataframe(
    health[
        [
            "Machine",
            "Health (%)",
            "Failure Risk (%)",
            "Status"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# SUPERVISOR NOTES
# ==========================================================

st.subheader("📝 Supervisor Notes")

notes = st.text_area(
    "Observations",
    placeholder="Enter inspection comments, recommendations, approvals or follow-up actions...",
    height=180
)

if st.button(
    "Save Notes",
    use_container_width=True
):

    if notes.strip():

        st.success(
            "Supervisor notes saved successfully (Demo Mode)."
        )

    else:

        st.warning(
            "Please enter some notes first."
        )

st.divider()

# ==========================================================
# SYSTEM STATUS
# ==========================================================

st.subheader("🟢 System Status")

critical = (
    machine_df["Failure Risk (%)"] >= 70
).sum()

if critical == 0:

    st.success(
        "All monitored machines are operating normally."
    )

elif critical <= 2:

    st.warning(
        f"{critical} machine(s) require maintenance attention."
    )

else:

    st.error(
        "Multiple critical machines detected."
    )

st.divider()

# ==========================================================
# QUICK NAVIGATION
# ==========================================================

quick_navigation(
    prediction=True,
    analytics=True,
    maintenance=True,
    admin=user.get("role") == "Administrator"
)

st.divider()

# ==========================================================
# SESSION INFORMATION
# ==========================================================

st.subheader("👤 Session Information")

left, right = st.columns(2)

with left:

    st.info(f"""
**User:** {user.get('fullname', 'Unknown')}

**Role:** {user.get('role', 'Unknown')}
""")

with right:

    st.info("""
**Dashboard:** Supervisor Dashboard

**Mode:** Supervision

**Refresh:** Automatic
""")

# ==========================================================
# END PAGE
# ==========================================================

end_page()