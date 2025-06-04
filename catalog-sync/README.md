# Shopify-Amazon Bridge

This project aims to sync product data between Shopify and Amazon.

## Database Setup

Run `python catalog_sync/database.py` to create a local SQLite database
`catalog.db` containing a `products` table indexed by Shopify ID and SKU.
