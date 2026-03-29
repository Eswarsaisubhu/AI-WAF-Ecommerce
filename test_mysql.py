import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@Subhu4224",   # ✅ your password
    database="waf_db"
)

print("✅ Connected Successfully!")

conn.close()