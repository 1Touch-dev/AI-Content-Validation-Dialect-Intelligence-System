import os
import json
import torch
import whisper
import warnings
import tempfile
import ffmpeg
from transformers import pipeline, CLIPProcessor, CLIPModel
from PIL import Image
import easyocr

# Suppress warnings
warnings.filterwarnings("ignore")


def _resolve_base_dir():
    """Resolve project base directory with environment override support."""
    if os.getenv("BASE_DIR"):
        return os.getenv("BASE_DIR")
    return os.path.dirname(os.path.abspath(__file__))


def _resolve_dialect_model_path(dialect_model_path):
    """
    Resolve dialect model path with explicit environment override support.
    Preference order:
      1) MODEL_PATH env (absolute or relative to BASE_DIR)
      2) dialect_model_path argument (absolute or relative to BASE_DIR)
    """
    base_dir = _resolve_base_dir()
    env_model_path = os.getenv("MODEL_PATH")

    if env_model_path:
        if os.path.isabs(env_model_path):
            return env_model_path
        return os.path.join(base_dir, env_model_path)

    if os.path.isabs(dialect_model_path):
        return dialect_model_path
    return os.path.join(base_dir, dialect_model_path)


class VideoValidator:
    def __init__(self, dialect_model_path="models/honduras_dialect_binary_classifier", device=None):
        base_dir = _resolve_base_dir()
        self.model_path = _resolve_dialect_model_path(dialect_model_path)
        self.reports_dir = os.path.join(base_dir, "reports")
        
        if device is None:
            self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Initializing Video Validator. Device: {self.device}")
        
        # 1. Load Whisper
        print("Loading Whisper model (base)...")
        self.whisper_model = whisper.load_model("base", device="cpu") # Whisper base runs fast enough on CPU, avoids some MPS audio bugs
        
        # 2. Load Dialect Classifier
        print("Loading Dialect Classifier...")
        if not os.path.isdir(self.model_path):
            raise FileNotFoundError(
                f"Dialect model directory not found: {self.model_path}. "
                "Set MODEL_PATH to a valid local model folder or train the model first."
            )
        # device=0 for cuda/mps in pipeline, -1 for cpu
        hf_device = 0 if self.device in ["cuda", "mps"] else -1
        self.dialect_classifier = pipeline(
            "text-classification", 
            model=self.model_path, 
            tokenizer=self.model_path, 
            device=hf_device
        )
        
        # 3. Load CLIP for Vision Analysis
        print("Loading CLIP Vision model...")
        self.clip_model_id = "openai/clip-vit-base-patch32"
        self.clip_model = CLIPModel.from_pretrained(self.clip_model_id).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained(self.clip_model_id)
        
        # 4. Load EasyOCR Strict Blacklist Evaluator
        print("Loading EasyOCR for Strict Text Validation...")
        self.ocr_reader = easyocr.Reader(['en', 'es'], gpu=False) # Processing frames locally via CPU for environment stability
        
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Setup persistent file logging
        import logging
        self.logs_dir = os.path.join(base_dir, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.logger = logging.getLogger("VideoValidator")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            fh = logging.FileHandler(os.path.join(self.logs_dir, "video_validation.log"))
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(fh)
            
        print("Initialization complete.")

    def extract_audio(self, video_path):
        """Extracts audio from video to a temporary WAV file."""
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        try:
            (
                ffmpeg
                .input(video_path)
                .output(temp_audio, acodec='pcm_s16le', ac=1, ar='16k', loglevel='quiet')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return temp_audio
        except ffmpeg.Error as e:
            print(f"FFmpeg audio extraction error: {e.stderr.decode()}")
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            return None

    def extract_frames(self, video_path, fps=0.5):
        """Extracts frames from video (default: 1 frame every 2 seconds)."""
        temp_dir = tempfile.mkdtemp()
        output_pattern = os.path.join(temp_dir, "frame_%04d.jpg")
        try:
            (
                ffmpeg
                .input(video_path)
                .filter('fps', fps=fps)
                .output(output_pattern, loglevel='quiet')
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            frames = []
            for img_file in sorted(os.listdir(temp_dir)):
                if img_file.endswith(".jpg"):
                    frames.append(os.path.join(temp_dir, img_file))
            return frames, temp_dir
        except ffmpeg.Error as e:
            print(f"FFmpeg frame extraction error: {e.stderr.decode()}")
            return [], temp_dir

    def validate_video(self, video_path, expected_content="Honduran football player"):
        """Runs the full validation pipeline on a video file."""
        print(f"\n--- Validating Video: {os.path.basename(video_path)} ---")
        import time
        start_time = time.time()
        self.logger.info(f"Starting validation for {os.path.basename(video_path)}")
        
        if not os.path.exists(video_path):
            self.logger.error(f"Error: Video file not found at {video_path}")
            print("Error: Video file not found.")
            return None
            
        # STEP 1: AUDIO EXTRACTION
        print("1. Extracting audio...")
        audio_path = self.extract_audio(video_path)
        
        # STEP 2: SPEECH TRANSCRIPTION
        print("2. Transcribing audio (Whisper)...")
        transcript = ""
        if audio_path:
            result = self.whisper_model.transcribe(audio_path, language="es")
            transcript = result["text"].strip()
            os.remove(audio_path) # cleanup
            print(f"   Transcript: '{transcript}'")
        else:
            print("   Warning: Could not extract audio.")
            
        # STEP 3: DIALECT VALIDATION
        print("3. Validating dialect...")
        dialect_prediction = "Other"
        dialect_confidence = 0.0
        dialect_pass = False
        
        if transcript:
            # Send to model
            res = self.dialect_classifier(transcript)[0]
            dialect_prediction = res['label']
            dialect_confidence = round(res['score'], 4)
            # Honduras = Pass
            dialect_pass = (dialect_prediction == "Honduras")
            print(f"   Prediction: {dialect_prediction} ({dialect_confidence*100:.1f}%)")
        else:
            print("   Warning: No transcript to validate.")

        # STEP 4: FRAME EXTRACTION
        print("4. Extracting frames...")
        frames, frames_dir = self.extract_frames(video_path)
        print(f"   Extracted {len(frames)} frames for analysis.")

        # STEP 5: VISION ANALYSIS
        print(f"5. Analyzing visual content against: '{expected_content}'...")
        content_match_score = 0.0
        ocr_blacklist_triggered = False
        blacklist = ["ecuador", "mexico", "costa rica", "guatemala", "colombia", "peru", "argentina", "chile", "uruguay", "paraguay", "bolivia", "venezuela"]
        
        if frames:
            images = [Image.open(f).convert("RGB") for f in frames]
            
            # --- OCR CHECK ---
            print("   Running strict OCR evaluations on extracted frames...")
            for img_path in frames:
                if ocr_blacklist_triggered:
                    break
                results = self.ocr_reader.readtext(img_path, detail=0)
                text = " ".join(results).lower()
                for b in blacklist:
                    if b in text:
                        print(f"   [FAIL - BLACKLIST] OCR intercepted term: '{b.upper()}' embedded in media frame!")
                        ocr_blacklist_triggered = True
                        break
            
            if ocr_blacklist_triggered:
                content_match_score = 0.0 # Force failing validation
                print("   Visual Match Score forced to 0.0 due to structural OCR anomaly.")
            else:
                # --- COMPARATIVE CLIP Softmax Algorithm ---
                # We compare expected_content against explicitly contrary targets to force the embedding manifold to separate similarities
                target_list = [expected_content, "Ecuador scenery or people", "Mexico scenery or people", "Generic unbranded people or background"]
                
                inputs = self.clip_processor(text=target_list, images=images, return_tensors="pt", padding=True)
                for k, v in inputs.items():
                    if hasattr(v, 'to'):
                        inputs[k] = v.to(self.device)
                
                with torch.no_grad():
                    outputs = self.clip_model(**inputs)
                    
                # logits_per_image has shape [Batch, Targets]. Softmax over dim=1 forces them to compete for 1.0 probability.
                probs = outputs.logits_per_image.softmax(dim=1)
                
                # We extract the 0th index which binds to `expected_content`
                honduras_probs = probs[:, 0].mean().item()
                content_match_score = round(honduras_probs, 4)
                print(f"   Visual Match Score (Comparative Softmax): {content_match_score}")
        
        # CLEANUP
        for f in frames:
            try:
                os.remove(f)
            except:
                pass
        try:
            os.rmdir(frames_dir)
        except:
            pass

        # 6. OUTPUT REDUCTION
        validation_score = (dialect_confidence * 0.5) + (content_match_score * 0.5)
        validation_status = "PASS" if validation_score >= 0.70 else "FAIL"

        output = {
            "video_file": os.path.basename(video_path),
            "transcript": transcript,
            "dialect_check": "pass" if dialect_pass else "fail",
            "dialect_predicted": dialect_prediction,
            "dialect_confidence": dialect_confidence,
            "expected_content": expected_content,
            "content_match_score": content_match_score,
            "validation_score": round(validation_score, 4),
            "validation_status": validation_status
        }
        
        # 7. LOGGING
        report_file = os.path.join(self.reports_dir, "video_validation_results.json")
        
        existing_data = []
        if os.path.exists(report_file):
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                pass
                
        existing_data.append(output)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
            
        calc_time = time.time() - start_time
        self.logger.info(f"Validation completed for {os.path.basename(video_path)} in {calc_time:.2f}s | Status: {validation_status}")
        
        # 8. TELEMETRY LOGGING (Phase 14)
        import csv
        from datetime import datetime
        metrics_file = os.path.join(self.logs_dir, "inference_metrics.csv")
        file_exists = os.path.exists(metrics_file)
        
        with open(metrics_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                # Write CSV header
                writer.writerow([
                    "timestamp", "video_name", "dialect_prediction", "dialect_confidence", 
                    "content_match_score", "validation_score", "validation_status", "processing_time_s", "transcript_length"
                ])
            writer.writerow([
                datetime.now().isoformat(),
                os.path.basename(video_path),
                dialect_prediction,
                round(dialect_confidence, 4),
                content_match_score,
                round(validation_score, 4),
                validation_status,
                round(calc_time, 2),
                len(transcript.split()) if transcript else 0
            ])
            
        print(f"\n✅ Validation complete. Results saved to {report_file}")
        return output



# For quick testing if run directly
if __name__ == "__main__":
    validator = VideoValidator()
    print("Validator initialized and ready.")
