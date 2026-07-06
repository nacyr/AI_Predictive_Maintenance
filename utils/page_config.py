import streamlit as st
from datetime import datetime

# ==========================================================
# PAGE SETUP
# ==========================================================

def setup_page(
    title,
    icon,
    allowed_roles=None,
    subtitle=None
):

    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide"
    )

    # ======================================================
    # LOGIN CHECK
    # ======================================================

    if "user" not in st.session_state:

        st.warning("Please login first.")

        st.switch_page("app.py")

        st.stop()

    user = st.session_state.user

    if not isinstance(user, dict):

        st.session_state.clear()

        st.switch_page("app.py")

        st.stop()

    # ======================================================
    # ROLE CHECK
    # ======================================================

    allowed_roles = allowed_roles or []

    role = user.get("role", "")

    if allowed_roles and role not in allowed_roles:

        st.error("⛔ Access Denied")

        st.stop()

    # ======================================================
    # PAGE HEADER
    # ======================================================

    left, right = st.columns([8, 2])

    with left:

        st.markdown(f"""
# {icon} {title}

{subtitle or ""}
""")

    with right:

        st.write("")

        st.write("")

        if st.button(
            "🚪 Logout",
            use_container_width=True,
            type="secondary"
        ):

            st.session_state.clear()

            st.success("Logged out successfully.")

            st.switch_page("app.py")

            st.stop()

    st.divider()

    # ======================================================
    # SESSION INFORMATION
    # ======================================================

    c1, c2, c3 = st.columns(3)

    with c1:

        st.info(
            f"👤 **User**\n\n{user.get('fullname','Unknown')}"
        )

    with c2:

        st.info(
            f"🎭 **Role**\n\n{role}"
        )

    with c3:

        st.info(
            f"🕒 **Current Time**\n\n{datetime.now().strftime('%d %b %Y %H:%M:%S')}"
        )

    st.divider()

    return user


# ==========================================================
# FOOTER
# ==========================================================

def end_page():

    st.divider()

    st.caption(
        "🏭 Industrial AI Predictive Maintenance System • Enterprise Edition v1.0"
    )