import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import streamlit as st
from auth.users import verify_user

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Industrial AI Login",
    page_icon="🏭",
    layout="centered"
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    st.switch_page("pages/admin_dashboard.py")


# ==========================================================
# IMPROVED INDUSTRIAL CSS
# ==========================================================

st.markdown(
    """
    <style>

    /* Background */
    .stApp {
        background: radial-gradient(circle at top, #0f172a, #0b1220, #050814);
        color: #ffffff;
    }

    /* Glass login card */
    .login-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 38px 35px;
        border-radius: 18px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.55);
        backdrop-filter: blur(14px);
    }

    /* Title */
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 18px;
    }

    /* Divider spacing */
    hr {
        margin: 18px 0;
        border: none;
        border-top: 1px solid rgba(255,255,255,0.08);
    }

    /* Input fields (safer targeting) */
    div[data-baseweb="input"] {
        background-color: #0f172a !important;
        border-radius: 10px;
    }

    /* Input text */
    input {
        color: white !important;
    }

    /* Labels */
    label {
        color: #cbd5e1 !important;
        font-size: 13px !important;
    }

    /* Button */
    .stButton button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px;
        border: none;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.25);
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.35);
    }

    /* Expander */
    .streamlit-expanderHeader {
        color: #cbd5e1;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# CENTER LAYOUT
# ==========================================================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    st.markdown('<div class="title">🏭 Industrial AI System</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="subtitle">Predictive Maintenance Control Portal</div>',
        unsafe_allow_html=True
    )

    st.write("Secure access required to continue")
    st.markdown("<hr>", unsafe_allow_html=True)


    # ======================================================
    # LOGIN FORM
    # ======================================================

    with st.form("login_form"):

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        login_btn = st.form_submit_button("🔐 Access System", use_container_width=True)


    # ======================================================
    # LOGIN LOGIC
    # ======================================================

    if login_btn:

        if not username or not password:
            st.warning("Both fields are required.")

        else:
            user = verify_user(username.strip(), password)

            if user:

                st.session_state.user = user

                st.success(f"Welcome {user['fullname']} 👋")

                st.switch_page("pages/admin_dashboard.py")

            else:
                st.error("Invalid credentials. Try again.")


    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# DEMO ACCOUNTS
# ==========================================================

st.markdown("---")

with st.expander("🧪 Demo Accounts (Testing Only)"):

    st.markdown(
        """
        | Username | Password | Role |
        |----------|----------|------|
        | admin | admin123 | Administrator |
        | maintenance | maint123 | Engineer |
        | operations | ops123 | Operator |
        | supervisor | super123 | Supervisor |
        | guest | guest123 | Viewer |
        """
    )