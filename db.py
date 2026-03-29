import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    # ATTACK LOG TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input TEXT,
        type TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database Ready!")

# RUN
if __name__ == "__main__":
    init_db()