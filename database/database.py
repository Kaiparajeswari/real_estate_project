import sqlite3

# connect database
conn = sqlite3.connect("database/users.db")

c = conn.cursor()

# create users table
c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT,
password TEXT
)
""")

# create history table
c.execute("""
CREATE TABLE IF NOT EXISTS history(
username TEXT,
city TEXT,
area REAL,
price REAL
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully")