import sqlite3
from sqlite3 import Connection
from pathlib import Path
import json # Added for storing raw_shopify_data

DB_FILENAME = "catalog.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shopify_product_id TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    title TEXT,
    description TEXT, -- Will store body_html from Shopify
    price REAL,
    quantity INTEGER,
    main_image_url TEXT,
    raw_shopify_data TEXT -- Storing the full JSON from Shopify for this product
);
CREATE INDEX IF NOT EXISTS idx_products_shopify_product_id ON products(shopify_product_id);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku); -- SKU is already UNIQUE, but index can help lookups if not PK
"""


def initialize_db(db_path: str = DB_FILENAME) -> Connection:
    """Initialize the SQLite database and return the connection."""
    path = Path(db_path)
    # Ensure the parent directory exists if db_path includes directories
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row # Access columns by name
    with conn:
        conn.executescript(SCHEMA_SQL)
    return conn

def upsert_product(conn: Connection, product_data: dict):
    """
    Insert or update a product in the database based on SKU.
    product_data is expected to be a dict similar to what _parse_product_data from shopify_client returns.
    """
    sql = """
    INSERT INTO products (shopify_product_id, sku, title, description, price, quantity, main_image_url, raw_shopify_data)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(sku) DO UPDATE SET
        shopify_product_id = excluded.shopify_product_id,
        title = excluded.title,
        description = excluded.description,
        price = excluded.price,
        quantity = excluded.quantity,
        main_image_url = excluded.main_image_url,
        raw_shopify_data = excluded.raw_shopify_data;
    """
    
    # Ensure raw_shopify_data is stored as a JSON string
    raw_data_json = json.dumps(product_data.get('raw_shopify_data'))

    params = (
        product_data.get('id'), # This is shopify_product_id from the parser
        product_data.get('sku'),
        product_data.get('title'),
        product_data.get('body_html'), # Mapped to description
        product_data.get('price'),
        product_data.get('inventory_quantity'), # Mapped to quantity
        product_data.get('main_image_url'),
        raw_data_json
    )
    
    with conn:
        conn.execute(sql, params)
    return conn.total_changes > 0 # Return True if a change was made (insert or update)

# Example of how to fetch a product (can be expanded later)
# def get_product_by_sku(conn: Connection, sku: str) -> sqlite3.Row | None:
#     cursor = conn.execute("SELECT * FROM products WHERE sku = ?", (sku,))
#     return cursor.fetchone()

if __name__ == "__main__":
    print(f"Initializing database: {DB_FILENAME}")
    conn = initialize_db()
    print("Database initialized.")

    # Example upsert (for testing database.py directly)
    # Make sure shopify_client.py has run and you have some sample parsed_product structure
    # sample_parsed_product_from_shopify_client = {
    #     'id': 'gid://shopify/Product/1234567890', # Shopify Product ID
    #     'title': 'Test Product - Updated Title',
    #     'sku': 'TESTSKU001',
    #     'price': 19.99,
    #     'inventory_quantity': 150,
    #     'body_html': '<p>This is an updated test product description.</p>',
    #     'main_image_url': 'https://example.com/updated_image.jpg',
    #     'variants': [], # Simplified for this example
    #     'raw_shopify_data': {'id': 1234567890, 'title': 'Test Product - Updated Title', 'body_html': '...'} # Full original JSON
    # } 
    # 
    # if upsert_product(conn, sample_parsed_product_from_shopify_client):
    #     print(f"Upserted product with SKU: {sample_parsed_product_from_shopify_client['sku']}")
    # else:
    #     print(f"No changes for product SKU: {sample_parsed_product_from_shopify_client['sku']}" (data might be identical or error occurred)")
    # 
    # # Example fetch
    # # fetched_product = get_product_by_sku(conn, 'TESTSKU001')
    # # if fetched_product:
    # # print(f"Fetched product: {dict(fetched_product)}")
    # # else:
    # #     print("Product not found.")

    conn.close()
    print("Database connection closed.")
