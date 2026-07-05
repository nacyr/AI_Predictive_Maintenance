from database.users import create_users_table, add_user, connect

# =====================================================
# CREATE TABLES
# =====================================================
create_users_table()

# =====================================================
# CREATE DEFAULT ADMIN (ONLY IF IT DOESN'T EXIST)
# =====================================================
conn = connect()
cursor = conn.cursor()

cursor.execute(
    "SELECT * FROM users WHERE username=?",
    ("admin",)
)

admin = cursor.fetchone()

if admin is None:

    add_user(
        fullname="System Administrator",
        username="admin",
        password="admin123",
        role="Administrator",
        department="ICT",
        plant="Head Office"
    )

    print("Default Administrator created.")

else:

    print("Administrator already exists.")

conn.close()

print("Database initialized successfully.")