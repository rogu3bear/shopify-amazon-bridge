# Project Plan: Shopify-Amazon Bridge

## Objective
Sync Shopify product catalog to Amazon Seller Central.

## Current Status
- Repository scaffolded (`README.md`, `requirements.txt`, `.gitignore`).
- Agent governance rules defined in `AGENT.md`.
- Initial SQLite database structure and setup scripts (e.g., `catalog_sync/database.py`) merged from PR #1.

## Guiding Principles
- **Iterative Development:** Build and release features in phases.
- **Modularity:** Design components for clarity and testability.
- **Configuration-driven:** Allow for easy adaptation to different stores or settings where possible.
- **Robust Error Handling:** Implement mechanisms to detect, log, and manage synchronization issues.

## Phases & Key Tasks

### Phase 1: Core Integration & Basic Sync (Minimum Viable Product - MVP)
Focus: Establish basic connectivity and one-way sync for a limited set of product data.

*   **Task 1.1: Shopify API Integration - Read**
    *   1.1.1: Develop Shopify API client module:
        *   Secure authentication (API key, password).
        *   Function to fetch a list of products.
        *   Function to fetch detailed information for a single product.
    *   1.1.2: Implement logic to extract essential product data:
        *   Product ID, Title, SKU, Price, Inventory Count, Basic Description, Main Image URL.
    *   1.1.3: Store fetched Shopify data (or a representation) in `catalog_sync_db.sqlite`.

*   **Task 1.2: Amazon SP-API Integration - Write**
    *   1.2.1: Develop Amazon SP-API client module:
        *   Secure authentication (LWA, IAM roles).
        *   Function to submit/update product listings (e.g., using Feeds API or Product Listing API).
    *   1.2.2: Research and define the data requirements for a single, simple Amazon category (e.g., "Home & Kitchen" basic attributes).
    *   1.2.3: Implement logic to transform Shopify data from Task 1.1.2 into the required Amazon format for the chosen category.
    *   1.2.4: Store Amazon listing identifiers (ASIN, SKU, submission status) in `amazon_listings_db.sqlite`.

*   **Task 1.3: Database Refinement**
    *   1.3.1: Finalize schema for `catalog_sync_db.sqlite` to hold Shopify product attributes, variants (basic), and last sync timestamps.
    *   1.3.2: Finalize schema for `amazon_listings_db.sqlite` to hold Amazon listing identifiers, last sync timestamps, and basic status.
    *   1.3.3: Update `db_init.py` accordingly.

*   **Task 1.4: Basic Synchronization Engine (One-Way: Shopify -> Amazon)**
    *   1.4.1: Develop core script (`sync_engine.py` or similar).
    *   1.4.2: Implement product matching logic (Shopify SKU to Amazon SKU).
    *   1.4.3: For new products (SKU in Shopify, not in Amazon DB):
        *   Create new listing on Amazon using data from Task 1.2.3.
    *   1.4.4: For existing products (SKU in both):
        *   Implement basic inventory level sync (Shopify inventory -> Amazon inventory).
        *   Implement basic price sync (Shopify price -> Amazon price).
    *   1.4.5: Basic logging of sync operations and errors.

*   **Task 1.5: Configuration Management**
    *   1.5.1: Utilize `.env` file for API credentials, store URLs, and default settings.
    *   1.5.2: Load configuration in the main script(s).

*   **Task 1.6: Initial Testing**
    *   1.6.1: Unit tests for API client connection methods and data extraction/transformation logic.
    *   1.6.2: Manual end-to-end test: sync 1-2 products from a test Shopify store to a test Amazon Seller Central account.

### Phase 2: Advanced Sync Features & Robustness
Focus: Expand data support, improve matching, handle updates, and enhance error management.

*   **Task 2.1: Enhanced Shopify Data Handling**
    *   2.1.1: Support for Shopify product variants (SKUs, prices, inventory per variant).
    *   2.1.2: Extract and map Shopify collections/product types for potential use in Amazon categorization.
    *   2.1.3: Handle multiple product images.

*   **Task 2.2: Enhanced Amazon SP-API Capabilities**
    *   2.2.1: Support for creating/updating listings in multiple Amazon categories (requires handling different templates/attributes). This may involve Codex researching specific flat-file structures or API requirements per category.
    *   2.2.2: Implement logic for more robust product matching (e.g., UPC/EAN if available, in addition to SKU).
    *   2.2.3: Handle Amazon listing submission feedback and errors (e.g., processing reports from Feeds API).

*   **Task 2.3: Comprehensive Synchronization Logic**
    *   2.3.1: Implement update logic for existing products:
        *   Changes to title, description, images, other attributes.
    *   2.3.2: Implement product deletion/archival sync (e.g., if a product is removed from Shopify, delist or zero out inventory on Amazon).
    *   2.3.3: More sophisticated error handling, logging (to database/file), and retry mechanisms for API calls.
    *   2.3.4: Consider a sync status dashboard or report.

*   **Task 2.4: Mapping & Transformation Improvements**
    *   2.4.1: Develop a more flexible attribute mapping system (e.g., configurable rules if Shopify field names differ significantly from Amazon's needs).

### Phase 3: Automation, Optimization & Operationalization
Focus: Make the sync process automated, efficient, and ready for ongoing use.

*   **Task 3.1: Automation & Scheduling**
    *   3.1.1: Implement Shopify webhook listeners for real-time updates (product create/update/delete, inventory changes).
    *   3.1.2: Set up a scheduler (e.g., cron job, scheduled task) for regular full syncs as a fallback or primary method.

*   **Task 3.2: Performance & Scalability**
    *   3.2.1: Optimize API call usage (batching requests where possible, respecting rate limits).
    *   3.2.2: Optimize database queries and interactions.
    *   3.2.3: Test with a larger catalog.

*   **Task 3.3: Comprehensive Testing & Validation**
    *   3.3.1: Expand unit and integration test coverage significantly.
    *   3.3.2: Set up and utilize sandbox/developer accounts for Shopify and Amazon for automated testing.
    *   3.3.3: Conduct User Acceptance Testing (UAT) with real (or realistic staging) data.

*   **Task 3.4: Deployment & Monitoring**
    *   3.4.1: Package the application (e.g., using `setup.py`, Docker container).
    *   3.4.2: Implement basic monitoring for the sync process (e.g., notifications on critical failures).

*   **Task 3.5: Documentation**
    *   3.5.1: User Guide: Setup, configuration, and operational procedures.
    *   3.5.2: Developer Guide: Code structure, API usage, extension points.

## Tools & Technologies
- **Programming Language:** Python 3.x
- **Databases:** SQLite
- **Key Libraries:** `requests`, `python-dotenv`, `ShopifyAPI` (or direct `requests` for Shopify), appropriate Amazon SP-API SDK or `requests`.
- **Version Control:** Git, GitHub
- **Environment Management:** `venv` or `conda`.

## Agent Responsibilities
- **Cursor (this agent):** Overall project management based on this plan, task definition and breakdown, code scaffolding, Git operations, documentation creation and updates, integration of components, and directing Codex.
- **Codex:** Detailed research (e.g., specific API endpoints, data formats for Amazon categories, Shopify webhook best practices), generation of targeted code modules (e.g., API client functions, data transformation logic, SQL queries for database interactions) based on precise prompts from Cursor.

## Next Steps (Immediate)
- **Confirm understanding of Phase 1, Task 1.1 (Shopify API Integration - Read).**
- **Begin development of Shopify API client (Task 1.1.1).**

*(This plan is a living document and may be updated as the project progresses and new information becomes available.)* 