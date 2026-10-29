import sqlite3
import os
from typing import Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "expense_tracker.db")

DEFAULT_CATEGORIES = [
    ("Food & Dining", "#FF5722", 500.0),
    ("Transportation", "#2196F3", 200.0),
    ("Bills & Utilities", "#F44336", 400.0),
    ("Health & Medical", "#4CAF50", 150.0),
    ("Entertainment", "#9C27B0", 150.0),
    ("Shopping", "#E91E63", 250.0),
    ("Other", "#607D8B", 100.0)
]

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[str] = None) -> None:
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Create Categories table with budget column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT DEFAULT '#888888',
            budget REAL DEFAULT 0.0
        );
    """)

    # Schema migration: Add budget column if missing on existing table
    cursor.execute("PRAGMA table_info(categories);")
    columns = [row[1] for row in cursor.fetchall()]
    if "budget" not in columns:
        cursor.execute("ALTER TABLE categories ADD COLUMN budget REAL DEFAULT 0.0;")

    # Create Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT,
            category_id INTEGER,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
    """)

    # Seed default categories if table is empty
    cursor.execute("SELECT COUNT(*) FROM categories;")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            "INSERT INTO categories (name, color, budget) VALUES (?, ?, ?);",
            DEFAULT_CATEGORIES
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully with category budgets schema.")
