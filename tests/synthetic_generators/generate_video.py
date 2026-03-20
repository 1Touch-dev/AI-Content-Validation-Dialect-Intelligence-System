import os
import json
from moviepy.editor import ImageClip, AudioFileClip

def generate_synthetic_videos(manifest_path, output_dir, assets_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    img_positive = os.path.join(assets_dir, "football.jpg")
    img_negative = os.path.join(assets_dir, "city.jpg")
    
    print(f"Generating {len(metadata)} test MP4 videos...")
    
    new_manifest = []
    
    for idx, item in enumerate(metadata):
        audio_path = item['audio_file']
        video_filename = item['video_filename']
        output_path = os.path.join(output_dir, video_filename)
        
        # Decide if this video gets the positive or negative visual frame
        # Let's say half of Honduras gets positive, and standard gets negative
        is_positive_visual = (idx % 2 == 0)
        img_path = img_positive if is_positive_visual else img_negative
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create a static video matching the audio duration
            video_clip = ImageClip(img_path).set_duration(duration)
            video_clip = video_clip.set_audio(audio_clip)
            
            # Export with low fps for speed
            video_clip.write_videofile(
                output_path, 
                fps=1, 
                codec="libx264", 
                audio_codec="aac", 
                logger=None
            )
            
            # Cleanup moviepy open files
            video_clip.close()
            audio_clip.close()
            
            # Append expectations
            item['video_path'] = output_path
            item['expected_visual_pass'] = is_positive_visual
            new_manifest.append(item)
            
            print(f"[{idx+1}/{len(metadata)}] Saved {video_filename}")
        except Exception as e:
            print(f"Failed to generate video '{video_filename}': {e}")
            
    # Save the finalized manifest for the main test runner
    final_manifest_path = os.path.join(os.path.dirname(manifest_path), "final_e2e_manifest.json")
    with open(final_manifest_path, 'w', encoding='utf-8') as f:
        json.dump(new_manifest, f, indent=4, ensure_ascii=False)
        
    print(f"Video generation complete. Final E2E manifest saved to {final_manifest_path}")

if __name__ == "__main__":
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    manifest = os.path.join(base_dir, "tests", "expected_outputs", "e2e_video_manifest.json")
    out_dir = os.path.join(base_dir, "tests", "videos")
    assets = os.path.join(base_dir, "tests", "assets")
    
    generate_synthetic_videos(manifest, out_dir, assets)
