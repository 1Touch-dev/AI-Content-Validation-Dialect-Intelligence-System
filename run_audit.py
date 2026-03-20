import os
import json
import pandas as pd
from collections import Counter

def check_file(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def main():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    print("="*50)
    print("AI DIALECT DATASET PIPELINE - FULL STATUS AUDIT")
    print("="*50)

    # 1. DATASETS
    print("\n1. DATASETS")
    honduras_expanded = f"{base_dir}/datasets/honduras/honduras_dataset_expanded.json"
    honduras_data = check_file(honduras_expanded)
    honduras_count = len(honduras_data) if honduras_data else 0
    print(f"- Honduras (expanded): {honduras_count} records (Target: 5000)")

    mexico_file = f"{base_dir}/datasets/mexico/mexico_dataset.json"
    mexico_data = check_file(mexico_file)
    print(f"- Mexico (labeled): {len(mexico_data) if mexico_data else 0} records")

    ecuador_file = f"{base_dir}/datasets/ecuador/ecuador_dataset.json"
    ecuador_data = check_file(ecuador_file)
    print(f"- Ecuador (labeled): {len(ecuador_data) if ecuador_data else 0} records")

    other_file = f"{base_dir}/datasets/other/other_spanish_dataset.json"
    other_data = check_file(other_file)
    other_count = len(other_data) if other_data else 0
    print(f"- Other Spanish: {other_count} records (Target: 1366)")

    # Check Mexico raw/cleaned candidates
    # According to previous outputs, Mexico had ~55k in spanish_only_dataset.json, but let's check exact files
    spanish_only_path = f"{base_dir}/storage/cleaned_data/spanish_only_dataset.json"
    spanish_only = check_file(spanish_only_path)
    if spanish_only:
        print(f"- Mexico (ready for labeling): {len(spanish_only)} records in spanish_only_dataset.json")

    # 2. LABELING STATUS & 4. DATA QUALITY
    print("\n2. LABELING STATUS & 4. DATA QUALITY")
    labeled_file = f"{base_dir}/storage/labeled_data/labeled_dataset.json"
    labeled_data = check_file(labeled_file)
    
    if labeled_data:
        print(f"- Total Labeled Records (Initial batch): {len(labeled_data)}")
        
        # Merge all final datasets for quality check
        all_final = []
        if honduras_data: all_final.extend(honduras_data)
        if mexico_data: all_final.extend(mexico_data)
        if ecuador_data: all_final.extend(ecuador_data)
        if other_data: all_final.extend(other_data)
        
        print(f"\nQuality Check on Final Datasets ({len(all_final)} total records):")
        
        # Check required fields
        required_fields = ['dialect', 'intent', 'tone', 'topic']
        missing_fields_count = 0
        for item in all_final:
            if not all(k in item and item[k] for k in required_fields):
                missing_fields_count += 1
                
        print(f"- Records missing required fields: {missing_fields_count}")
        
        # Check duplicates
        texts = [item.get('text', '').lower().strip() for item in all_final]
        unique_texts = set(texts)
        duplicates = len(texts) - len(unique_texts)
        print(f"- Duplicate texts across all final datasets: {duplicates}")
        
        # Dialect distribution in final data
        dialects = [str(item.get('dialect', 'None')).lower() for item in all_final]
        dist = Counter(dialects)
        print(f"- Dialect Distribution (including synthetic):")
        for k, v in dist.items():
            print(f"  * {k}: {v}")

    # 3. PIPELINE STAGES
    print("\n3. PIPELINE STAGES")
    print("- Scraping: Incomplete (Mexico raw scraped, Ecuador/Honduras blocked)")
    print("- Merging: Complete (Initial batch merged)")
    print("- Cleaning: Complete (Initial batch + large Mexico batch cleaned)")
    print("- Language Filtering: Complete")
    print("- LLM Labeling: Incomplete (55k Mexico records pending)")
    print("- Dialect Splitting: Complete (Initial batch split)")
    print("- Dataset Expansion: Partially Complete (Honduras synthetic generated, Mexico/Ecuador pending labeling/scraping)")

    # 5. EXPORTS
    print("\n5. EXPORTS")
    export_dir = f"{base_dir}/storage/labeled_data"
    exports_exist = {
        'JSON': os.path.exists(f"{export_dir}/final_dialect_dataset.json"),
        'CSV': os.path.exists(f"{export_dir}/final_dialect_dataset.csv"),
        'Parquet': os.path.exists(f"{export_dir}/final_dialect_dataset.parquet")
    }
    for ext, exists in exports_exist.items():
        print(f"- {ext}: {'Yes' if exists else 'No'}")

if __name__ == "__main__":
    main()
