import streamlit as st
import pandas as pd

from streamlit_autorefresh import st_autorefresh

from utils.page_config import setup_page, end_page
from utils.navigation import quick_navigation

from utils.simulator import (
    generate_sensor_data,
    calculate_failure_risk,
    get_machine_status
)

from database.work_orders import (
    get_work_orders,
    create_work_order,
    update_work_order_status
)

from components.live_status import show_live_status
from components.kpi_cards import show_kpi_cards
from components.live_machine_table import show_live_machine_table
from components.plant_health import show_plant_health
from components.alert_center import show_alert_center


# ==========================================================
# PAGE SETUP
# ==========================================================

user = setup_page(
    title="🛠 Maintenance Dashboard",
    icon="🛠",
    subtitle="Maintenance Control Center",
    allowed_roles=[
        "Administrator",
        "Maintenance Engineer"
    ]
)


# ==========================================================
# AUTO REFRESH
# ==========================================================

refresh_count = st_autorefresh(
    interval=10000,
    key="maintenance_dashboard_refresh"
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
# MACHINE FLEET
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



# ==========================================================
# AI MACHINE MONITORING ENGINE
# ==========================================================

records = []


for machine in machines:


    sensor = generate_sensor_data(machine)


    risk = calculate_failure_risk(

        sensor,

        machine

    )


    status = get_machine_status(

        risk

    )


    records.append(

        {

            "Machine": machine,


            "Temperature (°C)": round(
                sensor["temperature"],
                2
            ),


            "Pressure (bar)": round(
                sensor["pressure"],
                2
            ),


            "Vibration": round(
                sensor["vibration"],
                2
            ),


            "Current (A)": round(
                sensor["current"],
                2
            ),


            "RPM": round(
                sensor["rpm"],
                0
            ),


            "Running Hours": sensor["running_hours"],


            "Failure Risk (%)": risk,


            "Status": status

        }

    )



machine_df = pd.DataFrame(records)



# ==========================================================
# KPI CALCULATION
# ==========================================================

pending = (

    orders["status"] == "PENDING"

).sum() if not orders.empty else 0



completed = (

    orders["status"] == "COMPLETED"

).sum() if not orders.empty else 0



critical = (

    machine_df["Status"] == "CRITICAL"

).sum()



warning = (

    machine_df["Status"] == "WARNING"

).sum()



healthy = (

    machine_df["Status"] == "NORMAL"

).sum()



plant_health = round(

    healthy / len(machine_df) * 100,

    1

)



# ==========================================================
# KPI DASHBOARD
# ==========================================================

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

show_live_machine_table(

    machine_df

)


st.divider()



# ==========================================================
# FAILURE RISK ANALYSIS
# ==========================================================

st.subheader(

    "📈 AI Failure Risk Analysis"

)


st.bar_chart(

    machine_df

    .set_index("Machine")

    ["Failure Risk (%)"]

)


st.caption(

    "AI predictive engine analysing equipment health in real time."

)


st.divider()



# ==========================================================
# CREATE WORK ORDER
# ==========================================================

st.subheader(

    "➕ Create Work Order"

)


col1, col2 = st.columns(2)



with col1:

    selected_machine = st.selectbox(

        "Machine",

        machine_df["Machine"].tolist()

    )


with col2:

    priority = st.selectbox(

        "Priority",

        [

            "LOW",

            "MEDIUM",

            "HIGH",

            "CRITICAL"

        ]

    )



issue = st.text_area(

    "Issue Description"

)



if st.button(

    "Create Work Order",

    use_container_width=True

):

    if issue.strip():


        create_work_order(

            machine=selected_machine,

            issue=issue,

            priority=priority,

            created_by=user.get(

                "fullname",

                "SYSTEM"

            )

        )


        st.success(

            "Work order created successfully."

        )


        st.rerun()


    else:

        st.warning(

            "Please enter the issue description."

        )


st.divider()
# ==========================================================
# UPDATE WORK ORDER STATUS
# ==========================================================

st.subheader(
    "⚙️ Update Work Order Status"
)


if orders.empty:

    st.info(
        "No work orders available."
    )


else:

    order_id = st.selectbox(

        "Select Work Order",

        orders["id"].tolist(),

        key="maintenance_order"

    )


    new_status = st.selectbox(

        "New Status",

        [

            "PENDING",

            "APPROVED",

            "IN_PROGRESS",

            "COMPLETED",

            "REJECTED"

        ],

        key="maintenance_status"

    )


    if st.button(

        "Update Status",

        use_container_width=True

    ):


        update_work_order_status(

            order_id,

            new_status

        )


        st.success(

            "Work order updated successfully."

        )


        st.rerun()



st.divider()



# ==========================================================
# WORK ORDER TABLE
# ==========================================================

st.subheader(

    "📋 Maintenance Work Orders"

)



if orders.empty:

    st.info(

        "No work orders available."

    )


else:

    st.dataframe(

        orders,

        use_container_width=True,

        hide_index=True

    )



st.divider()



# ==========================================================
# PLANT HEALTH
# ==========================================================

show_plant_health(

    machine_df

)


st.divider()



# ==========================================================
# AI ALERT CENTER
# ==========================================================

show_alert_center(

    machine_df

)



st.divider()



# ==========================================================
# MAINTENANCE SUMMARY
# ==========================================================

st.subheader(

    "🛠 Maintenance Summary"

)



left, right = st.columns(2)



with left:

    st.success(

f"""
📋 Total Work Orders: **{len(orders)}**

🟡 Pending: **{pending}**

✅ Completed: **{completed}**
"""

    )



with right:

    st.info(

f"""
🔴 Critical Machines: **{critical}**

🟡 Warning Machines: **{warning}**

🟢 Healthy Machines: **{healthy}**

💚 Plant Health: **{plant_health:.1f}%**
"""

    )



st.divider()



# ==========================================================
# MAINTENANCE STATUS
# ==========================================================

st.subheader(

    "🟢 Maintenance Status"

)



if critical == 0:


    st.success(

        "Plant equipment is operating normally."

    )


elif critical <= 2:


    st.warning(

        "Maintenance attention is recommended for critical machines."

    )


else:


    st.error(

        "Immediate maintenance intervention is required."

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

st.subheader(

    "👤 Session Information"

)



col1, col2 = st.columns(2)



with col1:


    st.info(

f"""
**User:** {user.get('fullname','Unknown')}

**Role:** {user.get('role','Unknown')}
"""

    )



with col2:


    st.info(

f"""
**Dashboard:** Maintenance Dashboard

**Refresh Interval:** 10 Seconds

**Refresh Count:** {refresh_count}
"""

    )



st.divider()



# ==========================================================
# LIVE SYSTEM STATUS
# ==========================================================

st.subheader(

    "🔧 Live Maintenance System Status"

)



if critical == 0:


    st.success(

        "No critical maintenance issues detected. Equipment health is stable."

    )


elif critical <= 2:


    st.warning(

        "Some equipment requires scheduled maintenance review."

    )


else:


    st.error(

        "Multiple critical machines detected. Immediate maintenance action required."

    )



st.divider()



# ==========================================================
# FOOTER
# ==========================================================

end_page()