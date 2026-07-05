import streamlit as st
from auth.users import verify_user

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Industrial AI Predictive Maintenance",
    page_icon="🏭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# SESSION
# ==========================================================

if "user" not in st.session_state:
    st.session_state.user = {}

# ==========================================================
# ROUTING
# ==========================================================

def route_user():

    user = st.session_state.get("user", {})

    if not isinstance(user, dict):
        st.session_state.user = {}
        return

    role = user.get("role", "")

    routes = {
        "Administrator": "pages/admin_dashboard.py",
        "Maintenance Engineer": "pages/maintenance_dashboard.py",
        "Operations Engineer": "pages/operations_dashboard.py",
        "Supervisor": "pages/supervisor_dashboard.py",
        "Guest": "pages/guest_dashboard.py",
    }

    page = routes.get(role)

    if page:
        st.switch_page(page)

    st.error("Unknown user role.")
    st.session_state.user = {}

# ==========================================================
# AUTO LOGIN
# ==========================================================

if (
    isinstance(st.session_state.user, dict)
    and st.session_state.user.get("role")
):
    route_user()
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

st.title("🏭 Industrial AI Predictive Maintenance")

st.markdown(
"""
### Enterprise Authentication Portal

Welcome to the Industrial AI Predictive Maintenance System.

Please sign in using your enterprise credentials.
"""
)

st.divider()

# ==========================================================
# LOGIN FORM
# ==========================================================

with st.form("login_form"):

    username = st.text_input(
        "Username",
        placeholder="Enter username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password"
    )

    submit = st.form_submit_button(
        "🔐 Sign In",
        use_container_width=True
    )

# ==========================================================
# LOGIN
# ==========================================================

if submit:

    if not username.strip() or not password:

        st.warning("Please enter username and password.")

    else:

        user = verify_user(
            username.strip(),
            password
        )

        if user:

            # ------------------------------------------
            # ALWAYS STORE AS DICTIONARY
            # ------------------------------------------

            if isinstance(user, dict):

                st.session_state.user = {
                    "username": user.get("username", ""),
                    "fullname": user.get("fullname", user.get("username", "User")),
                    "role": user.get("role", "")
                }

            else:
                st.error("Invalid user record.")
                st.stop()

            with st.spinner("Signing in..."):
                route_user()

        else:

            st.error("Invalid username or password.")

# ==========================================================
# DEMO ACCOUNTS
# ==========================================================

st.divider()

with st.expander("👥 Demo Accounts"):

    st.table(
        {
            "Username": [
                "admin",
                "maintenance",
                "operations",
                "supervisor",
                "guest",
            ],
            "Password": [
                "admin123",
                "maint123",
                "ops123",
                "super123",
                "guest123",
            ],
            "Role": [
                "Administrator",
                "Maintenance Engineer",
                "Operations Engineer",
                "Supervisor",
                "Guest",
            ],
        }
    )

# ==========================================================
# SYSTEM INFO
# ==========================================================

with st.expander("ℹ️ System Information"):

    st.markdown(
"""
### Features

- 🤖 AI Failure Prediction
- 🏭 Live Plant Monitoring
- 📊 Predictive Analytics
- 🛠 Smart Maintenance Scheduling
- 👥 Multi-role Access
- 📈 Historical Reports
- 🔒 Secure Authentication
"""
)

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "Industrial AI Predictive Maintenance System • Enterprise Edition"
)