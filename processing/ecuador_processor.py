"""
Process raw Ecuador data: clean, deduplicate, and filter by language.
"""
import os
import re
import json
import logging
import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# For consistent language detection results
DetectorFactory.seed = 0

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def process_ecuador_data():
    """
    Load raw JSON from storage, clean it, filter for Spanish, and save to datasets.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_path = os.path.join(base_dir, "storage/raw_data/ecuador_merged_raw.json")
    output_path = os.path.join(base_dir, "datasets/ecuador/ecuador_dataset.json")

    if not os.path.exists(input_path):
        logger.error("Input file %s not found.", input_path)
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info("Loaded %d raw records for Ecuador.", len(data))
    df = pd.DataFrame(data)

    # 1. Basic Cleaning
    df = df[df['text'].str.strip() != ""]
    df = df.drop_duplicates(subset=['text'])
    # Reduced word count for Twitter compatibility (at least 3 words)
    df = df[df['text'].apply(lambda x: len(str(x).split()) >= 3)]

    # Normalize whitespace
    df['text'] = df['text'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip())

    logger.info("After basic cleaning: %d records.", len(df))

    # 2. Language Filtering (Spanish only)
    logger.info("Starting language filtering...")
    def is_spanish(text):
        try:
            return detect(text) == 'es'
        except LangDetectException:
            return False

    # Apply language filter
    df['is_es'] = df['text'].apply(is_spanish)
    df = df[df['is_es'] == True]
    df = df.drop(columns=['is_es'])

    logger.info("After language filtering: %d Spanish records.", len(df))

    # 3. Final Format
    final_data = df.to_dict(orient='records')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    logger.info("Ecuador dataset ready with %d high-quality records. Saved to %s",
                len(final_data), output_path)

if __name__ == "__main__":
    process_ecuador_data()
