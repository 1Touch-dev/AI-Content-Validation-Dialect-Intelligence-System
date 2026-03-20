import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logger = logging.getLogger(__name__)

def label_data(data, model="gpt-4o-mini"):
    """
    Labels the dataset for dialect, intent, tone, and topic using an LLM.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables.")
        return data

    client = OpenAI(api_key=api_key)
    
    labeled_data = []
    
    prompt_template = """
    Classify the following text in Spanish.
    
    Text: "{text}"
    
    Provide the classification in strictly valid JSON format with the following keys:
    - dialect: One of [Honduras, Mexico, Ecuador, Other]
    - intent: One of [opinion, complaint, recommendation, debate, question]
    - tone: One of [casual, sarcastic, formal, argumentative]
    - topic: One of [politics, restaurants, sports, daily_life, news]
    
    JSON:
    """

    logger.info(f"Starting LLM labeling for {len(data)} items...")
    
    for item in tqdm(data, desc="Labeling"):
        text = item.get("text", "")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_template.format(text=text)}],
                response_format={"type": "json_object"}
            )
            
            labels = json.loads(response.choices[0].message.content)
            
            # Merge labels with existing item data
            labeled_item = {
                "platform": item.get("platform"),
                "text": text,
                "dialect": labels.get("dialect"),
                "intent": labels.get("intent"),
                "tone": labels.get("tone"),
                "topic": labels.get("topic"),
                "timestamp": item.get("timestamp"),
                "source_url": item.get("source_url")
            }
            labeled_data.append(labeled_item)
            
        except Exception as e:
            logger.error(f"Error labeling item: {e}")
            # Fallback or skip
            continue

    output_path = os.path.join("storage", "labeled_data", "labeled_dataset.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(labeled_data, f, ensure_ascii=False, indent=4)
        
    logger.info(f"Labeling complete. Saved {len(labeled_data)} labeled items to {output_path}")
    return labeled_data

def export_final_dataset(data):
    """
    Exports the final labeled dataset to JSON, CSV, and Parquet formats.
    """
    if not data:
        logger.warning("No data to export.")
        return

    import pandas as pd
    df = pd.DataFrame(data)
    
    base_path = os.path.join("storage", "labeled_data", "final_dialect_dataset")
    
    # JSON already saved in label_data, but for consistency:
    df.to_json(f"{base_path}.json", orient='records', indent=4, force_ascii=False)
    # CSV
    df.to_csv(f"{base_path}.csv", index=False)
    # Parquet
    df.to_parquet(f"{base_path}.parquet", index=False)
    
    logger.info(f"Final dataset exported to JSON, CSV, and Parquet at {base_path}.*")

if __name__ == "__main__":
    input_path = os.path.join("storage", "cleaned_data", "spanish_only_dataset.json")
    if os.path.exists(input_path):
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # For testing, label only a few
        test_data = data[:5]
        labeled = label_data(test_data)
        export_final_dataset(labeled)
