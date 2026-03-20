import json
import os
import re
import random
from collections import Counter
import time

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    import difflib

def word_count(text):
    return len(re.findall(r'\b\w+\b', text))

def unique_words(text):
    return len(set(re.findall(r'\b\w+\b', text.lower())))

def analyze_bias():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    dataset_path = os.path.join(base_dir, "datasets", "honduras", "honduras_dataset_expanded.json")
    report_path = os.path.join(base_dir, "reports", "honduras_dataset_bias_audit.md")
    
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    total_records = len(data)
    
    real_records = []
    synthetic_records = []
    
    for item in data:
        if item.get("is_synthetic", False):
            synthetic_records.append(item)
        else:
            real_records.append(item)
            
    real_count = len(real_records)
    synthetic_count = len(synthetic_records)
    
    real_pct = (real_count / total_records) * 100
    synthetic_pct = (synthetic_count / total_records) * 100
    
    # Slang analysis
    slang_tokens = ['maje', 'pijudo', 'cipote', 'vos']
    token_stats = {token: {'real_count': 0, 'synthetic_count': 0, 'total': 0} for token in slang_tokens}
    
    def check_slang(record, is_synthetic):
        text = record.get("text", "").lower()
        for token in slang_tokens:
            if re.search(r'\b' + token + r'\b', text):
                token_stats[token]['total'] += 1
                if is_synthetic:
                    token_stats[token]['synthetic_count'] += 1
                else:
                    token_stats[token]['real_count'] += 1

    # Style distribution
    real_words = []
    real_unique_words = set()
    synth_words = []
    synth_unique_words = set()
    
    for r in real_records:
        check_slang(r, False)
        text = r.get("text", "")
        words = re.findall(r'\b\w+\b', text.lower())
        real_words.append(len(words))
        real_unique_words.update(words)
        
    for s in synthetic_records:
        check_slang(s, True)
        text = s.get("text", "")
        words = re.findall(r'\b\w+\b', text.lower())
        synth_words.append(len(words))
        synth_unique_words.update(words)
        
    avg_real_len = sum(real_words) / len(real_words) if real_words else 0
    avg_synth_len = sum(synth_words) / len(synth_words) if synth_words else 0
    
    # Approximate Vocab Diversity (Unique words / total subset)
    real_vocab_div = len(real_unique_words) / sum(real_words) if sum(real_words) else 0
    synth_vocab_div = len(synth_unique_words) / sum(synth_words) if sum(synth_words) else 0

    # Duplicate / Similarity Check
    texts = [item.get("text", "") for item in data]
    high_sim_clusters = 0
    
    if SKLEARN_AVAILABLE:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        sim_matrix = cosine_similarity(tfidf_matrix)
        
        # Upper triangular iteration to count > 0.90 pairs without diagonal
        # To avoid O(N^2) fully printing, just count
        sim_pairs = 0
        for i in range(total_records):
            for j in range(i+1, total_records):
                if sim_matrix[i, j] > 0.90:
                    sim_pairs += 1
        high_sim_clusters = sim_pairs
    else:
        # Fallback to random sampling if no sklearn, to save time on 12.5M pairs
        sample_size = min(1000, len(texts))
        sample_texts = random.sample(texts, sample_size)
        sim_pairs = 0
        for i in range(sample_size):
            for j in range(i+1, sample_size):
                ratio = difflib.SequenceMatcher(None, sample_texts[i], sample_texts[j]).ratio()
                if ratio > 0.90:
                    sim_pairs += 1
        high_sim_clusters = int(sim_pairs * ((total_records / sample_size) ** 2)) # Extrapolate

    flags = []
    for token, stats in token_stats.items():
        pct = (stats['total'] / total_records) * 100
        if pct > 30:
            flags.append(f"⚠️ Token '{token}' appears in {pct:.1f}% of samples (highly overrepresented).")

    if synthetic_pct > 60:
        flags.append(f"⚠️ Synthetic records exceed 60% ({synthetic_pct:.1f}%). High risk of model over-fitting to synthetic generation patterns.")
        
    if high_sim_clusters > (total_records * 0.05):
        flags.append(f"⚠️ High number of extremely similar records estimated ({high_sim_clusters} pairs > 0.90 sim). Risk of duplicates.")

    report = []
    report.append("# Honduras Dataset Bias Audit\n")
    report.append("## 1. Source Analysis")
    report.append(f"- **Total Records**: {total_records}")
    report.append(f"- **Real Records**: {real_count} ({real_pct:.1f}%)")
    report.append(f"- **Synthetic Records**: {synthetic_count} ({synthetic_pct:.1f}%)\n")
    
    report.append("## 2. Language Pattern Analysis (Slang Frequency)")
    for token, stats in token_stats.items():
        pct = (stats['total'] / total_records) * 100
        real_tok_pct = (stats['real_count'] / real_count) * 100 if real_count else 0
        synth_tok_pct = (stats['synthetic_count'] / synthetic_count) * 100 if synthetic_count else 0
        report.append(f"- **{token}**: Overall {pct:.1f}% | Real {real_tok_pct:.1f}% | Synthetic {synth_tok_pct:.1f}%")
        
    report.append("\n## 3. Style Distribution")
    report.append("- **Average Sentence Length**:")
    report.append(f"  - Real: {avg_real_len:.1f} words")
    report.append(f"  - Synthetic: {avg_synth_len:.1f} words")
    report.append("- **Vocabulary Diversity (Unique/Total Words)**:")
    report.append(f"  - Real: {real_vocab_div:.4f}")
    report.append(f"  - Synthetic: {synth_vocab_div:.4f}")
    
    report.append("\n## 4. Duplicate Pattern Check")
    report.append(f"- Pairs with > 0.90 similarity (estimated/counted): {high_sim_clusters}")
    
    report.append("\n## 5. Flags & Risks")
    if not flags:
        report.append("- No critical bias flags detected.")
    else:
        for f in flags:
            report.append(f)
            
    report.append("\n## 6. Real-World Validation Sample (20 Random Real Samples)")
    sample_real = random.sample(real_records, min(20, len(real_records)))
    for i, sr in enumerate(sample_real, 1):
        report.append(f"{i}. *{sr.get('text', '').strip()}*")
        
    report.append("\n## 7. Final Recommendation")
    if synthetic_pct <= 60 and not any("overrepresented" in str(f) for f in flags):
        report.append("**Dataset is generally safe for training**, provided similarity clusters and specific slang tokens are within expected natural distribution.")
    else:
        report.append("**Dataset requires additional real data scraping or careful downsampling of synthetic records.** Synthetic distribution and/or single-token bias is too high, leading to likely model brittle behavior in real-world inference.")
        
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print(f"Report generated at {report_path}")
    print(f"Synthetic VS Real: {synthetic_pct:.1f}% VS {real_pct:.1f}%")
    print(f"Overall Slang Frequency (vos): {((token_stats['vos']['total'] / total_records) * 100):.1f}%")
    if flags:
        print("FLAGS TRIGGERED:")
        for f in flags:
            print(f)
            
if __name__ == "__main__":
    analyze_bias()
