import os
import json
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def split_datasets():
    input_file = os.path.join("storage", "labeled_data", "final_dialect_dataset.json")
    
    if not os.path.exists(input_file):
        logger.error(f"Error: {input_file} not found. Please ensure the pipeline has run successfully.")
        return

    logger.info(f"Loading dataset from {input_file}...")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_records = len(data)
    logger.info(f"Total records loaded: {total_records}")

    # Grouping by dialect
    # Normalizing keys to handle case sensitivity if any
    dialect_groups = defaultdict(list)
    for record in data:
        dialect = record.get("dialect", "other").lower().strip()
        dialect_groups[dialect].append(record)

    # Define output mapping based on user requirements
    # "honduras", "mexico", "ecuador", "other", "neutral_spanish"
    output_meta = {
        "honduras": "datasets/honduras/honduras_dataset.json",
        "mexico": "datasets/mexico/mexico_dataset.json",
        "ecuador": "datasets/ecuador/ecuador_dataset.json",
        "other": "datasets/other/other_spanish_dataset.json",
        "neutral_spanish": "datasets/other/neutral_spanish_dataset.json"
    }

    processed_count = 0
    counts = {
        "Honduras": 0,
        "Mexico": 0,
        "Ecuador": 0,
        "Other Spanish": 0
    }

    # Iterate through groups and save
    for dialect, records in dialect_groups.items():
        # Determine target path
        if dialect in output_meta:
            target_path = output_meta[dialect]
        else:
            # Fallback for any unexpected dialect values
            target_path = f"datasets/other/{dialect}_dataset.json"
        
        # Create directory
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Save records
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        
        count = len(records)
        processed_count += count
        
        # Update user-facing log counts
        if dialect == "honduras":
            counts["Honduras"] += count
        elif dialect == "mexico":
            counts["Mexico"] += count
        elif dialect == "ecuador":
            counts["Ecuador"] += count
        else:
            counts["Other Spanish"] += count

    # Print required log format
    print("\n" + "="*30)
    print(f"Total records processed: {total_records}")
    print(f"Honduras: {counts['Honduras']}")
    print(f"Mexico: {counts['Mexico']}")
    print(f"Ecuador: {counts['Ecuador']}")
    print(f"Other Spanish: {counts['Other Spanish']}")
    print("="*30 + "\n")

    # Validation
    if processed_count == total_records:
        logger.info("Validation successful: All records were correctly written to files.")
    else:
        logger.warning(f"Validation Warning: Only {processed_count}/{total_records} records were processed.")

if __name__ == "__main__":
    split_datasets()
