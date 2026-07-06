import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# PROJECT ROOT
# ==========================================================

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# ==========================================================
# AUTO REFRESH (IMPORTANT FIX)
# ==========================================================

st_autorefresh(interval=10000, key="user_management_refresh")

# ==========================================================
# IMPORTS
# ==========================================================

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer

from database.users import (
    get_users,
    add_user,
    delete_user,
    update_user,
    update_status,
    reset_password
)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="User Management",
    page_icon="👥",
    layout="wide"
)

# ==========================================================
# LOGIN CHECK
# ==========================================================

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Please login first.")
    st.switch_page("app.py")
    st.stop()

user = st.session_state.user

if user["role"] != "Administrator":
    st.error("Administrator access required.")
    st.stop()

# ==========================================================
# HEADER
# ==========================================================

show_header(
    user,
    "👥 User Management",
    "Enterprise Identity & Access Management"
)

show_sidebar(user)

# ==========================================================
# LOAD USERS (AUTO REFRESHED)
# ==========================================================

try:
    users_df = get_users().copy()

    users_df.rename(
        columns={
            "id": "ID",
            "username": "Username",
            "fullname": "Full Name",
            "role": "Role",
            "email": "Email",
            "status": "Status",
            "created_at": "Created At",
            "last_login": "Last Login"
        },
        inplace=True
    )

except Exception as e:
    st.error(f"Unable to load users: {e}")
    users_df = pd.DataFrame(
        columns=[
            "ID",
            "Username",
            "Full Name",
            "Role",
            "Email",
            "Status",
            "Created At",
            "Last Login"
        ]
    )

# ==========================================================
# KPI DASHBOARD
# ==========================================================

st.subheader("📊 User Statistics")

total_users = len(users_df)

active_users = users_df["Status"].eq("Active").sum() if not users_df.empty else 0
disabled_users = users_df["Status"].eq("Disabled").sum() if not users_df.empty else 0

role_counts = users_df["Role"].value_counts() if not users_df.empty else {}

administrators = role_counts.get("Administrator", 0)
maintenance = role_counts.get("Maintenance Engineer", 0)
operations = role_counts.get("Operations Engineer", 0)
supervisors = role_counts.get("Supervisor", 0)
guests = role_counts.get("Guest", 0)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Users", total_users)
c2.metric("Active", active_users)
c3.metric("Disabled", disabled_users)
c4.metric("Administrators", administrators)

c5, c6, c7 = st.columns(3)
c5.metric("Maintenance", maintenance)
c6.metric("Operations", operations)
c7.metric("Supervisors", supervisors)

st.divider()

# ==========================================================
# CREATE USER
# ==========================================================

st.subheader("➕ Create New User")

with st.form("create_user_form"):
    left, right = st.columns(2)

    with left:
        username = st.text_input("Username")
        fullname = st.text_input("Full Name")
        password = st.text_input("Password", type="password")

    with right:
        email = st.text_input("Email")
        role = st.selectbox(
            "Role",
            [
                "Administrator",
                "Maintenance Engineer",
                "Operations Engineer",
                "Supervisor",
                "Guest"
            ]
        )

    create = st.form_submit_button("Create User")

if create:
    if not username.strip():
        st.warning("Username is required.")
    elif not fullname.strip():
        st.warning("Full name is required.")
    elif not password:
        st.warning("Password is required.")
    else:
        success = add_user(
            username.strip(),
            password,
            fullname.strip(),
            role,
            email.strip()
        )

        if success:
            st.success("User created successfully.")
            st.rerun()
        else:
            st.error("Username already exists.")

st.divider()

# ==========================================================
# SEARCH & FILTER
# ==========================================================

st.subheader("🔍 Search & Filter Users")

left, right = st.columns(2)

with left:
    search = st.text_input("Search Username or Full Name")

with right:
    role_options = ["ALL"]
    if not users_df.empty:
        role_options += sorted(users_df["Role"].dropna().unique().tolist())

    role_filter = st.selectbox("Filter by Role", role_options)

filtered = users_df.copy()

if not filtered.empty:
    if search.strip():
        keyword = search.lower()
        filtered = filtered[
            filtered["Username"].str.lower().str.contains(keyword, na=False)
            |
            filtered["Full Name"].str.lower().str.contains(keyword, na=False)
        ]

    if role_filter != "ALL":
        filtered = filtered[filtered["Role"] == role_filter]

# ==========================================================
# USERS TABLE
# ==========================================================

st.subheader("📋 Registered Users")

if filtered.empty:
    st.info("No users found.")
else:
    st.dataframe(filtered, use_container_width=True, hide_index=True)

# ==========================================================
# SYSTEM STATUS (AUTO UPDATING PART)
# ==========================================================

st.divider()
st.info(f"""
### Live System Status (Auto Refresh Enabled)

**Total Users:** {total_users}  
**Active:** {active_users}  
**Disabled:** {disabled_users}  

⏱ Refresh cycle: 10 seconds
""")

# ==========================================================
# FOOTER
# ==========================================================

show_footer()