import streamlit as st


# ==========================================================
# PAGE ROUTES (CENTRALIZED)
# ==========================================================

ROUTES = {
    "admin": "pages/admin_dashboard.py",
    "engineer": "pages/engineer_dashboard.py",
    "maintenance": "pages/maintenance_dashboard.py",
    "maintenance_work_orders": "pages/maintenance_work_orders.py",
    "operations": "pages/operations_dashboard.py",
    "supervisor": "pages/supervisor_dashboard.py",
    "prediction": "pages/prediction.py",
    "analytics": "pages/analytics.py",
}


# ==========================================================
# SAFE NAVIGATOR
# ==========================================================

def go_to(page_key: str):

    if page_key not in ROUTES:
        st.error(f"Unknown route: {page_key}")
        return

    st.switch_page(ROUTES[page_key])


# ==========================================================
# ROLE-BASED REDIRECT
# ==========================================================

def route_by_role(user: dict):

    if not isinstance(user, dict):
        st.error("Invalid user session")
        st.stop()

    role = user.get("role", "")

    mapping = {
        "Administrator": "admin",
        "Maintenance Engineer": "engineer",
        "Operations Engineer": "operations",
        "Supervisor": "supervisor",
        "Guest": "maintenance_work_orders",
    }

    page_key = mapping.get(role)

    if not page_key:
        st.error(f"Unknown role: {role}")
        st.stop()

    go_to(page_key)


# ==========================================================
# QUICK BUTTON NAVIGATION HELPERS
# ==========================================================

def nav_button(label: str, page_key: str):

    if st.button(label, use_container_width=True):
        go_to(page_key)