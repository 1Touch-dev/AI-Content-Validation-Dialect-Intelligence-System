import os
import json
import logging
import pandas as pd
from scraper.twitter_scraper import scrape_twitter
from scraper.reddit_scraper import scrape_reddit
from scraper.reviews_scraper import scrape_reviews
from processing.cleaner import clean_data, merge_datasets
from processing.language_filter import filter_spanish
from processing.labeling import label_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DIALECTS = {
    "mexico": {
        "twitter_queries": ["#Mexico", "CDMX", "Liga MX", "Club America", "Guadalajara"],
        "subreddits": ["Mexico", "mexico", "CDMX", "spanish"],
        "cities": ["Mexico City", "Guadalajara", "Monterrey", "Cancun"],
        "target_new": 5000,
        "existing_file": "datasets/mexico/mexico_dataset.json"
    },
    "ecuador": {
        "twitter_queries": ["#Ecuador", "Barcelona SC", "Emelec", "LigaPro", "LDU Quito"],
        "subreddits": ["Ecuador", "ecuador", "Quito", "Guayaquil"],
        "cities": ["Quito", "Guayaquil", "Cuenca"],
        "target_new": 5000,
        "existing_file": "datasets/ecuador/ecuador_dataset.json"
    },
    "honduras": {
        "twitter_queries": ["#Honduras", "Tegucigalpa", "San Pedro Sula", "Olimpia FC", "Motagua"],
        "subreddits": ["Honduras", "honduras"],
        "cities": ["Tegucigalpa", "San Pedro Sula", "La Ceiba"],
        "target_new": 3400,
        "existing_file": "datasets/honduras/honduras_dataset.json"
    }
}

MAX_LABEL_PER_BATCH = 10000

def load_existing_texts(dialect):
    filepath = DIALECTS[dialect]["existing_file"]
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {item["text"] for item in data}
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
    return set()

def append_to_dialect_dataset(dialect, new_items):
    filepath = DIALECTS[dialect]["existing_file"]
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    existing_data = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
    
    # Deduplicate new_items against existing_data and itself
    existing_texts = {item["text"] for item in existing_data}
    unique_new = []
    seen_new = set()
    
    for item in new_items:
        txt = item.get("text", "")
        if txt and txt not in existing_texts and txt not in seen_new:
            unique_new.append(item)
            seen_new.add(txt)
            
    combined = existing_data + unique_new
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=4)
        
    return len(unique_new), len(combined)

def expand_dialect(dialect):
    config = DIALECTS[dialect]
    logger.info(f"--- EXPANDING DIALECT: {dialect.upper()} ---")
    
    # 1. Scrape
    logger.info(f"Starting scrapes for {dialect}...")
    
    # We distribute the target across sources. 
    # Note: Apify credits will be consumed.
    tweets = scrape_twitter(config["twitter_queries"], tweets_desired=1500)
    reddit = scrape_reddit(config["subreddits"], limit=1500)
    reviews = scrape_reviews(config["cities"], max_reviews=1500)
    
    # Store temporary raw data for this batch
    batch_raw = []
    if tweets: batch_raw.extend([{"text": t["text"], "platform": "twitter", "timestamp": t.get("createdAt"), "source_url": t.get("url")} for t in tweets])
    if reddit: batch_raw.extend([{"text": r.get("selftext") or r.get("title"), "platform": "reddit", "timestamp": r.get("createdAt"), "source_url": r.get("url")} for r in reddit])
    if reviews: batch_raw.extend([{"text": rev.get("text"), "platform": "google_reviews", "timestamp": rev.get("publishedAtDate"), "source_url": rev.get("reviewUrl")} for rev in reviews])
    
    if not batch_raw:
        logger.warning(f"No new raw data found for {dialect}")
        return 0, 0
        
    # 2. Process
    logger.info(f"Processing {len(batch_raw)} new records...")
    cleaned = clean_data(batch_raw)
    spanish = filter_spanish(cleaned)
    
    if not spanish:
        logger.warning(f"No Spanish content found after filtering for {dialect}")
        return 0, 0
        
    # 3. Label (Only the new unique records)
    existing_texts = load_existing_texts(dialect)
    logger.info(f"Checking for new unique records... Found {len(to_label)}.")
    
    if not to_label:
        logger.info(f"All new records for {dialect} are already in the dataset.")
        return 0, len(existing_texts)
        
    # Sampling for speed and target focus
    if len(to_label) > MAX_LABEL_PER_BATCH:
        logger.info(f"Sampling {MAX_LABEL_PER_BATCH} records from {len(to_label)} to optimize processing time.")
        import random
        random.seed(42) # Reproducible sampling
        to_label = random.sample(to_label, MAX_LABEL_PER_BATCH)

    logger.info(f"Labeling {len(to_label)} records for {dialect}...")
    labeled = label_data(to_label)
    
    # 4. Append and Save
    new_added, final_total = append_to_dialect_dataset(dialect, labeled)
    
    logger.info(f"Expansion for {dialect} complete. Added: {new_added}, New Total: {final_total}")
    return new_added, final_total

def main():
    report = []
    for dialect in DIALECTS.keys():
        new_added, final_total = expand_dialect(dialect)
        report.append({
            "Dialect": dialect.capitalize(),
            "New Samples Added": new_added,
            "Final Dataset Size": final_total
        })
    
    print("\n" + "="*40)
    print("DATA EXPANSION FINAL REPORT")
    print("="*40)
    for entry in report:
        print(f"{entry['Dialect']}:")
        print(f"  New Samples Added: {entry['New Samples Added']}")
        print(f"  Final Dataset Size: {entry['Final Dataset Size']}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
