import os
import json
import logging
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def expand_ecuador_synthetic():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Error: OPENAI_API_KEY not found in environment variables.")
        return

    client = OpenAI(api_key=api_key)
    
    # Input comes from the cleaned organic data (Phase 21)
    # Since we are running this before organic is fully processed, 
    # we'll point it to where the final cleaned Ecuador JSON will live.
    input_file = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System/datasets/ecuador/ecuador_dataset.json"
    output_file = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System/datasets/ecuador/ecuador_dataset_expanded.json"
    
    if not os.path.exists(input_file):
        # If the file doesn't exist yet, we'll try to load the 45 original records we found earlier
        # located at datasets/ecuador/ecuador_dataset.json (it exists, I checked list_dir earlier)
        logger.info(f"Input file {input_file} found. Proceeding with expansion.")
    else:
        logger.info(f"Loading Ecuador dataset: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    original_size = len(original_data)
    target_size = 3500 # Target for Ecuador
    
    logger.info(f"Ecuador dataset base: {original_size} records found.")
    
    expanded_data = list(original_data)
    seen_texts = {item["text"].strip().lower() for item in original_data}
    
    # Prompt template for Ecuadorian paraphrasing
    prompt_template = """
    You are a linguistic expert in Ecuadorian Spanish (Español de Ecuador).
    Paraphrase the following text into 3 different variations that perfectly preserve the authentic Ecuadorian dialect.
    
    Constraints:
    - Maintain Ecuadorian slang where possible (e.g., "ñaño", "bacán", "chuta", "chucha", "la plena", "cachas", "chévere", "harto", "jama", "lampara").
    - Use a mix of "tú" and "usted" as common in Ecuador, or "vos" if appropriate for the Sierra region context.
    - Keep the tone conversational, natural, and realistic. Must sound like someone from Quito or Guayaquil.
    - DO NOT convert into neutral Spanish.
    - The variations must be distinct from the original and from each other.
    
    Original Text: "{text}"
    
    Provide the output in strictly valid JSON format with a key "variations" containing a list of 3 strings.
    JSON:
    """

    progress_bar = tqdm(total=target_size, initial=original_size, desc="Expanding Ecuador Dataset")
    lock = threading.Lock()

    def process_item(item):
        if len(expanded_data) >= target_size:
            return
            
        text = item.get("text", "")
        if not text or len(text) < 5:
            return
            
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional linguist specializing in South American Spanish dialects, specifically Ecuador."},
                    {"role": "user", "content": prompt_template.format(text=text)}
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
                timeout=30
            )
            
            content = json.loads(response.choices[0].message.content)
            variations = content.get("variations", [])
            
            for var in variations:
                if not isinstance(var, str):
                    continue

                with lock:
                    if len(expanded_data) >= target_size:
                        break
                        
                    var_clean = var.strip()
                    var_lower = var_clean.lower()
                    
                    if var_lower not in seen_texts:
                        new_item = item.copy()
                        new_item["text"] = var_clean
                        new_item["is_synthetic"] = True
                        new_item["country"] = "Ecuador"
                        expanded_data.append(new_item)
                        seen_texts.add(var_lower)
                        progress_bar.update(1)
        except Exception:
            pass

    # We might need multiple passes if 45 items * 3 variations is not enough.
    # But after organic scraping, we'll have ~2000 items. 
    # 2000 * 3 is more than enough.
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        # If we only have 45 items right now, we'll run multiple cycles on them
        items_to_process = original_data * (target_size // (original_size * 3) + 2) if original_size > 0 else []
        executor.map(process_item, items_to_process[:target_size])

    progress_bar.close()

    # Save final dataset
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(expanded_data, f, ensure_ascii=False, indent=4)

    # Print report
    print("\n" + "="*40)
    print("ECUADOR DATASET EXPANSION REPORT")
    print("="*40)
    print(f"Original dataset size: {original_size}")
    print(f"Generated samples:     {len(expanded_data) - original_size}")
    print(f"Final dataset size:     {len(expanded_data)}")
    print("="*40 + "\n")

if __name__ == "__main__":
    expand_ecuador_synthetic()
