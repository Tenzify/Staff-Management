import sqlite3

conn = sqlite3.connect('staff.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(staff)")
table_info = cursor.fetchall()

for column in table_info:
    print(column)

conn.close()
