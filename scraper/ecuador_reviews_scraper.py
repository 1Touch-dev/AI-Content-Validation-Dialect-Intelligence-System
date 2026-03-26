import os
import json
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

def scrape_ecuador_reviews(max_items=500):
    client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
    
    # Target: Restaurants and landmarks in Quito and Guayaquil
    start_urls = [
        {"url": "https://www.google.com/maps/search/restaurants+in+Quito+Ecuador"},
        {"url": "https://www.google.com/maps/search/restaurants+in+Guayaquil+Ecuador"},
        {"url": "https://www.google.com/maps/search/tourist+attractions+in+Cuenca+Ecuador"}
    ]
    
    run_input = {
        "startUrls": start_urls,
        "maxReviewsPerPlace": 50, # Limit to distribute across multiple places
        "maxReviews": max_items,
        "language": "es",
    }
    
    print(f"Starting Apify Google Maps Reviews Scraper for Ecuador (Target: {max_items})...")
    # Using compass/google-maps-reviews-scraper
    run = client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)
    
    results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    output_path = "storage/raw_data/ecuador_reviews_raw.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"Scraped {len(results)} reviews. Saved to {output_path}")
    return results

if __name__ == "__main__":
    scrape_ecuador_reviews()
