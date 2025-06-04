import sqlite3
from sqlite3 import Connection
from pathlib import Path

DB_FILENAME = "catalog.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopify_id TEXT,
    sku TEXT UNIQUE,
    title TEXT,
    description TEXT,
    price REAL,
    quantity INTEGER
);
CREATE INDEX IF NOT EXISTS idx_products_shopify_id ON products(shopify_id);
"""


def initialize_db(db_path: str = DB_FILENAME) -> Connection:
    """Initialize the SQLite database and return the connection."""
    path = Path(db_path)
    conn = sqlite3.connect(path)
    with conn:
        conn.executescript(SCHEMA_SQL)
    return conn


if __name__ == "__main__":
    initialize_db()
