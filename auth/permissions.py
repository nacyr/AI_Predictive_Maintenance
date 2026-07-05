import streamlit as st

# -------------------------------------------------------
# ROLE PERMISSIONS
# -------------------------------------------------------

ROLE_PERMISSIONS = {

    "Administrator": [
        "dashboard",
        "analytics",
        "prediction",
        "users"
    ],

    "Maintenance Engineer": [
        "dashboard",
        "analytics",
        "prediction"
    ],

    "Operations Engineer": [
        "dashboard"
    ],

    "Supervisor": [
        "dashboard",
        "analytics"
    ],

    "Guest": [
        "dashboard"
    ]
}

# -------------------------------------------------------
# CHECK LOGIN
# -------------------------------------------------------

def require_login():

    if "user" not in st.session_state:

        st.warning("Please login first.")

        st.stop()

    if st.session_state.user is None:

        st.warning("Please login first.")

        st.stop()

# -------------------------------------------------------
# CHECK PERMISSION
# -------------------------------------------------------

def require_permission(page):

    require_login()

    role = st.session_state.user["role"]

    allowed_pages = ROLE_PERMISSIONS.get(role, [])

    if page not in allowed_pages:

        st.error("🚫 Access Denied")

        st.info(
            "You do not have permission to access this page."
        )

        st.stop()