import json
import os

def prepare_ecuador_data():
    raw_dir = "storage/raw_data"
    output_file = "storage/raw_data/ecuador_merged_raw.json"
    
    merged_data = []
    
    # 1. Process Twitter
    twitter_path = os.path.join(raw_dir, "ecuador_twitter_raw.json")
    if os.path.exists(twitter_path):
        with open(twitter_path, "r", encoding="utf-8") as f:
            tweets = json.load(f)
            for t in tweets:
                text = t.get("full_text") or t.get("text")
                if text:
                    merged_data.append({
                        "text": text,
                        "source": "twitter",
                        "country": "Ecuador"
                    })
    
    # 2. Process Reddit
    reddit_path = os.path.join(raw_dir, "ecuador_reddit_raw.json")
    if os.path.exists(reddit_path):
        with open(reddit_path, "r", encoding="utf-8") as f:
            posts = json.load(f)
            for p in posts:
                # Some are comments, some are posts
                text = p.get("body") or p.get("selftext") or p.get("title")
                if text:
                    merged_data.append({
                        "text": text,
                        "source": "reddit",
                        "country": "Ecuador"
                    })
                    
    # 3. Process Google Reviews
    reviews_path = os.path.join(raw_dir, "ecuador_reviews_raw.json")
    if os.path.exists(reviews_path):
        with open(reviews_path, "r", encoding="utf-8") as f:
            reviews = json.load(f)
            for r in reviews:
                text = r.get("text")
                if text:
                    merged_data.append({
                        "text": text,
                        "source": "google_reviews",
                        "country": "Ecuador"
                    })
                    
    print(f"Total merged records: {len(merged_data)}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)
        
    print(f"Merged data saved to {output_file}")

if __name__ == "__main__":
    prepare_ecuador_data()
