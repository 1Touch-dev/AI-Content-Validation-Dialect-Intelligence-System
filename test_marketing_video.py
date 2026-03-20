import os
import sys

base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
sys.path.append(base_dir)

from video_validator import VideoValidator

def test_actual_marketing_data():
    video_path = os.path.join(base_dir, "sample_marketing_video.mp4")
    
    if not os.path.exists(video_path):
        print(f"File not found: {video_path}")
        return
        
    print(f"Testing actual marketing data: {video_path}")
    
    validator = VideoValidator()
    
    # Run validation with a generic expected topic suitable for marketing
    result = validator.validate_video(video_path, expected_content="Honduran marketing, people, products, commercial")
    
    import json
    print("\n" + "="*50)
    print("FINAL VALIDATION RESULT:")
    print("="*50)
    print(json.dumps(result, indent=4))
    
if __name__ == "__main__":
    test_actual_marketing_data()
