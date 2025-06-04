import sqlite3
import sys
from pathlib import Path

# Ensure catalog-sync package is on path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from catalog_sync import database

def test_initialize_db(tmp_path):
    db_path = tmp_path / 'test.db'
    conn = database.initialize_db(str(db_path))
    conn.close()

    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    assert 'id' in columns and 'sku' in columns

    cursor.execute("PRAGMA index_list(products)")
    indexes = [row[1] for row in cursor.fetchall()]
    assert 'idx_products_shopify_id' in indexes
    conn.close()
