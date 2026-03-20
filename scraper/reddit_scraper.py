import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient
import logging

# Configure logging
logger = logging.getLogger(__name__)

def scrape_reddit(subreddits, limit=100):
    """
    Scrapes Reddit data using alex_claw/reddit-scraper.
    """
    load_dotenv()
    api_token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_API_KEY")
    
    if not api_token:
        logger.error("APIFY_API_TOKEN not found in environment variables.")
        return

    client = ApifyClient(api_token)
    
    # Using alex_claw/reddit-scraper with maxItems and maxPostCount
    run_input = {
        "subreddits": subreddits,
        "maxItems": limit,
        "maxPostCount": limit
    }

    try:
        logger.info(f"Starting Reddit scraper (alex_claw) for subreddits: {subreddits}")
        # Run the actor and wait for it to finish
        run = client.actor("alex_claw/reddit-scraper").call(run_input=run_input)
        
        run_status = run["status"]
        if run_status != "SUCCEEDED":
            logger.error(f"Scrape failed with status: {run_status}")
            return []
            
        dataset_id = run["defaultDatasetId"]
        logger.info(f"Scrape finished. Dataset ID: {dataset_id}. Fetching items...")
        
        items = list(client.dataset(dataset_id).iterate_items())
        logger.info(f"Fetched {len(items)} items from Reddit.")

        # Save to raw_data
        output_path = os.path.join("storage", "raw_data", "reddit.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Reddit data saved to {output_path}")
        return items

    except Exception as e:
        logger.error(f"An error occurred during Reddit scraping: {e}")
        return []

if __name__ == "__main__":
    # Expanded list to reach volume
    subs = ["Honduras", "Mexico", "Ecuador", "LatinAmerica", "Colombia", "Peru", "Argentina", "Chile", 
            "Venezuela", "Guatemala", "CostaRica", "Panama", "Salvador", "Nicaragua", "DominicanRepublic", 
            "Espanol", "AskLatinAmerica", "Spanish"]
    scrape_reddit(subs, limit=2000)
