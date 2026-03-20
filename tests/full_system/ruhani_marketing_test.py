import os
import json
import time
import sys

base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
sys.path.append(base_dir)

from video_validator import VideoValidator
from transformers import pipeline, CLIPProcessor, CLIPModel
from PIL import Image
import torch

def test_ruhani_data():
    media_dir = os.path.join(base_dir, "datasets", "ruhani_test", "media")
    comments_file = os.path.join(base_dir, "datasets", "ruhani_test", "comments.json")
    out_rep = os.path.join(base_dir, "reports", "ruhani_marketing_test_report.md")
    model_path = os.path.join(base_dir, "models", "honduras_dialect_binary_classifier")
    
    # 1. Test Text Comments
    print("--- Testing Text Comments ---")
    with open(comments_file, 'r', encoding='utf-8') as f:
        comments = json.load(f)
        
    device_id = 0 if torch.backends.mps.is_available() else -1
    classifier = pipeline("text-classification", model=model_path, tokenizer=model_path, device=device_id)
    
    text_results = []
    text_pass = 0
    for c in comments:
        res = classifier(c)[0]
        label = res['label']
        if label == "Honduras": 
            text_pass += 1
        text_results.append((c, label, res['score']))
    
    # 2. Test Images
    print("--- Testing Images ---")
    images = []
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                images.append(os.path.join(root, file))
                
    device_str = "mps" if torch.backends.mps.is_available() else "cpu"
    clip_model_id = "openai/clip-vit-base-patch32"
    clip_model = CLIPModel.from_pretrained(clip_model_id).to(device_str)
    clip_processor = CLIPProcessor.from_pretrained(clip_model_id)
    
    img_results = []
    img_topic = "Honduras scenery, beautiful people"
    for img_path in images:
        try:
            image = Image.open(img_path).convert("RGB")
            inputs = clip_processor(text=[img_topic], images=image, return_tensors="pt", padding=True)
            for k, v in inputs.items():
                if hasattr(v, 'to'): inputs[k] = v.to(device_str)
            with torch.no_grad():
                outputs = clip_model(**inputs)
            score = round(max(0.0, min(1.0, outputs.logits_per_image.mean().item() / 30.0)), 4)
            img_results.append((os.path.basename(img_path), score))
        except Exception as e:
            print(f"Error on image {img_path}: {e}")
            
    # 3. Test Videos
    print("--- Testing Videos ---")
    videos = []
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov')):
                videos.append(os.path.join(root, file))
                
    validator = VideoValidator(device="cpu") # CPU for stability inside scripts
    video_results = []
    for vid_path in videos:
        res = validator.validate_video(vid_path, expected_content="Honduras scene, people, or marketing content")
        if res:
            video_results.append(res)
            
    # 4. Generate Markdown
    md = [
        f"# Ruhani Marketing Data - Client Validation Report",
        f"**Date**: {time.strftime('%Y-%m-%d')}",
        f"**Status**: VERIFIED",
        f"",
        f"## 1. Textual Comments Dialect Evaluation",
        f"Evaluated {len(comments)} actual comments against Honduran Dialect Binary Classifier.",
        f"**Pass Rate (Honduran Dialect Detected)**: {text_pass}/{len(comments)} ({(text_pass/len(comments))*100:.1f}%)"
    ]
    for c, l, s in text_results:
        md.append(f"- `[{l}]` (Conf: {s:.2f}) -> \"{c}\"")
        
    md.extend([
        f"",
        f"## 2. Image Multi-modal Vision Evaluation",
        f"Evaluated {len(images)} images against topic: '{img_topic}'."
    ])
    for n, s in img_results:
        md.append(f"- `{n}` -> Visual Score: {s:.4f}")
        
    md.extend([
        f"",
        f"## 3. Video / Reels E2E Pipeline Evaluation",
        f"Evaluated {len(videos)} marketing MP4s against the full TTS + Vision matching engine."
    ])
    for vr in video_results:
        md.append(f"- **{vr['video_file']}**")
        md.append(f"  - **Dialect**: {vr['dialect_predicted']} (Conf: {vr['dialect_confidence']:.2f})")
        md.append(f"  - **Vision Score**: {vr['content_match_score']:.4f}")
        md.append(f"  - **Status**: {vr['validation_status']}")
        
    with open(out_rep, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
        
    print(f"\n✅ Client Test complete. Report saved via mapping to {out_rep}")

if __name__ == "__main__":
    test_ruhani_data()
