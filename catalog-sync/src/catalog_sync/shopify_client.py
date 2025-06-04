import os
import requests
from dotenv import load_dotenv

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
        
        return self._request("GET", "products.json", params=params)

    def get_product_details(self, product_id):
        """
        Fetch detailed information for a single product.
        
        Args:
            product_id (int or str): The ID of the Shopify product.
            
        Returns:
            dict: JSON response containing the product details, or None on error.
        """
        return self._request("GET", f"products/{product_id}.json")

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
        try:
            client = ShopifyAPIClient()
            print("ShopifyAPIClient initialized successfully.")
            
            # Test fetching products
            # print("\nFetching products...")
            # products_response = client.get_products(limit=5)
            # if products_response and 'products' in products_response:
            #     print(f"Fetched {len(products_response['products'])} products:")
            #     for product in products_response['products']:
            #         print(f"  - ID: {product['id']}, Title: {product['title']}")
            # else:
            #     print("Failed to fetch products or no products found.")

            # Test fetching a specific product (replace with a valid product ID from your test store)
            # test_product_id = 1234567890 # Replace with a real Product ID
            # print(f"\nFetching product details for ID: {test_product_id}...")
            # product_details = client.get_product_details(test_product_id)
            # if product_details and 'product' in product_details:
            #     print(f"Product Title: {product_details['product']['title']}")
            # else:
            #     print(f"Failed to fetch product details for ID: {test_product_id}")

        except ValueError as e:
            print(f"Error initializing client: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}") 