import sqlite3

conn = sqlite3.connect("resumes.db")

cursor = conn.cursor()

# =========================
# USERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")


# Add profile columns to existing users table
profile_columns = [
    ("phone", "TEXT"),
    ("college", "TEXT"),
    ("degree", "TEXT"),
    ("graduation_year", "TEXT"),
    ("skills", "TEXT"),
    ("linkedin", "TEXT"),
    ("github", "TEXT")
]

for column, data_type in profile_columns:

    try:

        cursor.execute(
            f"ALTER TABLE users ADD COLUMN {column} {data_type}"
        )

    except sqlite3.OperationalError:

        # Column already exists
        pass


# =========================
# RESUMES TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS resumes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    github TEXT,
    linkedin TEXT,
    summary TEXT,
    skills TEXT,
    education TEXT,
    projects TEXT,
    experience TEXT,
    certifications TEXT
)
""")


# Add user_id to resumes table
try:

    cursor.execute("""
    ALTER TABLE resumes
    ADD COLUMN user_id INTEGER
    """)

except sqlite3.OperationalError:

    # user_id already exists
    pass


conn.commit()
conn.close()

print("Database Created Successfully!")