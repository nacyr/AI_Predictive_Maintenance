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
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="user_management_refresh"
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
# LOAD USERS
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

active_users = (
    users_df["Status"]
    .eq("Active")
    .sum()
    if not users_df.empty else 0
)

disabled_users = (
    users_df["Status"]
    .eq("Disabled")
    .sum()
    if not users_df.empty else 0
)

administrators = (
    users_df["Role"]
    .eq("Administrator")
    .sum()
    if not users_df.empty else 0
)

maintenance = (
    users_df["Role"]
    .eq("Maintenance Engineer")
    .sum()
    if not users_df.empty else 0
)

operations = (
    users_df["Role"]
    .eq("Operations Engineer")
    .sum()
    if not users_df.empty else 0
)

supervisors = (
    users_df["Role"]
    .eq("Supervisor")
    .sum()
    if not users_df.empty else 0
)

guests = (
    users_df["Role"]
    .eq("Guest")
    .sum()
    if not users_df.empty else 0
)

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
        password = st.text_input(
            "Password",
            type="password"
        )

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

    create = st.form_submit_button(
        "Create User",
        width="stretch"
    )

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

    search = st.text_input(
        "Search Username or Full Name"
    )

with right:

    role_options = ["ALL"]

    if not users_df.empty:

        role_options += sorted(
            users_df["Role"].dropna().unique().tolist()
        )

    role_filter = st.selectbox(
        "Filter by Role",
        role_options
    )

filtered = users_df.copy()

if not filtered.empty:

    if search.strip():

        keyword = search.lower()

        filtered = filtered[
            filtered["Username"].str.lower().str.contains(
                keyword,
                na=False
            )
            |
            filtered["Full Name"].str.lower().str.contains(
                keyword,
                na=False
            )
        ]

    if role_filter != "ALL":

        filtered = filtered[
            filtered["Role"] == role_filter
        ]

# ==========================================================
# REGISTERED USERS
# ==========================================================

st.subheader("📋 Registered Users")

if filtered.empty:

    st.info("No users found.")

else:

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "⬇ Export Users",
        filtered.to_csv(index=False),
        file_name="registered_users.csv",
        mime="text/csv",
        width="stretch"
    )

st.divider()

# ==========================================================
# USER MANAGEMENT
# ==========================================================

st.subheader("⚙ User Management")

if filtered.empty:

    st.info("No users available.")

else:

    usernames = filtered["Username"].tolist()

    selected_username = st.selectbox(
        "Select User",
        usernames
    )

    selected = filtered[
        filtered["Username"] == selected_username
    ].iloc[0]

    user_id = int(selected["ID"])

    st.info(f"""
Username: **{selected['Username']}**

Full Name: **{selected['Full Name']}**

Role: **{selected['Role']}**

Status: **{selected['Status']}**
""")

# ==========================================================
# EDIT USER
# ==========================================================

st.subheader("✏ Edit User")

with st.form("edit_user_form"):

    edit_name = st.text_input(
        "Full Name",
        value=selected["Full Name"]
    )

    edit_email = st.text_input(
        "Email",
        value="" if pd.isna(selected["Email"]) else selected["Email"]
    )

    edit_role = st.selectbox(
        "Role",
        [
            "Administrator",
            "Maintenance Engineer",
            "Operations Engineer",
            "Supervisor",
            "Guest"
        ],
        index=[
            "Administrator",
            "Maintenance Engineer",
            "Operations Engineer",
            "Supervisor",
            "Guest"
        ].index(selected["Role"])
    )

    save_changes = st.form_submit_button(
        "💾 Save Changes",
        width="stretch"
    )

if save_changes:

    update_user(
        user_id,
        edit_name,
        edit_role,
        edit_email
    )

    st.success("User updated successfully.")

    st.rerun()

st.divider()
# ==========================================================
# ACCOUNT ACTIONS
# ==========================================================

st.subheader("🔧 Account Actions")

c1, c2, c3, c4 = st.columns(4)

# ==========================================================
# ENABLE USER
# ==========================================================

with c1:

    if st.button(
        "✅ Enable User",
        width="stretch"
    ):

        update_status(
            user_id,
            "Active"
        )

        st.success("User enabled successfully.")

        st.rerun()

# ==========================================================
# DISABLE USER
# ==========================================================

with c2:

    if st.button(
        "🚫 Disable User",
        width="stretch"
    ):

        if selected["Username"] == user["username"]:

            st.error(
                "You cannot disable your own account."
            )

        else:

            update_status(
                user_id,
                "Disabled"
            )

            st.success("User disabled successfully.")

            st.rerun()

# ==========================================================
# RESET PASSWORD
# ==========================================================

with c3:

    if st.button(
        "🔑 Reset Password",
        width="stretch"
    ):

        reset_password(
            user_id,
            "password123"
        )

        st.success("""
Password has been reset successfully.

Default Password:

password123
""")

# ==========================================================
# DELETE USER
# ==========================================================

with c4:

    confirm_delete = st.checkbox(
        "Confirm Delete"
    )

    if st.button(
        "🗑 Delete User",
        width="stretch"
    ):

        if not confirm_delete:

            st.warning(
                "Please confirm deletion."
            )

        elif selected["Username"] == user["username"]:

            st.error(
                "You cannot delete your own account."
            )

        else:

            admin_count = (
                users_df["Role"] == "Administrator"
            ).sum()

            if (
                selected["Role"] == "Administrator"
                and admin_count <= 1
            ):

                st.error(
                    "Cannot delete the last Administrator."
                )

            else:

                delete_user(user_id)

                st.success(
                    "User deleted successfully."
                )

                st.rerun()

st.divider()

# ==========================================================
# USER ANALYTICS
# ==========================================================

st.subheader("📊 User Analytics")

if users_df.empty:

    st.info("No users available.")

else:

    left, right = st.columns(2)

    with left:

        st.markdown("#### Users by Role")

        st.bar_chart(
            users_df["Role"].value_counts()
        )

    with right:

        st.markdown("#### Users by Status")

        st.bar_chart(
            users_df["Status"].value_counts()
        )

st.divider()

# ==========================================================
# SYSTEM HEALTH
# ==========================================================

st.subheader("🟢 Identity Management Status")

if total_users == 0:

    st.warning(
        "No registered users found."
    )

elif disabled_users == 0:

    st.success(
        "All user accounts are active."
    )

elif disabled_users < total_users / 3:

    st.warning(
        f"{disabled_users} account(s) are disabled."
    )

else:

    st.error(
        "Large number of user accounts are disabled."
    )

st.divider()
# ==========================================================
# SYSTEM SUMMARY
# ==========================================================

st.subheader("📋 System Summary")

summary_df = pd.DataFrame(
    {
        "Metric": [
            "Total Users",
            "Active Users",
            "Disabled Users",
            "Administrators",
            "Maintenance Engineers",
            "Operations Engineers",
            "Supervisors",
            "Guests"
        ],
        "Value": [
            total_users,
            active_users,
            disabled_users,
            administrators,
            maintenance,
            operations,
            supervisors,
            guests
        ]
    }
)

st.dataframe(
    summary_df,
    width="stretch",
    hide_index=True
)

st.divider()

# ==========================================================
# QUICK ACTIONS
# ==========================================================

st.subheader("⚡ Quick Actions")

q1, q2, q3, q4 = st.columns(4)

with q1:

    if st.button(
        "➕ Create Another User",
        width="stretch"
    ):
        st.rerun()

with q2:

    if st.button(
        "🔄 Refresh Users",
        width="stretch"
    ):
        st.rerun()

with q3:

    st.download_button(
        "⬇ Download CSV",
        users_df.to_csv(index=False),
        file_name="users_export.csv",
        mime="text/csv",
        width="stretch"
    )

with q4:

    st.metric(
        "Registered Users",
        len(users_df)
    )

st.divider()

# ==========================================================
# USER DIRECTORY
# ==========================================================

with st.expander("👥 Complete User Directory", expanded=False):

    if users_df.empty:

        st.info("No registered users.")

    else:

        display_columns = [
            "Username",
            "Full Name",
            "Role",
            "Email",
            "Status",
            "Created At"
        ]

        available_columns = [
            c for c in display_columns
            if c in users_df.columns
        ]

        st.dataframe(
            users_df[available_columns],
            width="stretch",
            hide_index=True
        )

st.divider()

# ==========================================================
# ADMIN INFORMATION
# ==========================================================

st.info(f"""
### Administrator Session

**Logged in as:** {user['fullname']}

**Role:** {user['role']}

**Current Users:** {total_users}

**Page Refresh:** Every 10 seconds
""")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()