import streamlit as st
from auth.users import verify_user

# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Industrial AI Predictive Maintenance",
    page_icon="🏭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# INITIALIZE SESSION
# ==========================================================

if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================================
# ROLE ROUTING
# ==========================================================

def route_user(user):

    role = user.get("role", "")

    routes = {
        "Administrator": "pages/admin_dashboard.py",
        "Maintenance Engineer": "pages/maintenance_dashboard.py",
        "Operations Engineer": "pages/operations_dashboard.py",
        "Supervisor": "pages/supervisor_dashboard.py",
        "Guest": "pages/guest_dashboard.py"
    }

    page = routes.get(role)

    if page:
        st.switch_page(page)

    st.error(f"Unknown user role: {role}")
    st.session_state.user = None
    st.stop()


# ==========================================================
# AUTO LOGIN
# ==========================================================

if st.session_state.user is not None:
    route_user(st.session_state.user)
    st.stop()

# ==========================================================
# PAGE HEADER
# ==========================================================

st.title("🏭 Industrial AI Predictive Maintenance")

st.markdown("""
### Enterprise Authentication Portal

Welcome to the **Industrial AI Predictive Maintenance System**.

Please sign in with your authorized enterprise credentials to access your dashboard.
""")

st.divider()

# ==========================================================
# LOGIN FORM
# ==========================================================

with st.form("login_form", clear_on_submit=False):

    username = st.text_input(
        "Username",
        placeholder="Enter your username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    login = st.form_submit_button(
        "🔐 Sign In",
        use_container_width=True
    )

# ==========================================================
# LOGIN PROCESS
# ==========================================================

if login:

    username = username.strip()

    if username == "" or password == "":

        st.warning("Please enter both username and password.")

    else:

        user = verify_user(username, password)

        if user:

            st.session_state.user = user

            with st.spinner("Signing in..."):
                route_user(user)

        else:

            st.error("Invalid username or password.")

# ==========================================================
# DEMO ACCOUNTS
# ==========================================================

st.divider()

with st.expander("👥 Demo Accounts"):

    st.table({
        "Username": [
            "admin",
            "maintenance",
            "operations",
            "supervisor",
            "guest"
        ],
        "Password": [
            "admin123",
            "maint123",
            "ops123",
            "super123",
            "guest123"
        ],
        "Role": [
            "Administrator",
            "Maintenance Engineer",
            "Operations Engineer",
            "Supervisor",
            "Guest"
        ]
    })

# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

with st.expander("ℹ️ System Information"):

    st.markdown("""
### Features

- 🤖 AI Failure Prediction
- 🏭 Live Industrial Monitoring
- 📊 Predictive Analytics
- 🛠 Smart Maintenance Scheduling
- 👥 Multi-Role Access Control
- 📈 Historical Performance Reports
- 🔒 Secure Enterprise Authentication

Each user is automatically redirected to their assigned dashboard after successful authentication.
""")

# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "Industrial AI Predictive Maintenance System • Enterprise Edition v2.0 • Powered by Streamlit & Machine Learning"
)