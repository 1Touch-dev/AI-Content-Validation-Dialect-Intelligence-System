import os
import logging
import json
from dotenv import load_dotenv

# Import our modules
from scraper.twitter_scraper import scrape_twitter
from scraper.reddit_scraper import scrape_reddit
from scraper.reviews_scraper import scrape_reviews
from processing.cleaner import merge_datasets, clean_data
from processing.language_filter import filter_spanish
from processing.labeling import label_data, export_final_dataset
import time
import schedule
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline(limit=10):
    """
    Full automated pipeline: Scrape -> Merge -> Clean -> Filter -> Label -> Export.
    """
    start_time = datetime.datetime.now()
    logger.info(f"--- Starting AI Dialect Dataset Pipeline Run at {start_time} ---")
    
    try:
        # 1. Scrape
        logger.info("Step 1/6: Scraping data sources...")
        scrape_twitter(["honduras", "tegucigalpa", "mexico", "ecuador"], tweets_desired=limit)
        scrape_reddit(["Honduras", "Mexico", "Ecuador", "LatinAmerica"], limit=limit)
        scrape_reviews(["Tegucigalpa", "San Pedro Sula", "Mexico City", "Quito"], max_reviews=limit)
        
        # 2. Merge
        logger.info("Step 2/6: Merging datasets...")
        combined = merge_datasets()
        
        # 3. Clean
        logger.info("Step 3/6: Cleaning data...")
        cleaned = clean_data(combined)
        
        # 4. Filter Language
        logger.info("Step 4/6: Filtering for Spanish text...")
        spanish_only = filter_spanish(cleaned)
        
        # 5. Label
        logger.info("Step 5/6: Labeling dataset with LLM...")
        labeled = label_data(spanish_only)
        
        # 6. Export
        logger.info("Step 6/6: Exporting final dataset...")
        export_final_dataset(labeled)
        
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        
        # Store metadata
        metadata = {
            "run_time": start_time.isoformat(),
            "completion_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "items_processed": len(labeled) if labeled else 0,
            "status": "success"
        }
        
        with open("storage/last_run_metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)
            
        logger.info(f"--- Pipeline Completed Successfully in {duration} ---")
        
    except Exception as e:
        logger.critical(f"Pipeline failed with error: {e}", exc_info=True)

if __name__ == "__main__":
    # Load env
    load_dotenv()
    
    import sys
    
    if "--schedule" in sys.argv:
        logger.info("Starting pipeline in scheduling mode...")
        # Daily scraping at 02:00
        schedule.every().day.at("02:00").do(run_pipeline, limit=100)
        # Weekly full rebuild on Sunday
        schedule.every().sunday.do(run_pipeline, limit=1000)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # One-off run
        run_pipeline(limit=5)
