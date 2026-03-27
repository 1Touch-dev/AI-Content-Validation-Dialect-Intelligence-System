import os
import json
import torch
from faster_whisper import WhisperModel
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
    # Global "Hard Negative" Anchors to pull CLIP softmax away from generic backgrounds
    GLOBAL_ANCHORS = [
        "European city street with historical architecture",
        "North American suburban neighborhood or highway",
        "Asian neon-lit city at night",
        "Modern glass skyscraper office interior",
        "London rainy day with red buses",
        "Generic indoor conference room",
        "African savannah or dry plains",
        "Mediterranean coastal village with white houses"
    ]

    COUNTRY_CONFIG = {
        "honduras": {
            "model_path": "models/honduras_dialect_binary_classifier",
            "label": "Honduras",
            "flag": "🇭🇳",
            "clip_targets": [
                "Honduran identity, flag, or Central American scenery",
                "Andean mountains",
                "Mexican desert",
                "European city"
            ],
            # Advanced Ensemble Prompts
            "visual_anchors": [
                "Honduras national flag with 5 blue stars",
                "Central American tropical landscape with palm trees",
                "Colonial architecture in Comayagua or Tegucigalpa",
                "Honduran football fans in blue and white jerseys",
                "Mayan ruins of Copan in Honduras"
            ],
            "ocr_blacklist": ["ecuador", "mexico", "colombia", "peru", "chile", "argentina", "chelsea", "london"],
            "ocr_positive_keywords": ["Honduras", "Fenafuth", "Catracho", "Tegucigalpa", "San Pedro Sula", "La H"],
            "positive_entities": ["honduras", "tegucigalpa", "san pedro sula", "olimpia", "motagua", "real españa", "marathón", "catracho", "catrachos"],
            "negative_entities": ["ecuador", "quito", "guayaquil", "chelsea", "newcastle", "london", "premier league", "estadio stamford bridge", "arsenal", "liverpool", "manchester"],
            "slang_keywords": ["alero", "pije", "pijín", "macanudo", "cipote", "mara", "bolo", "chele", "cheque", "chamba", "pucha"]
        },
        "ecuador": {
            "model_path": "models/ecuador_dialect_binary_classifier",
            "label": "Ecuador",
            "flag": "🇪🇨",
            "clip_targets": [
                "Ecuadorian identity, flag, or Andean scenery",
                "Central American jungle",
                "North American city",
                "European soccer stadium"
            ],
            # Advanced Ensemble Prompts
            "visual_anchors": [
                "Ecuadorian flag with yellow blue red stripes",
                "Andean mountain landscape with snowy peaks in Ecuador",
                "Colonial architecture in Quito old town",
                "Ecuadorian football fans in bright yellow jerseys",
                "Amazon rainforest landscape in Ecuador",
                "Galapagos islands volcanic scenery"
            ],
            "ocr_blacklist": ["honduras", "mexico", "colombia", "peru", "chile", "argentina", "chelsea", "london"],
            "ocr_positive_keywords": ["Ecuador", "FEF", "Tri", "Quito", "Guayaquil", "Chavez", "La Tri"],
            "positive_entities": ["ecuador", "quito", "guayaquil", "cuenca", "fef", "tricolor", "ldu", "barcelona sc", "emelec", "piero hincapie", "moises caicedo", "valencia"],
            "negative_entities": ["honduras", "tegucigalpa", "san pedro sula", "chelsea", "newcastle", "london", "premier league", "estadio stamford bridge", "arsenal", "liverpool", "manchester"],
            "slang_keywords": ["bacán", "chévere", "ñaño", "caleta", "chuta", "guambra", "mashi", "longo", "pelado", "aniñado", "bestia", "chulla", "cachas", "habla"]
        }
    }

    def __init__(self, country="honduras", device=None):
        self.country = country.lower()
        if self.country not in self.COUNTRY_CONFIG:
            raise ValueError(f"Unsupported country: {country}. Supported: {list(self.COUNTRY_CONFIG.keys())}")
        
        self.config = self.COUNTRY_CONFIG[self.country]
        base_dir = os.environ.get("BASE_DIR", "/app" if os.path.exists("/app/models") else os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(base_dir, self.config["model_path"])
        self.reports_dir = os.path.join(base_dir, "reports")
        
        if device is None:
            self.device = "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Initializing Video Validator for {self.config['label']} {self.config['flag']}. Device: {self.device}")
        
        # 1. Load faster-whisper (large-v3-turbo for accuracy, int8 for CPU speed)
        print("Loading faster-whisper model (large-v3-turbo/int8)...")
        self.whisper_model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
        
        # 2. Load Dialect Classifier
        print(f"Loading {self.config['label']} Dialect Classifier...")
        hf_device = 0 if self.device in ["cuda", "mps"] else -1
        
        # Safety check for model existence (especially on fresh Ecuador setup)
        if not os.path.exists(self.model_path):
            print(f"Warning: Model not found at {self.model_path}. Dialect check will fail until training completes.")
            self.dialect_classifier = None
        else:
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
        self.ocr_reader = easyocr.Reader(['en', 'es'], gpu=False)
        
        os.makedirs(self.reports_dir, exist_ok=True)
        
        import logging
        self.logs_dir = os.environ.get("LOG_DIR", os.path.join(base_dir, "logs"))
        os.makedirs(self.logs_dir, exist_ok=True)
        self.logger = logging.getLogger(f"VideoValidator_{self.country}")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            fh = logging.FileHandler(os.path.join(self.logs_dir, "video_validation.log"))
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(fh)
            
        print("Initialization complete.")

    def extract_audio(self, video_path):
        """Extracts audio from video to a temporary WAV file with loudnorm."""
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        try:
            (
                ffmpeg
                .input(video_path)
                # ac=1 (mono), ar='16k' (Whisper optimal), af='loudnorm' (normalization)
                .output(temp_audio, acodec='pcm_s16le', ac=1, ar='16k', af='loudnorm', loglevel='quiet')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            return temp_audio
        except ffmpeg.Error as e:
            print(f"FFmpeg audio extraction error: {e.stderr.decode()}")
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            return None

    def extract_frames(self, video_path, fps=0.5, max_frames=8):
        """Extracts frames from video, capped at max_frames for CPU performance."""
        temp_dir = tempfile.mkdtemp()
        output_pattern = os.path.join(temp_dir, "frame_%04d.jpg")
        try:
            # Get video duration first so we can sample evenly
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format'].get('duration', 0))
            if duration > 0 and max_frames > 0:
                # Clamp fps so we never extract more than max_frames total
                capped_fps = min(fps, max_frames / duration)
            else:
                capped_fps = fps

            (
                ffmpeg
                .input(video_path)
                .filter('fps', fps=capped_fps)
                .output(output_pattern, loglevel='quiet')
                .run(capture_stdout=True, capture_stderr=True)
            )

            frames = []
            for img_file in sorted(os.listdir(temp_dir)):
                if img_file.endswith(".jpg"):
                    frames.append(os.path.join(temp_dir, img_file))
            # Safety cap — never process more than max_frames
            frames = frames[:max_frames]
            print(f"   Sampled {len(frames)} frames (duration={duration:.1f}s, fps={capped_fps:.3f})")
            return frames, temp_dir
        except ffmpeg.Error as e:
            print(f"FFmpeg frame extraction error: {e.stderr.decode()}")
            return [], temp_dir

    def context_check(self, text, ocr_texts):
        """Geographic & Dialectic Sanitizer (Localism Grounding)"""
        text_lower = text.lower()
        ocr_combined = " ".join(ocr_texts).lower()
        full_context = f"{text_lower} {ocr_combined}"
        
        pos_found = [e for e in self.config.get('positive_entities', []) if e.lower() in full_context]
        neg_found = [e for e in self.config.get('negative_entities', []) if e.lower() in full_context]
        slang_found = [s for s in self.config.get('slang_keywords', []) if s.lower() in text_lower]
        
        # A text is "Neutral" if it's long but has NO local entities AND NO local slang
        is_neutral = len(text.split()) > 25 and len(pos_found) == 0 and len(slang_found) == 0
        
        return {
            "positive_count": len(pos_found),
            "negative_count": len(neg_found),
            "slang_count": len(slang_found),
            "positive_list": pos_found,
            "negative_list": neg_found,
            "slang_list": slang_found,
            "is_neutral_spanish": is_neutral,
            "has_context_mismatch": len(neg_found) > 0
        }

    def validate_text(self, text):
        """Standalone text validation engine (Dialect + Slang + Neutrality)"""
        if not text or not self.dialect_classifier:
            return {
                "prediction": "Other",
                "confidence": 0.0,
                "pass": False,
                "slang_found": [],
                "entities_found": [],
                "is_neutral": True
            }
            
        # 1. Primary HF Classification
        res = self.dialect_classifier(text)[0]
        prediction = res['label']
        confidence = round(res['score'], 4)
        dialect_pass = (prediction == self.config['label'])
        
        # 2. Localism / Neutrality Check
        context = self.context_check(text, []) # No OCR for text-only
        
        # 3. Override Label if text is Neutral Span (missing localisms)
        final_prediction = prediction
        final_pass = dialect_pass
        final_confidence = confidence
        
        # We only override if the AI model is NOT extremely confident.
        # This prevents over-penalizing valid localisms that aren't in our dictionary yet.
        is_high_confidence = confidence > 0.92
        
        if dialect_pass and context['is_neutral_spanish'] and not is_high_confidence:
            final_pass = False
            final_prediction = "Neutral/International Spanish"
            final_confidence = min(confidence, 0.20)
        elif not dialect_pass and context['is_neutral_spanish']:
            # Harmonize label for non-passing neutral text (e.g. Other -> Neutral)
            final_prediction = "Neutral/International Spanish"
            
        return {
            "prediction": final_prediction,
            "confidence": final_confidence,
            "pass": final_pass,
            "slang_found": context['slang_list'],
            "entities_found": context['positive_list'],
            "is_neutral": context['is_neutral_spanish']
        }

    def validate_scene(self, image, clip_model, clip_processor, device):
        """Advanced Visual Grounding using an ensemble of anchors."""
        target_anchors = self.config.get('visual_anchors', ["Ecuadorian scenery"])
        negative_anchors = self.GLOBAL_ANCHORS
        
        # Combine all prompts for a single softmax pass
        all_prompts = target_anchors + negative_anchors
        
        inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
        for k in inputs:
            v = inputs[k]
            if hasattr(v, 'to'):
                inputs[k] = v.to(device)
            
        with torch.no_grad():
            outputs = clip_model(**inputs)
            
        probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy()[0]
        
        # Aggregate positive and negative scores
        pos_total = sum(probs[:len(target_anchors)])
        neg_total = sum(probs[len(target_anchors):])
        
        # Find Top Context
        top_idx = probs.argmax()
        top_label = all_prompts[top_idx]
        top_prob = float(probs[top_idx])
        
        return {
            "visual_score": float(pos_total),
            "top_context": top_label,
            "top_confidence": top_prob,
            "is_generic": neg_total > pos_total
        }

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
        
        # STEP 2: SPEECH TRANSCRIPTION (auto language detection)
        print("2. Transcribing audio (faster-whisper large-v3-turbo, auto-detect)...")
        transcript = ""
        detected_language = ""
        language_probability = 0.0
        if audio_path:
            # Auto-detect language — do NOT force 'es' to avoid hallucination
            # no_speech_threshold=0.8: background music raises no_speech_prob above default 0.6
            segments, info = self.whisper_model.transcribe(
                audio_path, 
                beam_size=5,
                vad_filter=False,
                no_speech_threshold=0.8
            )
            
            detected_language = info.language
            language_probability = info.language_probability
            print(f"   Detected language: {detected_language} ({language_probability:.1%})")
            
            transcript_parts = []
            for segment in segments:
                transcript_parts.append(segment.text)
                if len(transcript_parts) % 5 == 0:
                    print(f"   ...transcribed {len(transcript_parts)} segments")
                    
            transcript = " ".join(transcript_parts).strip()
            os.remove(audio_path) # cleanup
            print(f"   Final Transcript: '{transcript[:150]}...'" if len(transcript) > 150 else f"   Final Transcript: '{transcript}'")
        else:
            print("   Warning: Could not extract audio.")
            
        # STEP 3: DIALECT VALIDATION (only if Spanish detected)
        print(f"3. Validating {self.config['label']} dialect...")
        dialect_results = {
            "prediction": "Other",
            "confidence": 0.0,
            "pass": False
        }
        
        is_spanish = detected_language == "es"
        
        if transcript and is_spanish:
            dialect_results = self.validate_text(transcript)
            print(f"   Result: {dialect_results['prediction']} ({dialect_results['confidence']*100:.1f}%)")
        elif transcript and not is_spanish:
            print(f"   Audio is in '{detected_language}' (not Spanish). Skipping dialect classifier.")
            dialect_results["prediction"] = f"Non-Spanish ({detected_language})"
        else:
            print("   Warning: No transcript to validate.")


        # STEP 4: FRAME EXTRACTION
        print("4. Extracting frames...")
        frames, frames_dir = self.extract_frames(video_path)
        print(f"   Extracted {len(frames)} frames for analysis.")

        # STEP 5: VISION & OCR ANALYSIS
        print(f"5. Analyzing visual content against: '{expected_content}'...")
        content_match_score = 0.0
        ocr_blacklist_triggered = False
        ocr_positive_match = False
        blacklist = self.config["ocr_blacklist"]
        positive_keywords = self.config.get("ocr_positive_keywords", [])
        
        if frames:
            images = [Image.open(f).convert("RGB") for f in frames]
            
            # --- OCR CHECK ---
            print("   Running strict OCR evaluations on extracted frames...")
            found_positive_terms = []
            ocr_all_text = []
            for img_path in frames:
                if ocr_blacklist_triggered:
                    break
                results = self.ocr_reader.readtext(img_path, detail=0)
                text = " ".join(results).lower()
                ocr_all_text.append(text)
                
                # Blacklist check
                for b in blacklist:
                    if b in text:
                        print(f"   [FAIL - BLACKLIST] OCR intercepted term: '{b.upper()}' embedded in media frame!")
                        ocr_blacklist_triggered = True
                        break
                
                # Positive Keyword check (reinforcement)
                for p in positive_keywords:
                    if p.lower() in text:
                        if p not in found_positive_terms:
                            found_positive_terms.append(p)
                            ocr_positive_match = True
            
            if found_positive_terms:
                print(f"   [PASS - OCR] Detected positive markers: {found_positive_terms}")

            if ocr_blacklist_triggered:
                content_match_score = 0.0 # Force failing validation
                print("   Visual Match Score forced to 0.0 due to structural OCR anomaly.")
            else:
                # --- COMPARATIVE CLIP Softmax Algorithm ---
                # Enhanced prompts to penalize international venues
                # STEP 5: VISUAL VALIDATION (CLIP)
                print(f"5. Analyzing visual content against: '{expected_content}' (Ensemble)...")
                clip_scores = []
                top_contexts = {}
                
                # Assuming 'images' are the sampled frames from the video
                # and 'clip_model', 'clip_processor', 'device' are available in this scope
                # (These would typically be passed as arguments or accessed from self)
                # For this refactor, we'll assume 'images' is the list of sampled frames.
                # If 'images' is not the sampled frames, you might need to adjust 'sampled_frames' variable.
                
                for i, img in enumerate(images):
                    visual_results = self.validate_scene(img, self.clip_model, self.clip_processor, self.device)
                    clip_scores.append(visual_results['visual_score'])
                    
                    ctx = visual_results['top_context']
                    top_contexts[ctx] = top_contexts.get(ctx, 0) + 1
                    
                content_match_score = sum(clip_scores) / len(clip_scores) if clip_scores else 0.0
                
                # Frequency analysis of top visual contexts
                most_common_context = max(top_contexts.items(), key=lambda x: float(x[1]))[0] if top_contexts else "Unknown"
                print(f"   Visual Match Score (Ensemble Softmax): {content_match_score:.4f}")
                print(f"   Dominant Visual Context: {most_common_context}")
                
                # OCR Boost: If positive keywords are found, provide a 20% floor boost to vision score
                if ocr_positive_match:
                    content_match_score = min(1.0, content_match_score + 0.20)
                    print(f"   Visual Match Score (CLIP + OCR Boost): {content_match_score}")
                else:
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

        # STEP 5.5: GEOGRAPHIC CONTEXT CHECK
        print("5.5 Running Geographic Context Verification...")
        ocr_combined = ocr_all_text if 'ocr_all_text' in locals() else []
        context_report = self.context_check(transcript, ocr_combined)
        
        dialect_prediction = dialect_results['prediction']
        dialect_confidence = dialect_results['confidence']
        dialect_pass = dialect_results['pass']

        context_multiplier = 1.0
        if context_report['has_context_mismatch']:
            print(f"   ⚠️ CONTEXT MISMATCH! Detected incompatible entities: {context_report['negative_list']}")
            context_multiplier = 0.5 # Severe penalty
        elif context_report['positive_count'] > 0 or context_report['slang_count'] > 0:
            print(f"   ✅ Local context confirmed: {context_report['positive_list'] + context_report['slang_list']}")
            context_multiplier = 1.1 # Small boost
        else:
            print("   ℹ️ Neutral context (no specific geographic entities found)")

        # 6. OUTPUT REDUCTION (Hierarchical Scoring Logic)
        is_mute = not bool(transcript)
        
        if is_mute:
            print("   Mute/Silence detected: Validation weighting shifted 100% to Vision Layer.")
            # Still apply context penalty even if mute
            validation_score = float(content_match_score) * context_multiplier
            dialect_confidence = 0.0
        else:
            # Standard 50/50 balance
            base_score = (float(dialect_confidence) * 0.5) + (float(content_match_score) * 0.5)
            validation_score = float(base_score) * context_multiplier
            
            # Hierarchical Pass: If dialect class is extremely confident AND OCR matches,
            # we allow a lower CLIP vision score to PASS (prevents false negatives for generic backgrounds)
            # ONLY IF there is no context mismatch and NOT neutral international Spanish.
            if dialect_pass and float(dialect_confidence) > 0.95 and ocr_positive_match and not context_report['has_context_mismatch']:
                if float(validation_score) < 0.65:
                    print(f"   Hierarchical Pass triggered: High dialect confidence ({dialect_confidence}) + OCR match. Adjusting score.")
                    validation_score = max(float(validation_score), 0.65) # Floor at 0.65 for hierarchical pass

        # Adjusted Threshold: 0.60 for a PASS
        validation_status = "PASS" if validation_score >= 0.60 else "FAIL"

        output = {
            "video_file": os.path.basename(video_path),
            "transcript": transcript,
            "detected_language": detected_language,
            "mute_detected": is_mute,
            "dialect_check": "pass" if dialect_pass else "fail",
            "dialect_predicted": str(dialect_prediction),
            "dialect_confidence": float(dialect_confidence),
            "expected_content": expected_content,
            "content_match_score": float(content_match_score),
            "ocr_positive_match": bool(ocr_positive_match),
            "detected_entities": context_report['positive_list'] + context_report['slang_list'] if not context_report['has_context_mismatch'] else context_report['negative_list'],
            "validation_score": round(float(validation_score), 4),
            "validation_status": str(validation_status)
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
                round(float(dialect_confidence), 4),
                float(content_match_score),
                round(float(validation_score), 4),
                validation_status,
                round(float(calc_time), 2),
                len(transcript.split()) if transcript else 0
            ])
            
        print(f"\n✅ Validation complete. Results saved to {report_file}")
        return output



# For quick testing if run directly
if __name__ == "__main__":
    validator = VideoValidator()
    print("Validator initialized and ready.")
