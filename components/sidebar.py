import streamlit as st


def show_sidebar(user):

    if user is None:
        user = {}

    full_name = (
        user.get("fullname")
        or user.get("full_name")
        or user.get("name")
        or user.get("username")
        or "User"
    )

    username = user.get("username", "-")
    role = user.get("role", "Unknown")

    with st.sidebar:

        st.title("🏭 Navigation")

        st.divider()

        st.subheader("Current User")

        st.write(f"**Name:** {full_name}")
        st.write(f"**Username:** {username}")
        st.write(f"**Role:** {role}")

        st.divider()

        st.success("System Status: Online")