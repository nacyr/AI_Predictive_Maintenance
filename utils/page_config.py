import streamlit as st

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer

from utils.auth_guard import require_role


# ==========================================================
# ENTERPRISE PAGE SETUP
# ==========================================================

def setup_page(
    title: str,
    icon: str,
    allowed_roles: list[str],
    subtitle: str = "",
):
    """
    Standard page initialization.

    Returns
    -------
    user : dict
        Logged-in user.
    """

    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide"
    )

    user = require_role(allowed_roles)

    show_header(
        user=user,
        title=title,
        subtitle=subtitle
    )

    show_sidebar(user)

    return user


# ==========================================================
# STANDARD FOOTER
# ==========================================================

def end_page():

    st.divider()

    show_footer()