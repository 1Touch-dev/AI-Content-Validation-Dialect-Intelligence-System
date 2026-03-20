import os
import json
import logging
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# For consistent results
DetectorFactory.seed = 0

# Configure logging
logger = logging.getLogger(__name__)

def filter_spanish(data):
    """
    Filters the dataset to keep only Spanish texts.
    """
    if not data:
        return []

    spanish_only = []
    
    logger.info(f"Starting language filtering for {len(data)} items...")
    
    for item in data:
        text = item.get("text", "")
        if not text:
            continue
            
        try:
            lang = detect(text)
            if lang == 'es':
                spanish_only.append(item)
        except LangDetectException:
            # If detection fails, we skip the item
            continue

    output_path = os.path.join("storage", "cleaned_data", "spanish_only_dataset.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spanish_only, f, ensure_ascii=False, indent=4)
        
    logger.info(f"Language filtering complete: {len(spanish_only)} Spanish items remaining out of {len(data)}. Saved to {output_path}")
    return spanish_only

if __name__ == "__main__":
    input_path = os.path.join("storage", "cleaned_data", "cleaned_dataset.json")
    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        filter_spanish(data)
    else:
        logger.warning(f"No cleaned dataset found at {input_path}")
