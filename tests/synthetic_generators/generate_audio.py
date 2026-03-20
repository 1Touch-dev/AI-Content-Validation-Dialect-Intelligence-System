import os
import json
import time
from gtts import gTTS

def generate_synthetic_audio(input_json, output_dir, max_samples=50):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_json, 'r', encoding='utf-8') as f:
        text_cases = json.load(f)
        
    # Filter out gibberish for the main audio test (we'll do noise later if needed)
    valid_cases = [c for c in text_cases if c['type'] != 'Gibberish']
    
    # Take a balanced subset
    honduras_cases = [c for c in valid_cases if c['type'] == 'Honduras'][:max_samples//2]
    other_cases = [c for c in valid_cases if c['type'] in ['Mexico', 'Neutral']][:max_samples//2]
    
    test_subset = honduras_cases + other_cases
    
    metadata = []
    
    print(f"Generating audio for {len(test_subset)} samples...")
    for idx, item in enumerate(test_subset):
        text = item['text']
        c_type = item['type']
        
        # gTTS dialect hack: 'com.mx' for Mexico, 'es' for standard
        tld_val = 'com.mx' if c_type == 'Mexico' else 'es'
        
        filename = f"audio_{idx:03d}_{c_type}.mp3"
        filepath = os.path.join(output_dir, filename)
        
        try:
            tts = gTTS(text=text, lang='es', tld=tld_val, slow=False)
            tts.save(filepath)
            
            # Store metadata for E2E testing
            item['audio_file'] = filepath
            item['video_filename'] = f"test_video_{idx:03d}_{c_type}.mp4"
            metadata.append(item)
            
            print(f"[{idx+1}/{len(test_subset)}] Saved {filename}")
            time.sleep(1) # Prevent rate limits
        except Exception as e:
            print(f"Failed to generate audio for '{text}': {e}")
            
    # Save the E2E manifest
    manifest_path = os.path.join(os.path.dirname(input_json), "e2e_video_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
        
    print(f"Audio generation complete. Manifest saved to {manifest_path}")

if __name__ == "__main__":
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    input_file = os.path.join(base_dir, "tests", "expected_outputs", "text_cases.json")
    out_dir = os.path.join(base_dir, "tests", "audio")
    
    generate_synthetic_audio(input_file, out_dir, max_samples=50)
