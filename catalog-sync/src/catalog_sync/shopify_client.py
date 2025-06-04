import os
import requests
from dotenv import load_dotenv
from .database import initialize_db, upsert_product

# Load environment variables from .env file
load_dotenv()

SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL") # e.g., "your-store-name.myshopify.com"
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_PASSWORD = os.getenv("SHOPIFY_API_PASSWORD") # This is the App Password or Access Token

class ShopifyAPIClient:
    def __init__(self, store_url=None, api_key=None, api_password=None):
        self.store_url = store_url or SHOPIFY_STORE_URL
        self.api_key = api_key or SHOPIFY_API_KEY
        self.api_password = api_password or SHOPIFY_API_PASSWORD
        
        if not all([self.store_url, self.api_key, self.api_password]):
            raise ValueError("Shopify store URL, API key, and API password must be provided or set in .env")

        self.base_url = f"https://{self.api_key}:{self.api_password}@{self.store_url}/admin/api/2023-10" # Using 2023-10 API version, can be updated

    def _parse_product_data(self, product_raw_data):
        """Helper function to parse raw product data into a structured dict."""
        # Default to None for fields that might be missing
        sku = None
        price = None
        inventory_quantity = None

        if product_raw_data.get('variants') and len(product_raw_data['variants']) > 0:
            first_variant = product_raw_data['variants'][0]
            sku = first_variant.get('sku')
            price = first_variant.get('price')
            inventory_quantity = first_variant.get('inventory_quantity')
        
        main_image_url = None
        if product_raw_data.get('image') and product_raw_data['image'].get('src'):
            main_image_url = product_raw_data['image'].get('src')
        elif product_raw_data.get('images') and len(product_raw_data['images']) > 0:
            main_image_url = product_raw_data['images'][0].get('src')

        return {
            'id': product_raw_data.get('id'),
            'title': product_raw_data.get('title'),
            'sku': sku,
            'price': price,
            'inventory_quantity': inventory_quantity,
            'body_html': product_raw_data.get('body_html'), # Basic description
            'main_image_url': main_image_url,
            # Store the full variant data for now, might be useful for Task 1.1.3
            'variants': product_raw_data.get('variants', []),
            'raw_shopify_data': product_raw_data # Keep raw data for potential future needs/debugging
        }

    def _request(self, method, endpoint, params=None, json_data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response = requests.request(method, url, params=params, json=json_data, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            return response.json()
        except requests.exceptions.HTTPError as errh:
            print(f"Http Error: {errh} - {response.text}")
            # TODO: Add more robust error logging/handling
            return None
        except requests.exceptions.ConnectionError as errc:
            print(f"Error Connecting: {errc}")
            return None
        except requests.exceptions.Timeout as errt:
            print(f"Timeout Error: {errt}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Oops: Something Else: {err}")
            return None

    def get_products(self, limit=50, page_info=None):
        """
        Fetch a list of products. Supports pagination using page_info.
        
        Args:
            limit (int): Number of products to fetch per page.
            page_info (str, optional): Page info token for fetching next/previous page.
        
        Returns:
            dict: JSON response containing products and pagination info, or None on error.
        """
        params = {"limit": limit}
        if page_info:
            params["page_info"] = page_info
            
        # Example: Fetching products (actual endpoint might vary based on what's needed)
        # Shopify uses cursor-based pagination. The response will contain link headers for next/prev.
        # For simplicity, this initial version doesn't fully implement link header parsing.
        # We will need to enhance this for robust pagination.
        
        raw_response = self._request("GET", "products.json", params=params)
        if raw_response and 'products' in raw_response:
            parsed_products = [self._parse_product_data(p) for p in raw_response['products']]
            # Pass along pagination info if present in raw_response (e.g. Link headers for Shopify)
            # For now, returning parsed products and the raw response for pagination handling later
            return {'products': parsed_products, 'raw_response': raw_response}
        return None

    def get_product_details(self, product_id):
        """
        Fetch detailed information for a single product.
        
        Args:
            product_id (int or str): The ID of the Shopify product.
            
        Returns:
            dict: Parsed product details, or None on error.
        """
        raw_product = self._request("GET", f"products/{product_id}.json")
        if raw_product and 'product' in raw_product:
            return self._parse_product_data(raw_product['product'])
        return None

# Example usage (for testing purposes, will be removed or moved to a test file)
if __name__ == "__main__":
    print("Attempting to initialize ShopifyAPIClient...")
    print(f"Store URL: {SHOPIFY_STORE_URL}") # For debugging, ensure .env is loaded
    
    # Before running, ensure you have a .env file in the project root (sAb/.env)
    # with SHOPIFY_STORE_URL, SHOPIFY_API_KEY, and SHOPIFY_API_PASSWORD set.
    # Example .env content:
    # SHOPIFY_STORE_URL="your-dev-store-name.myshopify.com"
    # SHOPIFY_API_KEY="your_api_key"
    # SHOPIFY_API_PASSWORD="your_app_password_or_access_token"

    if not all([SHOPIFY_STORE_URL, SHOPIFY_API_KEY, SHOPIFY_API_PASSWORD]):
        print("One or more Shopify credentials are not set in the environment variables.")
        print("Please create a .env file in the project root (sAb/.env) with:")
        print("SHOPIFY_STORE_URL=your-store.myshopify.com")
        print("SHOPIFY_API_KEY=your_api_key")
        print("SHOPIFY_API_PASSWORD=your_app_password_or_access_token")
    else:
        db_conn = None  # Initialize db_conn to None
        try:
            client = ShopifyAPIClient()
            print("ShopifyAPIClient initialized successfully.")

            # --- Initialize Database ---
            print("\nInitializing database...")
            db_conn = initialize_db() # Default path is catalog.db relative to where script is run
                                      # For consistency, it might be better to define DB_FILENAME in one place (e.g. a config module)
                                      # and ensure it uses an absolute path or path relative to project root.
                                      # Current database.py DB_FILENAME = "catalog.db"
            print("Database initialized.")
            # ---
            
            # Test fetching products and storing them
            print("\nFetching products (limit 2 for example)...")
            products_response_data = client.get_products(limit=2)
            
            if products_response_data and products_response_data.get('products'):
                fetched_products = products_response_data['products']
                print(f"Fetched {len(fetched_products)} products:")
                for product in fetched_products:
                    print(f"  - Processing Product ID: {product['id']}, Title: {product['title']}")
                    if product.get('sku'): # Only attempt to upsert if SKU is present
                        if upsert_product(db_conn, product):
                            print(f"    Successfully upserted product with SKU: {product['sku']}")
                        else:
                            print(f"    Product with SKU: {product['sku']} (ID: {product['id']}) likely unchanged or error in upsert.")
                    else:
                        print(f"    Skipping product ID: {product['id']} as it has no SKU (first variant).")
            else:
                print("Failed to fetch products or no products found.")

            # Example: Test fetching a specific product and storing it
            # test_product_id = 'gid://shopify/Product/YOUR_TEST_PRODUCT_ID' # Replace with a real Product ID from your test store (use the GID format or integer)
            # if test_product_id != 'gid://shopify/Product/YOUR_TEST_PRODUCT_ID':
            #     print(f"\nFetching product details for ID: {test_product_id}...")
            #     product_details = client.get_product_details(test_product_id)
            #     if product_details:
            #         print(f"  Product Title: {product_details['title']}")
            #         print(f"    SKU: {product_details['sku']}")
            #         print(f"    Price: {product_details['price']}")
            #         if product_details.get('sku'):
            #             if upsert_product(db_conn, product_details):
            #                 print(f"    Successfully upserted product with SKU: {product_details['sku']}")
            #             else:
            #                 print(f"    Product with SKU: {product_details['sku']} likely unchanged or error in upsert.")
            #         else:
            #             print(f"    Skipping product ID: {product_details['id']} as it has no SKU (first variant).")
            #     else:
            #         print(f"  Failed to fetch product details for ID: {test_product_id}")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            if db_conn:
                db_conn.close()
                print("\nDatabase connection closed.") 