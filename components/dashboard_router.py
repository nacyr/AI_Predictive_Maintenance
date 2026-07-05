import streamlit as st


def route_dashboard(user):
    """
    Routes user to correct dashboard based on role.
    """

    role = user.get("role")

    if role == "Administrator":
        st.switch_page("pages/admin_dashboard.py")

    elif role == "Maintenance Engineer":
        st.switch_page("pages/maintenance_dashboard.py")

    elif role == "Operations Engineer":
        st.switch_page("pages/operations_dashboard.py")

    elif role == "Supervisor":
        st.switch_page("pages/supervisor_dashboard.py")

    else:
        st.switch_page("pages/guest_dashboard.py")