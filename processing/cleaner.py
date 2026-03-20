import os
import json
import logging
import pandas as pd
import re

# Configure logging
logger = logging.getLogger(__name__)

def merge_datasets(raw_dir="storage/raw_data"):
    """
    Combines Twitter, Reddit, and Reviews datasets into a single list of standardized records.
    """
    combined = []
    
    # Twitter
    twitter_path = os.path.join(raw_dir, "twitter.json")
    if os.path.exists(twitter_path):
        with open(twitter_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                combined.append({
                    "platform": "twitter",
                    "text": item.get("full_text") or item.get("text") or "",
                    "timestamp": item.get("created_at"),
                    "author": item.get("user", {}).get("screen_name"),
                    "engagement": {
                        "likes": item.get("favorite_count"),
                        "retweets": item.get("retweet_count")
                    },
                    "source_url": f"https://twitter.com/i/web/status/{item.get('id_str')}"
                })
        logger.info(f"Loaded {len(data)} items from Twitter.")

    # Reddit
    reddit_path = os.path.join(raw_dir, "reddit.json")
    if os.path.exists(reddit_path):
        with open(reddit_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                combined.append({
                    "platform": "reddit",
                    "text": item.get("body") or item.get("selftext") or item.get("title") or "",
                    "timestamp": item.get("created_utc"),
                    "author": item.get("author"),
                    "engagement": {
                        "score": item.get("score"),
                        "num_comments": item.get("num_comments")
                    },
                    "source_url": item.get("url")
                })
        logger.info(f"Loaded {len(data)} items from Reddit.")

    # Reviews
    reviews_path = os.path.join(raw_dir, "reviews.json")
    if os.path.exists(reviews_path):
        with open(reviews_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                combined.append({
                    "platform": "google_reviews",
                    "text": item.get("text") or "",
                    "timestamp": item.get("publishAt"),
                    "author": item.get("authorTitle"),
                    "engagement": {
                        "stars": item.get("stars")
                    },
                    "source_url": item.get("reviewId") # ID for source mapping
                })
        logger.info(f"Loaded {len(data)} items from Google Reviews.")

    output_path = os.path.join(raw_dir, "combined_dataset.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=4)
    logger.info(f"Merged {len(combined)} items into {output_path}")
    return combined

def clean_data(data):
    """
    Cleans the merged dataset: removes duplicates, spam, ads, and short posts.
    """
    if not data:
        return []

    df = pd.DataFrame(data)
    
    # 1. Remove empty text
    df = df[df['text'].str.strip() != ""]
    
    # 2. Remove duplicates by text
    df = df.drop_duplicates(subset=['text'])
    
    # 3. Remove short posts (< 5 words)
    df = df[df['text'].apply(lambda x: len(str(x).split()) >= 5)]
    
    # 4. Simple spam/ad heuristic (very basic)
    ads_keywords = ['buy now', 'discount', 'win a 100', 'follow me for']
    def is_spam(text):
        text_lower = text.lower()
        return any(kw in text_lower for kw in ads_keywords)
    
    df = df[~df['text'].apply(is_spam)]
    
    # 5. Normalize text (remove extra whitespace)
    df['text'] = df['text'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip())
    
    cleaned_data = df.to_dict(orient='records')
    
    output_path = os.path.join("storage", "cleaned_data", "cleaned_dataset.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
    
    logger.info(f"Cleaned dataset: {len(cleaned_data)} items remaining. Saved to {output_path}")
    return cleaned_data

if __name__ == "__main__":
    combined = merge_datasets()
    clean_data(combined)
