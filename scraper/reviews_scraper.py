import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient
import logging

# Configure logging
logger = logging.getLogger(__name__)

def scrape_reviews(locations, max_reviews=100):
    """
    Scrapes Google Maps reviews using compass/google-maps-reviews-scraper.
    """
    load_dotenv()
    api_token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_API_KEY")
    
    if not api_token:
        logger.error("APIFY_API_TOKEN not found in environment variables.")
        return

    client = ApifyClient(api_token)
    
    # Properly encode search queries into URLs
    import urllib.parse
    start_urls = []
    for loc in locations:
        query = f"restaurants in {loc}"
        encoded_query = urllib.parse.quote(query)
        start_urls.append({"url": f"https://www.google.com/maps/search/{encoded_query}"})
    
    run_input = {
        "startUrls": start_urls,
        "maxReviews": max_reviews,
    }

    try:
        logger.info(f"Starting Google Reviews scraper for locations: {locations}")
        # Run the actor and wait for it to finish
        run = client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)
        
        dataset_id = run["defaultDatasetId"]
        logger.info(f"Scrape finished. Dataset ID: {dataset_id}. Fetching items...")
        
        items = list(client.dataset(dataset_id).iterate_items())
        logger.info(f"Fetched {len(items)} items from Google Reviews.")

        # Save to raw_data
        output_path = os.path.join("storage", "raw_data", "reviews.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Reviews data saved to {output_path}")
        return items

    except Exception as e:
        logger.error(f"An error occurred during Reviews scraping: {e}")
        return []

if __name__ == "__main__":
    # Test run with small sample
    locs = ["Tegucigalpa"]
    scrape_reviews(locs, max_reviews=10)
