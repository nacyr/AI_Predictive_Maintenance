import streamlit as st


# ==========================================================
# SAFE IMPORT WRAPPER
# ==========================================================

def safe_import(module_name, attr_name=None, fallback=None):

    try:
        module = __import__(module_name, fromlist=["*"])

        if attr_name:
            return getattr(module, attr_name, fallback)

        return module

    except Exception:
        return fallback


# ==========================================================
# SAFE DATAFRAME HANDLER
# ==========================================================

def safe_df(df):

    try:
        import pandas as pd

        if df is None:
            return pd.DataFrame()

        if hasattr(df, "empty") and df.empty:
            return pd.DataFrame()

        return df

    except Exception:
        return None


# ==========================================================
# SAFE SESSION USER
# ==========================================================

def get_user():

    user = st.session_state.get("user", {})

    if not isinstance(user, dict):
        return {}

    return user


# ==========================================================
# SAFE ROLE CHECK
# ==========================================================

def require_role(allowed_roles):

    user = get_user()
    role = user.get("role", "")

    if role not in allowed_roles:
        st.error("Access Denied")
        st.stop()

    return user


# ==========================================================
# SAFE PAGE START WRAPPER
# ==========================================================

def start_page(title):

    st.title(title)
    st.divider()