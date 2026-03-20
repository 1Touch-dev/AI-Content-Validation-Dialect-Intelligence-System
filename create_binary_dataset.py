import os
import json
import random
import pandas as pd

def create_binary_dataset():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    honduras_path = os.path.join(base_dir, "datasets", "honduras", "honduras_dataset_balanced.json")
    other_path = os.path.join(base_dir, "datasets", "other", "other_spanish_dataset.json")
    
    # Target files (overwriting the single-class splits to reuse training scripts easier or we can put them somewhere else. Let's overwrite)
    train_path = os.path.join(base_dir, "datasets", "honduras", "train.jsonl")
    val_path = os.path.join(base_dir, "datasets", "honduras", "validation.jsonl")
    test_path = os.path.join(base_dir, "datasets", "honduras", "test.jsonl")
    
    # 1. Load data
    with open(honduras_path, 'r', encoding='utf-8') as f:
        honduras_data = json.load(f)
        
    with open(other_path, 'r', encoding='utf-8') as f:
        other_data = json.load(f)
        
    # 2. Add labels & Normalize structure
    # Honduras -> 1, Other -> 0
    # Keep it simple: Add a 'label' field explicitly or 'binary_dialect'
    for item in honduras_data:
        item['binary_dialect'] = 'Honduras'
        item['label'] = 1.0

    for item in other_data:
        item['binary_dialect'] = 'Other'
        item['label'] = 0.0
        
    print(f"Loaded {len(honduras_data)} Honduras samples and {len(other_data)} Other samples.")
    
    # 3. Balance Datasets
    target_size = min(len(honduras_data), len(other_data))
    print(f"Balancing size to {target_size} samples per class to maintain 50/50 balance.")
    
    balanced_honduras = random.sample(honduras_data, target_size)
    balanced_other = random.sample(other_data, target_size)
    
    binary_dataset = balanced_honduras + balanced_other
    random.shuffle(binary_dataset)
    
    print(f"Total binary dataset size: {len(binary_dataset)}")
    
    # 4. Train / Val / Test (80/10/10)
    total = len(binary_dataset)
    train_end = int(total * 0.8)
    val_end = int(total * 0.9)
    
    train_split = binary_dataset[:train_end]
    val_split = binary_dataset[train_end:val_end]
    test_split = binary_dataset[val_end:]
    
    # 5. Export JSONL (required for reliable huggingface loading)
    def save_jsonl(data, path):
        with open(path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
    save_jsonl(train_split, train_path)
    save_jsonl(val_split, val_path)
    save_jsonl(test_split, test_path)
    
    print("Export Complete:")
    print(f"Train: {len(train_split)}")
    print(f"Validation: {len(val_split)}")
    print(f"Test: {len(test_split)}")
    print("Files saved to datasets/honduras as .jsonl")

if __name__ == "__main__":
    create_binary_dataset()
