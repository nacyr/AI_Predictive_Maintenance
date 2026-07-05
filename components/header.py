import streamlit as st
from datetime import datetime


# ==========================================================
# ENTERPRISE HEADER
# ==========================================================

def show_header(user, title, subtitle=""):

    # ------------------------------------------------------
    # SAFE USER DETAILS
    # ------------------------------------------------------

    if user is None:
        user = {}

    full_name = (
        user.get("fullname")
        or user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    role = user.get("role", "Unknown")

    current_time = datetime.now().strftime("%d %B %Y  %H:%M:%S")

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            background:#0E1117;
            padding:20px;
            border-radius:12px;
            border:1px solid #31333F;
            margin-bottom:15px;
        ">

        <h2 style="margin:0;color:white;">
            {title}
        </h2>

        <p style="margin-top:6px;color:#BBBBBB;font-size:16px;">
            {subtitle}
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------
    # USER INFORMATION
    # ------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"👤 **User:** {full_name}")

    with col2:
        st.info(f"🛡️ **Role:** {role}")

    with col3:
        st.info(f"🕒 **Time:** {current_time}")

    st.divider()