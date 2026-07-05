import streamlit as st


# ==========================================================
# PAGE ROUTES
# ==========================================================

PAGE_ROUTES = {
    "Admin Dashboard": "pages/admin_dashboard.py",
    "Maintenance Dashboard": "pages/maintenance_dashboard.py",
    "Engineer Dashboard": "pages/engineer_dashboard.py",
    "Operations Dashboard": "pages/operations_dashboard.py",
    "Supervisor Dashboard": "pages/supervisor_dashboard.py",
    "Guest Dashboard": "pages/guest_dashboard.py",
    "Prediction": "pages/prediction.py",
    "Analytics": "pages/analytics.py",
    "Work Orders": "pages/maintenance_work_orders.py",
    "History": "pages/history.py",
}


# ==========================================================
# NAVIGATION BUTTON
# ==========================================================

def navigation_button(label, page, icon=None, disabled=False):
    """
    Create a single navigation button.

    Example:
        navigation_button("Prediction", "Prediction", "🤖")
    """

    text = f"{icon} {label}" if icon else label

    if st.button(
        text,
        width="stretch",
        disabled=disabled,
        key=f"nav_{page}_{label}"
    ):
        st.switch_page(PAGE_ROUTES[page])


# ==========================================================
# QUICK NAVIGATION ROW
# ==========================================================

def quick_navigation(buttons):
    """
    Display navigation buttons in columns.

    Example:

    quick_navigation([
        ("Prediction", "Prediction", "🤖"),
        ("Analytics", "Analytics", "📈"),
        ("Work Orders", "Work Orders", "🛠"),
        ("Dashboard", "Admin Dashboard", "🏠")
    ])
    """

    if not buttons:
        return

    st.subheader("⚡ Quick Navigation")

    cols = st.columns(len(buttons))

    for col, item in zip(cols, buttons):

        label = item[0]
        page = item[1]

        icon = item[2] if len(item) > 2 else None
        disabled = item[3] if len(item) > 3 else False

        with col:
            navigation_button(
                label,
                page,
                icon,
                disabled
            )


# ==========================================================
# SIDEBAR NAVIGATION
# ==========================================================

def sidebar_navigation(buttons):
    """
    Display navigation buttons inside the sidebar.

    Example:

    with st.sidebar:
        sidebar_navigation([
            ("Dashboard","Admin Dashboard","🏠"),
            ("Prediction","Prediction","🤖")
        ])
    """

    st.sidebar.markdown("## 📂 Navigation")

    for item in buttons:

        label = item[0]
        page = item[1]

        icon = item[2] if len(item) > 2 else None
        disabled = item[3] if len(item) > 3 else False

        text = f"{icon} {label}" if icon else label

        if st.sidebar.button(
            text,
            width="stretch",
            disabled=disabled,
            key=f"sidebar_{page}_{label}"
        ):
            st.switch_page(PAGE_ROUTES[page])


# ==========================================================
# GO TO DASHBOARD
# ==========================================================

def go_home(role):
    """
    Redirect a user to the correct dashboard.
    """

    routes = {
        "Administrator": "Admin Dashboard",
        "Maintenance Engineer": "Maintenance Dashboard",
        "Engineer": "Engineer Dashboard",
        "Operations Engineer": "Operations Dashboard",
        "Supervisor": "Supervisor Dashboard",
        "Guest": "Guest Dashboard",
    }

    dashboard = routes.get(role)

    if dashboard:
        st.switch_page(PAGE_ROUTES[dashboard])