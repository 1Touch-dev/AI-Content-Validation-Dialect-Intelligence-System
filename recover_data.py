import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient
import logging

# Configure logging
logger = logging.getLogger(__name__)

def recover_last_run(actor_name):
    load_dotenv()
    api_token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_API_KEY")
    client = ApifyClient(api_token)
    
    # List runs for the actor
    runs = client.actor(actor_name).runs().list()
    if not runs.items:
        logger.error(f"No runs found for {actor_name}")
        return
    
    last_run = runs.items[0]
    dataset_id = last_run["defaultDatasetId"]
    logger.info(f"Recovering dataset {dataset_id} from run {last_run['id']}")
    
    items = list(client.dataset(dataset_id).iterate_items())
    logger.info(f"Fetched {len(items)} items.")
    
    # Save based on actor type
    if "google-maps" in actor_name:
        filename = "reviews.json"
    elif "reddit" in actor_name:
        filename = "reddit.json"
    elif "tweet" in actor_name or "twitter" in actor_name:
        filename = "twitter.json"
    else:
        filename = "recovered.json"
        
    output_path = os.path.join("storage", "raw_data", filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=4)
    logger.info(f"Data saved to {output_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Recover Google Reviews
    recover_last_run("compass/google-maps-reviews-scraper")
