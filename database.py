import sqlite3

conn = sqlite3.connect("resumes.db")

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

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
try:
    cursor.execute("""
    ALTER TABLE resumes
    ADD COLUMN user_id INTEGER
    """)
except:
    pass

conn.commit()
conn.close()

print("Database Created Successfully!")