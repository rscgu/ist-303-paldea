import sqlite3

connection = sqlite3.connect('database.db')

with connection:
    connection.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        );
    ''')

print("Database initialized.")
