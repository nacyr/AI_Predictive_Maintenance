import streamlit as st


# ==========================================================
# SIDEBAR
# ==========================================================

def show_sidebar(user):

    if not isinstance(user, dict):
        user = {}

    fullname = (
        user.get("fullname")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    role = user.get("role", "Unknown")

    with st.sidebar:

        st.title("🏭 AI Predictive Maintenance")

        st.divider()

        st.write(f"**User:** {fullname}")
        st.write(f"**Role:** {role}")

        st.divider()

        st.subheader("Navigation")

        pages = [
            ("🏠 Admin Dashboard", "pages/admin_dashboard.py"),
            ("🔧 Maintenance", "pages/maintenance_dashboard.py"),
            ("⚙️ Operations", "pages/operations_dashboard.py"),
            ("👤 Guest", "pages/guest_dashboard.py"),
            ("📊 Analytics", "pages/analytics.py"),
            ("🤖 Prediction", "pages/prediction.py"),
            ("🛠 Work Orders", "pages/maintenance_work_orders.py"),
        ]

        for label, page in pages:
            if st.button(label, use_container_width=True):
                st.switch_page(page)

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            st.session_state.user = {}
            st.switch_page("app.py")