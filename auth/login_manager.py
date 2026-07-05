import streamlit as st

# ----------------------------------------------------
# LOGIN STATUS
# ----------------------------------------------------

def is_logged_in():

    return (
        "user" in st.session_state
        and st.session_state.user is not None
    )

# ----------------------------------------------------
# CURRENT USER
# ----------------------------------------------------

def current_user():

    if is_logged_in():

        return st.session_state.user

    return None

# ----------------------------------------------------
# CURRENT ROLE
# ----------------------------------------------------

def current_role():

    user = current_user()

    if user:

        return user["role"]

    return None

# ----------------------------------------------------
# LOGOUT
# ----------------------------------------------------

def logout():

    st.session_state.user = None

# ----------------------------------------------------
# REQUIRE LOGIN
# ----------------------------------------------------

def require_login():

    if not is_logged_in():

        st.error("Please login first.")

        st.stop()