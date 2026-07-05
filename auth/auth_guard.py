import streamlit as st

# ==========================================================
# GET CURRENT USER
# ==========================================================

def get_current_user():
    """
    Returns the logged-in user as a dictionary.
    Always returns a dictionary.
    """

    user = st.session_state.get("user", {})

    if not isinstance(user, dict):
        user = {}

    return user


# ==========================================================
# REQUIRE LOGIN
# ==========================================================

def require_login():
    """
    Ensures a user is logged in.
    Redirects to login page if not.
    """

    user = get_current_user()

    if not user.get("role"):
        st.warning("Please login first.")
        st.switch_page("app.py")
        st.stop()

    return user


# ==========================================================
# REQUIRE ROLE
# ==========================================================

def require_role(allowed_roles):
    """
    Ensures the current user has one of the allowed roles.

    Example:
        user = require_role([
            "Administrator",
            "Supervisor"
        ])
    """

    user = require_login()

    role = user.get("role", "")

    if role not in allowed_roles:

        st.error("⛔ Access Denied")

        st.stop()

    return user


# ==========================================================
# USER HELPERS
# ==========================================================

def get_username():

    return get_current_user().get(
        "username",
        "Unknown"
    )


def get_fullname():

    user = get_current_user()

    return (
        user.get("fullname")
        or user.get("name")
        or user.get("username")
        or "User"
    )


def get_role():

    return get_current_user().get(
        "role",
        "Unknown"
    )


# ==========================================================
# LOGOUT
# ==========================================================

def logout():

    st.session_state.user = {}

    st.switch_page("app.py")