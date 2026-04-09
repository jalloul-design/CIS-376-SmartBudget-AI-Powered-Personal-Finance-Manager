# Mira
# Handles everything SQLite related. Creates the database and tables on first run, and provides functions for connecting and running queries. Every other file that needs the DB goes through this file.

import sqlite3
from config import database_name, DEFAULT_CATEGORIES

def get_connection():
    connect = sqlite3.connect(database_name)
    connect.row_factory = sqlite3.Row
    return connect

def initialize_database():
    connect = get_connection()
    cursor = connect.cursor()

    # Executing Categories Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
        )
    ''')

    # Executing Transaction Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        amount         REAL             NOT NULL,
        date           TEXT             NOT NULL,
        description    TEXT,
        category_id    INTEGER,
        payment_method TEXT,
        type           TEXT             NOT NULL,
        recurring      INTEGER          DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Executing Budget Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER          NOT NULL,
        amount      REAL             NOT NULL,
        time_period TEXT             NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    # Inserting default categories
    for category in DEFAULT_CATEGORIES:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
    connect.commit()
    connect.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()

