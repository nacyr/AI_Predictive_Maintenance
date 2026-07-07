import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ==========================================================
# PROJECT ROOT
# ==========================================================

project_root = Path(__file__).resolve().parent.parent

if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# ==========================================================
# AUTO REFRESH
# ==========================================================

st_autorefresh(
    interval=10000,
    key="user_management_refresh"
)

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
# SESSION VALIDATION
# ==========================================================

session_user = st.session_state.get("user")

if session_user is None:

    st.warning("Please login first.")

    st.switch_page("app.py")

    st.stop()

if not isinstance(session_user, dict):

    st.error("Invalid login session.")

    st.session_state.clear()

    st.switch_page("app.py")

    st.stop()

user = {

    "username": session_user.get(
        "username",
        ""
    ),

    "fullname": session_user.get(
        "fullname",
        "Unknown User"
    ),

    "role": session_user.get(
        "role",
        ""
    ),

    "email": session_user.get(
        "email",
        ""
    )

}

if user.get("role") != "Administrator":

    st.error(
        "Administrator access required."
    )

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

st.divider()

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

    st.error(

        f"Unable to load users: {e}"

    )

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
# USER STATISTICS
# ==========================================================

st.subheader(
    "📊 User Statistics"
)

total_users = len(users_df)

active_users = (

    users_df["Status"].eq("Active").sum()

    if not users_df.empty

    else 0

)

disabled_users = (

    users_df["Status"].eq("Disabled").sum()

    if not users_df.empty

    else 0

)

role_counts = (

    users_df["Role"].value_counts()

    if not users_df.empty

    else pd.Series(dtype=int)

)

administrators = role_counts.get(
    "Administrator",
    0
)

maintenance = role_counts.get(
    "Maintenance Engineer",
    0
)

operations = role_counts.get(
    "Operations Engineer",
    0
)

supervisors = role_counts.get(
    "Supervisor",
    0
)

guests = role_counts.get(
    "Guest",
    0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Users",
    total_users
)

c2.metric(
    "Active Users",
    active_users
)

c3.metric(
    "Disabled Users",
    disabled_users
)

c4.metric(
    "Administrators",
    administrators
)

c5, c6, c7 = st.columns(3)

c5.metric(
    "Maintenance",
    maintenance
)

c6.metric(
    "Operations",
    operations
)

c7.metric(
    "Supervisors",
    supervisors
)

st.caption(
    f"Guests: {guests}"
)

st.divider()

# ==========================================================
# CREATE USER
# ==========================================================

st.subheader(
    "➕ Create New User"
)

with st.form(
    "create_user_form"
):

    left, right = st.columns(2)

    with left:

        username = st.text_input(
            "Username"
        )

        fullname = st.text_input(
            "Full Name"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

    with right:

        email = st.text_input(
            "Email"
        )

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
        use_container_width=True
    )

if create:

    if not username.strip():

        st.warning(
            "Username is required."
        )

    elif not fullname.strip():

        st.warning(
            "Full name is required."
        )

    elif not password:

        st.warning(
            "Password is required."
        )

    else:

        success = add_user(

            username.strip(),

            password,

            fullname.strip(),

            role,

            email.strip()

        )

        if success:

            st.success(
                "User created successfully."
            )

            st.rerun()

        else:

            st.error(
                "Username already exists."
            )

st.divider()

# ==========================================================
# SEARCH & FILTER
# ==========================================================

st.subheader(
    "🔍 Search & Filter Users"
)

left, right = st.columns(2)

with left:

    search = st.text_input(
        "Search Username or Full Name"
    )

with right:

    roles = ["ALL"]

    if not users_df.empty:

        roles.extend(

            sorted(

                users_df["Role"]

                .dropna()

                .unique()

                .tolist()

            )

        )

    role_filter = st.selectbox(

        "Filter by Role",

        roles

    )

filtered = users_df.copy()

if not filtered.empty:

    if search.strip():

        keyword = search.lower()

        filtered = filtered[

            filtered["Username"]

            .str.lower()

            .str.contains(

                keyword,

                na=False

            )

            |

            filtered["Full Name"]

            .str.lower()

            .str.contains(

                keyword,

                na=False

            )

        ]

    if role_filter != "ALL":

        filtered = filtered[
            filtered["Role"] == role_filter
        ]

# ==========================================================
# CONTINUE WITH PART 2
# ==========================================================
# ==========================================================
# REGISTERED USERS
# ==========================================================

st.subheader("📋 Registered Users")

if filtered.empty:

    st.info("No users found.")

else:

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ==========================================================
# UPDATE USER
# ==========================================================

st.subheader("✏️ Update User")

if users_df.empty:

    st.info("No users available.")

else:

    selected_user = st.selectbox(
        "Select User",
        users_df["Username"].tolist(),
        key="update_user"
    )

    selected_row = users_df[
        users_df["Username"] == selected_user
    ].iloc[0]

    with st.form("update_user_form"):

        left, right = st.columns(2)

        with left:

            new_fullname = st.text_input(
                "Full Name",
                value=selected_row["Full Name"]
            )

            new_email = st.text_input(
                "Email",
                value=selected_row["Email"]
            )

        with right:

            new_role = st.selectbox(
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
                ].index(selected_row["Role"])
                if selected_row["Role"] in [
                    "Administrator",
                    "Maintenance Engineer",
                    "Operations Engineer",
                    "Supervisor",
                    "Guest"
                ]
                else 0
            )

        update_btn = st.form_submit_button(
            "💾 Update User",
            use_container_width=True
        )

    if update_btn:

        success = update_user(
            selected_user,
            new_fullname.strip(),
            new_email.strip(),
            new_role
        )

        if success:

            st.success("User updated successfully.")

            st.rerun()

        else:

            st.error("Unable to update user.")

st.divider()

# ==========================================================
# ENABLE / DISABLE USER
# ==========================================================

st.subheader("🔒 Enable / Disable User")

if not users_df.empty:

    username = st.selectbox(
        "Select User",
        users_df["Username"].tolist(),
        key="status_user"
    )

    status = st.selectbox(
        "Status",
        [
            "Active",
            "Disabled"
        ]
    )

    if st.button(
        "Update Status",
        use_container_width=True
    ):

        success = update_status(
            username,
            status
        )

        if success:

            st.success(
                "User status updated."
            )

            st.rerun()

        else:

            st.error(
                "Unable to update status."
            )

st.divider()

# ==========================================================
# RESET PASSWORD
# ==========================================================

st.subheader("🔑 Reset Password")

if not users_df.empty:

    username = st.selectbox(
        "User",
        users_df["Username"].tolist(),
        key="password_user"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    if st.button(
        "Reset Password",
        use_container_width=True
    ):

        if not new_password:

            st.warning(
                "Please enter a password."
            )

        else:

            success = reset_password(
                username,
                new_password
            )

            if success:

                st.success(
                    "Password reset successfully."
                )

            else:

                st.error(
                    "Password reset failed."
                )

st.divider()

# ==========================================================
# DELETE USER
# ==========================================================

st.subheader("🗑 Delete User")

if not users_df.empty:

    username = st.selectbox(
        "Select User to Delete",
        users_df["Username"].tolist(),
        key="delete_user"
    )

    if username == user.get("username"):

        st.warning(
            "You cannot delete your own account."
        )

    elif st.button(
        "Delete User",
        type="primary",
        use_container_width=True
    ):

        success = delete_user(
            username
        )

        if success:

            st.success(
                "User deleted successfully."
            )

            st.rerun()

        else:

            st.error(
                "Unable to delete user."
            )

st.divider()

# ==========================================================
# LIVE SYSTEM STATUS
# ==========================================================

st.subheader("🖥 Live System Status")

st.info(f"""
**Total Users:** {total_users}

**Active Users:** {active_users}

**Disabled Users:** {disabled_users}

**Automatic Refresh:** Every 10 Seconds
""")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

show_footer()