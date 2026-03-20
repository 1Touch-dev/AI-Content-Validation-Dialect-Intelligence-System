import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient
import logging

# Configure logging
logger = logging.getLogger(__name__)

def scrape_twitter(search_terms, tweets_desired=100, language='es'):
    """
    Scrapes Twitter data using apidojo/twitter-x-scraper.
    """
    load_dotenv()
    api_token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_API_KEY")
    
    if not api_token:
        logger.error("APIFY_API_TOKEN not found in environment variables.")
        return

    client = ApifyClient(api_token)
    
    # Updated to apidojo/tweet-scraper and using correct fields
    run_input = {
        "searchTerms": search_terms,
        "maxItems": tweets_desired,
        "tweetLanguage": language,
        "sort": "Latest"
    }

    try:
        logger.info(f"Starting Twitter scraper with search terms: {search_terms}")
        # Run the actor and wait for it to finish
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)
        
        dataset_id = run["defaultDatasetId"]
        logger.info(f"Scrape finished. Dataset ID: {dataset_id}. Fetching items...")
        
        items = list(client.dataset(dataset_id).iterate_items())
        logger.info(f"Fetched {len(items)} items from Twitter.")

        # Save to raw_data
        output_path = os.path.join("storage", "raw_data", "twitter.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Twitter data saved to {output_path}")
        return items

    except Exception as e:
        logger.error(f"An error occurred during Twitter scraping: {e}")
        return []

if __name__ == "__main__":
    # Test run with small sample
    terms = ["honduras", "#honduras"]
    scrape_twitter(terms, tweets_desired=10)
