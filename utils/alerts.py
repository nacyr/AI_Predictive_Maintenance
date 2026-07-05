import streamlit as st


# ==========================================================
# SIMPLE ALERTS
# ==========================================================

def success(message):
    st.success(message)


def warning(message):
    st.warning(message)


def error(message):
    st.error(message)


def info(message):
    st.info(message)


# ==========================================================
# MACHINE HEALTH ALERT
# ==========================================================

def machine_status(critical, warning_count=0):

    if critical == 0:

        st.success(
            "All monitored equipment is operating normally."
        )

    elif critical <= 2:

        st.warning(
            f"{critical} machine(s) require maintenance attention."
        )

    else:

        st.error(
            f"{critical} critical machine(s) require immediate intervention."
        )

    if warning_count > 0:

        st.info(
            f"{warning_count} machine(s) are currently under observation."
        )


# ==========================================================
# PLANT STATUS ALERT
# ==========================================================

def plant_status(critical, warning_count=0):

    if critical == 0:

        st.success(
            "Industrial plant is operating within safe limits."
        )

    elif critical <= 2:

        st.warning(
            f"{critical} plant unit(s) require inspection."
        )

    else:

        st.error(
            f"{critical} plant unit(s) require immediate maintenance."
        )

    if warning_count > 0:

        st.info(
            f"{warning_count} unit(s) are being monitored."
        )


# ==========================================================
# WORK ORDER ALERT
# ==========================================================

def work_order_summary(stats):

    pending = stats.get("pending", 0)
    approved = stats.get("approved", 0)
    completed = stats.get("completed", 0)
    rejected = stats.get("rejected", 0)

    if pending == 0:

        st.success(
            "No pending work orders."
        )

    else:

        st.warning(
            f"{pending} pending work order(s)."
        )

    if approved > 0:

        st.info(
            f"{approved} approved work order(s)."
        )

    if completed > 0:

        st.success(
            f"{completed} completed work order(s)."
        )

    if rejected > 0:

        st.error(
            f"{rejected} rejected work order(s)."
        )


# ==========================================================
# AI RISK ALERT
# ==========================================================

def ai_prediction(probability):

    probability = float(probability)

    if probability >= 0.80:

        st.error(
            f"Critical failure risk ({probability:.1%}). Immediate action recommended."
        )

    elif probability >= 0.50:

        st.warning(
            f"High failure risk ({probability:.1%}). Schedule maintenance soon."
        )

    elif probability >= 0.20:

        st.info(
            f"Moderate failure risk ({probability:.1%}). Continue monitoring."
        )

    else:

        st.success(
            f"Low failure risk ({probability:.1%}). Machine operating normally."
        )


# ==========================================================
# EMPTY DATASET
# ==========================================================

def no_data(message="No data available."):

    st.info(message)


# ==========================================================
# ACCESS DENIED
# ==========================================================

def access_denied():

    st.error(
        "You do not have permission to access this page."
    )

    st.stop()


# ==========================================================
# DATABASE ERROR
# ==========================================================

def database_error():

    st.error(
        "Unable to load data from the database."
    )


# ==========================================================
# COMING SOON
# ==========================================================

def coming_soon(feature):

    st.info(
        f"{feature} will be available in a future version."
    )