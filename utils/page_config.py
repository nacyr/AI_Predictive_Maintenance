import streamlit as st
from datetime import datetime


# ==========================================================
# PAGE SETUP (SAFE GLOBAL GUARD)
# ==========================================================

def setup_page(title, icon, allowed_roles=None, subtitle=None):

    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide"
    )

    # ------------------------------------------------------
    # SESSION SAFE INIT
    # ------------------------------------------------------

    user = st.session_state.get("user", {})

    if not isinstance(user, dict):
        user = {}

    role = user.get("role", "")

    allowed_roles = allowed_roles or []

    # ------------------------------------------------------
    # ROLE CHECK
    # ------------------------------------------------------

    if allowed_roles and role not in allowed_roles:

        st.error("Access Denied")
        st.stop()

    # ------------------------------------------------------
    # HEADER BLOCK (SAFE)
    # ------------------------------------------------------

    st.markdown(
        f"""
        # {icon} {title}

        {subtitle or ""}

        ---
        """
    )

    # ------------------------------------------------------
    # SESSION INFO (SAFE DISPLAY)
    # ------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.info(f"👤 User: {user.get('fullname', 'Unknown')}")
    col2.info(f"🎭 Role: {role or 'Unknown'}")
    col3.info(f"🕒 {datetime.now().strftime('%d %b %Y %H:%M:%S')}")

    st.divider()

    return user


# ==========================================================
# END PAGE
# ==========================================================

def end_page():

    st.divider()

    st.caption(
        "Industrial AI Predictive Maintenance System • Enterprise Edition"
    )