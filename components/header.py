import streamlit as st
from datetime import datetime


# ==========================================================
# ENTERPRISE HEADER
# ==========================================================

def show_header(user, title, subtitle):

    st.title(title)
    st.caption(subtitle)

    st.divider()

    left, center, right = st.columns([4, 2, 1])

    # ------------------------------------------------------
    # LEFT
    # ------------------------------------------------------

    with left:

        st.markdown(f"""
### {subtitle}

🗓 **Date:** {datetime.now().strftime("%A, %d %B %Y")}

🕒 **Time:** {datetime.now().strftime("%H:%M:%S")}
""")

    # ------------------------------------------------------
    # CENTER
    # ------------------------------------------------------

    with center:

        st.info(f"""
### Current User

👤 **{user['fullname']}**

🛡 **Role:** {user['role']}

🟢 System Online
""")

    # ------------------------------------------------------
    # RIGHT
    # ------------------------------------------------------

    with right:

        st.write("")

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.user = None

            st.success("Logged out successfully.")

            st.switch_page("app.py")

    st.divider()