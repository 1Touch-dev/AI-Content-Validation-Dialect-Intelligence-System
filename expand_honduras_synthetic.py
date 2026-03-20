import os
import json
import logging
import random
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def expand_honduras_synthetic():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Error: OPENAI_API_KEY not found in environment variables.")
        return

    client = OpenAI(api_key=api_key)
    
    input_file = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System/datasets/honduras/honduras_dataset.json"
    output_file = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System/datasets/honduras/honduras_dataset_expanded.json"
    
    if not os.path.exists(input_file):
        logger.error(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    original_size = len(original_data)
    target_size = 5000
    
    logger.info(f"Loading Honduras dataset: {original_size} records found.")
    
    expanded_data = list(original_data)
    seen_texts = {item["text"].strip().lower() for item in original_data}
    
    generated_count = 0
    
    # Prompt template for Honduran paraphrasing
    prompt_template = """
    You are a linguistic expert in Honduran Spanish (Español de Honduras).
    Paraphrase the following text into 2 different variations that perfectly preserve the authentic Honduran dialect.
    
    Constraints:
    - Maintain Honduran slang where possible (e.g., "maje", "pijudo", "chamba", "chepo", "birra", "bolo", "cipote").
    - Use "vos" (voseo) instead of "tú" as is common in Honduras.
    - Keep the tone conversational, natural, and realistic.
    - DO NOT convert into neutral Spanish. It must sound like someone from Tegucigalpa or San Pedro Sula.
    - The variations must be distinct from the original and from each other.
    
    Original Text: "{text}"
    
    Provide the output in strictly valid JSON format with a key "variations" containing a list of 2 strings.
    JSON:
    """

    # We need to reach 5000. 1633 originals + variations.
    # To be safe, we might need a few records to produce more than 2, but we'll start with 2 as requested.
    
    progress_bar = tqdm(total=target_size, initial=original_size, desc="Expanding Dataset")
    
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
                    {"role": "system", "content": "You are a professional linguist specializing in Central American Spanish dialects."},
                    {"role": "user", "content": prompt_template.format(text=text)}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                timeout=30
            )
            
            content = json.loads(response.choices[0].message.content)
            variations = content.get("variations", [])
            
            for var in variations:
                # Ensure var is a string
                if isinstance(var, list) and len(var) > 0:
                    var = var[0]
                
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
                        expanded_data.append(new_item)
                        seen_texts.add(var_lower)
                        progress_bar.update(1)
        except Exception as e:
            pass

    import threading
    lock = threading.Lock()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_item, original_data)

    # Second pass logic if needed (modified for threading)
    if len(expanded_data) < target_size:
        logger.info(f"Still need {target_size - len(expanded_data)} more samples. Starting second pass...")
        
        def process_second_pass(item):
            if len(expanded_data) >= target_size:
                return
            text = item.get("text", "")
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional linguist specializing in Central American Spanish dialects."},
                        {"role": "user", "content": f"Provide one more unique Honduran variation of this text: '{text}'. Use 'vos' and slang. JSON format: {{'variation': '...'}}"}
                    ],
                    response_format={"type": "json_object"},
                    timeout=30
                )
                var = json.loads(response.choices[0].message.content).get("variation", "").strip()
                with lock:
                    if var and var.lower() not in seen_texts and len(expanded_data) < target_size:
                        new_item = item.copy()
                        new_item["text"] = var
                        new_item["is_synthetic"] = True
                        expanded_data.append(new_item)
                        seen_texts.add(var.lower())
                        progress_bar.update(1)
            except:
                pass

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(process_second_pass, original_data)

    progress_bar.close()

    # Save final dataset
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(expanded_data, f, ensure_ascii=False, indent=4)

    # Print report
    print("\n" + "="*40)
    print("HONDURAS DATASET EXPANSION REPORT")
    print("="*40)
    print(f"Original dataset size: {original_size}")
    print(f"Generated samples:     {len(expanded_data) - original_size}")
    print(f"Final dataset size:     {len(expanded_data)}")
    print("="*40 + "\n")

if __name__ == "__main__":
    expand_honduras_synthetic()
