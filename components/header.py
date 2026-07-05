import streamlit as st
from datetime import datetime


# ==========================================================
# HEADER
# ==========================================================

def show_header(user, title, subtitle=""):

    # --------------------------------------------
    # Safe user extraction
    # --------------------------------------------

    if not isinstance(user, dict):
        user = {}

    fullname = (
        user.get("fullname")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    role = user.get("role", "Unknown")

    now = datetime.now()

    # --------------------------------------------
    # Title
    # --------------------------------------------

    st.title(title)

    if subtitle:
        st.caption(subtitle)

    st.divider()

    # --------------------------------------------
    # Information cards
    # --------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "User",
            fullname
        )

    with c2:
        st.metric(
            "Role",
            role
        )

    with c3:
        st.metric(
            "Time",
            now.strftime("%d %b %Y %H:%M:%S")
        )

    st.divider()