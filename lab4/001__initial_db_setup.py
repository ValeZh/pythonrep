import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()
cursor.execute('''  
                    CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER
                )''')