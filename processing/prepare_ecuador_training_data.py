"""
Prepare balanced binary training datasets for Ecuador dialect classification.
"""
import os
import json
import random

def load_data(file_path):
    """Safely load a JSON file if it exists."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def prepare_ecuador_training_data():
    """
    Merge Ecuador (Label 1) and Non-Ecuador (Label 0) records into balanced spits.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Path Configuration
    paths = {
        "ecuador": os.path.join(base_dir, "datasets/ecuador/ecuador_dataset_expanded.json"),
        "honduras": os.path.join(base_dir, "datasets/honduras/honduras_dataset_expanded.json"),
        "other": os.path.join(base_dir, "datasets/other/other_spanish_dataset.json"),
        "mexico": os.path.join(base_dir, "datasets/mexico/mexico_dataset.json")
    }
    
    # 1. Load Ecuador (Target: 3500)
    ecuador_data = load_data(paths["ecuador"])
    label_1 = [{"text": item["text"], "label": 1} for item in ecuador_data]
        
    random.shuffle(label_1)
    label_1 = label_1[:3500] if len(label_1) >= 3500 else label_1
    
    # 2. Load Non-Ecuador (Target: 3500)
    raw_label_0 = []
    for source in ["other", "honduras", "mexico"]:
        raw_label_0.extend(load_data(paths[source]))
                
    # Deduplicate and shuffle label_0
    unique_texts = set()
    label_0 = []
    for item in raw_label_0:
        txt = item["text"].strip().lower()
        if txt not in unique_texts:
            label_0.append({"text": item["text"], "label": 0})
            unique_texts.add(txt)
            
    random.shuffle(label_0)
    label_0 = label_0[:3500] if len(label_0) >= 3500 else label_0
    
    print(f"Ecuador records: {len(label_1)}")
    print(f"Non-Ecuador records: {len(label_0)}")
    
    all_data = label_1 + label_0
    random.shuffle(all_data)
    
    # 3. Split 80/10/10
    total = len(all_data)
    train_idx = int(total * 0.8)
    val_idx = int(total * 0.9)
    
    datasets = {
        "train": all_data[:train_idx],
        "validation": all_data[train_idx:val_idx],
        "test": all_data[val_idx:]
    }
    
    output_dir = os.path.join(base_dir, "datasets/ecuador")
    os.makedirs(output_dir, exist_ok=True)
    
    for name, dataset in datasets.items():
        # Save JSON
        json_path = os.path.join(output_dir, f"{name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)
        # Save JSONL
        jsonl_path = os.path.join(output_dir, f"{name}.jsonl")
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                
    print(f"Training data saved to {output_dir}/ (Total: {total})")

if __name__ == "__main__":
    prepare_ecuador_training_data()
