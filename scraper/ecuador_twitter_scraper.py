import os
import json
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

def scrape_ecuador_twitter(max_items=1000):
    client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
    
    # Target: Ecuadorian Football and Major Cities/Keywords
    search_queries = [
        "LDU Quito", "Independiente del Valle", "Barcelona SC", "Emelec",
        "Moisés Caicedo", "Piero Hincapié", "Enner Valencia", "Kendry Páez",
        "Quito Ecuador", "Guayaquil Ecuador", "Dialecto Ecuatoriano",
        "Ñaño Ecuador", "Bacán Ecuador"
    ]
    
    # Updated to match apidojo/tweet-scraper schema
    run_input = {
        "searchTerms": search_queries,
        "maxItems": max_items,
        "tweetLanguage": "es",
        "sort": "Latest"
    }
    
    print(f"Starting Apify Twitter Scraper for Ecuador (Target: {max_items})...")
    # Using apidojo/tweet-scraper
    run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)
    
    results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    output_path = "storage/raw_data/ecuador_twitter_raw.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(results)} tweets. Saved to {output_path}")
    return results

if __name__ == "__main__":
    scrape_ecuador_twitter()
