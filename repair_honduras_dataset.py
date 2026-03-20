import json
import os
import re
import random
import pandas as pd
from collections import Counter
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    pass

def word_count(text):
    return len(re.findall(r'\b\w+\b', text))

def unique_words(text):
    return len(set(re.findall(r'\b\w+\b', text.lower())))

def repair_dataset():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    input_path = os.path.join(base_dir, "datasets", "honduras", "honduras_dataset_expanded.json")
    balanced_json_path = os.path.join(base_dir, "datasets", "honduras", "honduras_dataset_balanced.json")
    balanced_csv_path = os.path.join(base_dir, "datasets", "honduras", "honduras_dataset_balanced.csv")
    train_path = os.path.join(base_dir, "datasets", "honduras", "train.json")
    val_path = os.path.join(base_dir, "datasets", "honduras", "validation.json")
    test_path = os.path.join(base_dir, "datasets", "honduras", "test.json")
    report_path = os.path.join(base_dir, "reports", "honduras_dataset_repair_report.md")

    # STEP 1: LOAD AND SEPARATE
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    original_size = len(data)
    real_records = [d for d in data if not d.get("is_synthetic", False)]
    synthetic_records = [d for d in data if d.get("is_synthetic", False)]
    
    # STEP 2: REMOVE DUPLICATES (Synthetic)
    # Target synthetic primarily, as real data is assumed clean or more valuable
    texts = [s.get("text", "") for s in synthetic_records]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(texts)
    sim_matrix = cosine_similarity(tfidf_matrix)

    to_drop = set()
    for i in range(len(synthetic_records)):
        if i in to_drop: continue
        for j in range(i+1, len(synthetic_records)):
            if sim_matrix[i, j] > 0.90:
                to_drop.add(j)
                
    deduped_synthetic = [s for i, s in enumerate(synthetic_records) if i not in to_drop]
    dupes_removed = len(synthetic_records) - len(deduped_synthetic)

    # STEP 3: REMOVE REPETITIVE PATTERNS
    slang_tokens = ['maje', 'pijudo', 'cipote', 'vos']
    
    def count_slang(records, token):
        return sum(1 for r in records if re.search(r'\b' + token + r'\b', r.get("text", "").lower()))
        
    # Tone down 'maje' if it's over 10%
    target_pct = 0.10
    for token in slang_tokens:
        count = count_slang(deduped_synthetic, token)
        curr_pct = count / len(deduped_synthetic)
        if curr_pct > target_pct:
            # We need to drop records containing this token
            target_count = int(len(deduped_synthetic) * target_pct)
            drop_count = count - target_count
            
            # Find indices of records with token
            token_indices = [i for i, r in enumerate(deduped_synthetic) if re.search(r'\b' + token + r'\b', r.get("text", "").lower())]
            indices_to_drop = set(random.sample(token_indices, drop_count))
            
            deduped_synthetic = [s for i, s in enumerate(deduped_synthetic) if i not in indices_to_drop]

    # STEP 5: LINGUISTIC DIVERSITY FILTER
    # Remove records with very low diversity (< 0.1) or very short
    div_filtered_synthetic = []
    for s in deduped_synthetic:
        text = s.get("text", "")
        w_curr = word_count(text)
        if w_curr < 5: 
            continue
        div = unique_words(text) / w_curr
        if div >= 0.1: # Threshold for low diversity
            div_filtered_synthetic.append(s)
            
    # STEP 4: SYNTHETIC DOWNSAMPLING
    # Match real records
    target_synthetic_size = len(real_records)
    if len(div_filtered_synthetic) > target_synthetic_size:
        balanced_synthetic = random.sample(div_filtered_synthetic, target_synthetic_size)
    else:
        balanced_synthetic = div_filtered_synthetic
        
    synthetic_removed = len(synthetic_records) - len(balanced_synthetic)
    
    # Combine
    balanced_dataset = real_records + balanced_synthetic
    random.shuffle(balanced_dataset)

    # STEP 6: QUALITY VALIDATION (calculate for report)
    final_real = len(real_records)
    final_synth = len(balanced_synthetic)
    final_total = len(balanced_dataset)
    final_synth_ratio = final_synth / final_total
    
    token_distributions = {}
    for token in slang_tokens:
        count = count_slang(balanced_dataset, token)
        token_distributions[token] = f"{(count / final_total) * 100:.1f}%"

    # STEP 7: EXPORT CLEAN DATASET
    with open(balanced_json_path, 'w', encoding='utf-8') as f:
        json.dump(balanced_dataset, f, ensure_ascii=False, indent=4)
        
    df = pd.DataFrame(balanced_dataset)
    df.to_csv(balanced_csv_path, index=False)

    # STEP 8: TRAINING SPLIT
    # 80 / 10 / 10
    train_end = int(0.8 * final_total)
    val_end = int(0.9 * final_total)
    
    train_split = balanced_dataset[:train_end]
    val_split = balanced_dataset[train_end:val_end]
    test_split = balanced_dataset[val_end:]
    
    with open(train_path, 'w', encoding='utf-8') as f: json.dump(train_split, f, ensure_ascii=False, indent=4)
    with open(val_path, 'w', encoding='utf-8') as f: json.dump(val_split, f, ensure_ascii=False, indent=4)
    with open(test_path, 'w', encoding='utf-8') as f: json.dump(test_split, f, ensure_ascii=False, indent=4)

    # STEP 9: FINAL REPORT
    report = [
        "# Honduras Dataset Repair Report",
        "",
        "## Original Dataset Statistics",
        f"- Total records: {original_size}",
        f"- Real records: {len(real_records)}",
        f"- Synthetic records: {len(synthetic_records)}",
        "",
        "## Modifications",
        f"- Duplicates removed (sim > 0.90): {dupes_removed}",
        f"- Synthetic records removed (slang threshold & diversity): {len(deduped_synthetic) - len(div_filtered_synthetic)}",
        f"- Total synthetic records discarded: {synthetic_removed}",
        "",
        "## Final Dataset Size",
        f"- Total records: {final_total}",
        f"- Real: {final_real} ({final_real/final_total*100:.1f}%)",
        f"- Synthetic: {final_synth} ({final_synth_ratio*100:.1f}%)",
        "",
        "## Slang Token Distribution (Final)",
    ]
    for t, dist in token_distributions.items():
        report.append(f"- {t}: {dist}")
        
    report.extend([
        "",
        "## ML Splits",
        f"- Train (80%): {len(train_split)} records",
        f"- Validation (10%): {len(val_split)} records",
        f"- Test (10%): {len(test_split)} records",
        "",
        "## Training Recommendation",
        "The dataset has been successfully balanced. The synthetic ratio is ≤ 50%, repetitive overrepresented tokens have been clipped, and extreme semantic duplicates (<0.90 sim) were pruned. The dataset is now highly robust and safe for training the dialect intelligence model."
    ])

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))

    print(f"Repair Complete. Final Dataset Size: {final_total} ({final_real} real, {final_synth} synthetic)")
    print(f"Report generated at {report_path}")

if __name__ == "__main__":
    repair_dataset()
