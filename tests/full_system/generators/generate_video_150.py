import os
import random
import time
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import json

def generate_150_videos():
    base_dir = "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System"
    vid_dir = os.path.join(base_dir, "tests", "full_system", "videos")
    audio_dir = os.path.join(base_dir, "tests", "full_system", "audio")
    image_dir = os.path.join(base_dir, "tests", "full_system", "images")
    os.makedirs(vid_dir, exist_ok=True)
    
    # Read assets lists
    audios_hon = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.startswith("audio_hon_")]
    audios_mex = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.startswith("audio_mex_")]
    audios_silence = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.startswith("audio_silence_")]
    
    # We generated images as well
    images_pos = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.startswith("image_pos_")]
    images_neg = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.startswith("image_neg_")]
    
    print(f"Loaded {len(audios_hon)} HON audio, {len(images_pos)} POS images.")
    
    def forge_video(audio_path, image_path, filename):
        out_path = os.path.join(vid_dir, filename)
        if not os.path.exists(out_path):
            audio_clip = AudioFileClip(audio_path)
            # Make image clip duration match audio
            video_clip = ImageClip(image_path).set_duration(audio_clip.duration)
            video_clip = video_clip.set_audio(audio_clip)
            # Write with low fps to speed up generation
            video_clip.write_videofile(out_path, fps=1, codec="libx264", audio_codec="aac", logger=None)
            video_clip.close()
            audio_clip.close()
        return out_path
        
    def forge_multiscene(audio_path, img1, img2, filename):
        out_path = os.path.join(vid_dir, filename)
        if not os.path.exists(out_path):
            audio_clip = AudioFileClip(audio_path)
            dur = audio_clip.duration
            c1 = ImageClip(img1).set_duration(dur/2)
            c2 = ImageClip(img2).set_duration(dur/2)
            video_clip = concatenate_videoclips([c1, c2])
            video_clip = video_clip.set_audio(audio_clip)
            video_clip.write_videofile(out_path, fps=1, codec="libx264", audio_codec="aac", logger=None)
            video_clip.close()
            audio_clip.close()
        return out_path
        
    dataset = []

    print("Forging 150 System Validation MP4s...")
    
    # 50 VALID
    for i in range(50):
        a = random.choice(audios_hon)
        im = random.choice(images_pos)
        path = forge_video(a, im, f"vid_valid_{i}.mp4")
        dataset.append({"path": path, "type": "VALID", "expected_dialect": "Honduras", "expected_visual": "pass"})
        
    # 20 DIALECT FAIL (Mexican speech, right visuals)
    for i in range(20):
        a = random.choice(audios_mex)
        im = random.choice(images_pos)
        path = forge_video(a, im, f"vid_dialectfail_{i}.mp4")
        dataset.append({"path": path, "type": "DIALECT_FAIL", "expected_dialect": "Other", "expected_visual": "pass"})
        
    # 20 VISUAL FAIL (Honduran speech, wrong visuals)
    for i in range(20):
        a = random.choice(audios_hon)
        im = random.choice(images_neg)
        path = forge_video(a, im, f"vid_visualfail_{i}.mp4")
        dataset.append({"path": path, "type": "VISUAL_FAIL", "expected_dialect": "Honduras", "expected_visual": "fail"})
        
    # 20 SILENT
    for i in range(20):
        a = random.choice(audios_silence)
        im = random.choice(images_pos)
        path = forge_video(a, im, f"vid_silent_{i}.mp4")
        dataset.append({"path": path, "type": "SILENT", "expected_dialect": "Other", "expected_visual": "pass"})
        
    # 20 NOISE AUDIO
    # For noise, we just use the silent tracks
    for i in range(20):
        a = random.choice(audios_silence)
        im = random.choice(images_neg)
        path = forge_video(a, im, f"vid_noise_{i}.mp4")
        dataset.append({"path": path, "type": "NOISE", "expected_dialect": "Other", "expected_visual": "fail"})
        
    # 20 MULTI SCENE (Speech + Mixed Visuals)
    for i in range(20):
        a = random.choice(audios_hon)
        im1 = random.choice(images_pos)
        im2 = random.choice(images_neg)
        path = forge_multiscene(a, im1, im2, f"vid_multiscene_{i}.mp4")
        dataset.append({"path": path, "type": "MULTI_SCENE", "expected_dialect": "Honduras", "expected_visual": "mixed"})
        
    print(f"Generated 150 Videos successfully.")
    
    # Save mapping for testing
    out_json = os.path.join(base_dir, "tests", "full_system", "results", "video_expected_dataset.json")
    with open(out_json, "w") as f:
        json.dump(dataset, f, indent=4)
        
    print("Exported dataset mapping to video_expected_dataset.json")

if __name__ == "__main__":
    generate_150_videos()
