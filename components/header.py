import streamlit as st
from datetime import datetime


def show_header(user, title, subtitle=""):

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

    st.title(title)

    if subtitle:
        st.caption(subtitle)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("User", full_name)

    with col2:
        st.metric("Role", role)

    with col3:
        st.metric(
            "Time",
            datetime.now().strftime("%d %b %Y %H:%M:%S")
        )

    st.divider()