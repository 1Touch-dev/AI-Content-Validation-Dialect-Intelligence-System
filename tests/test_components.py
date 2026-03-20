import os
import json
import time
import whisper
from transformers import pipeline
import evaluate
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch

def test_dialect_model(manifest_path, dialect_model_path):
    print("--- 1. Testing Dialect Classifier ---")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    classifier = pipeline(
        "text-classification", 
        model=dialect_model_path, 
        tokenizer=dialect_model_path, 
        device=0 if torch.backends.mps.is_available() else -1
    )
    
    y_true = []
    y_pred = []
    
    start_time = time.time()
    for item in metadata:
        text = item['text']
        expected = item['expected_model_prediction']
        
        # 1 = Honduras, 0 = Other
        y_true.append(1 if expected == "Honduras" else 0)
        
        res = classifier(text)[0]
        y_pred.append(1 if res['label'] == "Honduras" else 0)
        
    calc_time = time.time() - start_time
    
    # Evaluate
    acc_metric = evaluate.load("accuracy")
    f1_metric = evaluate.load("f1")
    
    acc = acc_metric.compute(predictions=y_pred, references=y_true)['accuracy']
    f1 = f1_metric.compute(predictions=y_pred, references=y_true, average='weighted')['f1']
    
    print(f"Total Text Samples: {len(metadata)}")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Time Taken: {calc_time:.2f}s")
    return {"accuracy": acc, "f1": f1}


def test_whisper_wer(manifest_path):
    print("\n--- 2. Testing Whisper Transcription WER ---")
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    model = whisper.load_model("base", device="cpu")
    wer_metric = evaluate.load("wer")
    
    references = []
    predictions = []
    
    start_time = time.time()
    for item in metadata:
        references.append(item['text'].lower().replace(".", "").replace(",", "").replace("¿", "").replace("?", ""))
        
        audio_path = item['audio_file']
        result = model.transcribe(audio_path, language="es")
        pred_text = result['text'].lower().replace(".", "").replace(",", "").replace("¿", "").replace("?", "").strip()
        predictions.append(pred_text)
        
    calc_time = time.time() - start_time
    wer_score = wer_metric.compute(predictions=predictions, references=references)
    
    print(f"Total Audio Samples: {len(metadata)}")
    print(f"Word Error Rate (WER): {wer_score:.4f}")
    print(f"Time Taken: {calc_time:.2f}s")
    return {"wer": wer_score}

def test_clip_matching(assets_dir):
    print("\n--- 3. Testing CLIP Vision Matching ---")
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    clip_model_id = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(clip_model_id).to(device)
    processor = CLIPProcessor.from_pretrained(clip_model_id)
    
    img_positive = os.path.join(assets_dir, "football.jpg")
    img_negative = os.path.join(assets_dir, "city.jpg")
    
    prompts = ["a football player on the field", "a street scene in a city"]
    
    for img_path in [img_positive, img_negative]:
        print(f"\nAnalyzing: {os.path.basename(img_path)}")
        image = Image.open(img_path).convert("RGB")
        
        inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True)
        for k, v in inputs.items():
            if hasattr(v, 'to'): inputs[k] = v.to(device)
                
        with torch.no_grad():
            outputs = model(**inputs)
            
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).cpu().numpy()[0]
        
        for i, prompt in enumerate(prompts):
            print(f" - '{prompt}': {probs[i]*100:.1f}% confidence")

if __name__ == "__main__":
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    manifest = os.path.join(base_dir, "tests", "expected_outputs", "final_e2e_manifest.json")
    dialect_model = os.path.join(base_dir, "models", "honduras_dialect_binary_classifier")
    assets = os.path.join(base_dir, "tests", "assets")
    
    print("================ COMPONENT TESTS ================")
    test_dialect_model(manifest, dialect_model)
    test_whisper_wer(manifest)
    test_clip_matching(assets)
    print("=================================================")
