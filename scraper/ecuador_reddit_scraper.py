import os
import json
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

def scrape_ecuador_reddit(max_items=500):
    client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
    
    # Target: r/ecuador and r/guayaquil
    run_input = {
        "startUrls": [
            { "url": "https://www.reddit.com/r/ecuador/new" },
            { "url": "https://www.reddit.com/r/guayaquil/new" }
        ],
        "maxItems": max_items,
        "skipComments": False
    }
    
    print(f"Starting Apify Reddit Scraper for Ecuador (Target: {max_items})...")
    # Using trudax/reddit-scraper-lite
    run = client.actor("trudax/reddit-scraper-lite").call(run_input=run_input)
    
    results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    output_path = "storage/raw_data/ecuador_reddit_raw.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(results)} reddit items. Saved to {output_path}")
    return results

if __name__ == "__main__":
    scrape_ecuador_reddit()
