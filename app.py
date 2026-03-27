import streamlit as st
import os
import time
import json
import torch
import tempfile
from PIL import Image
import easyocr

# ML Models
from faster_whisper import WhisperModel
from transformers import pipeline, CLIPProcessor, CLIPModel
from video_validator import VideoValidator

# --- Setup & CSS ---
st.set_page_config(page_title="AI Validation Studio", page_icon="🌍", layout="wide")

# --- UI Sidebar & Country Selection ---
st.sidebar.title("🌍 Validation Engine")
st.sidebar.markdown("Test marketing assets instantly against the Dialect & Vision layers.")

selected_country_name = st.sidebar.selectbox("Select Target Country:", ["Honduras 🇭🇳", "Ecuador 🇪🇨"])
country_map = {"Honduras 🇭🇳": "honduras", "Ecuador 🇪🇨": "ecuador"}
selected_country = country_map[selected_country_name]
country_flag = "🇭🇳" if selected_country == "honduras" else "🇪🇨"
country_name = "Honduras" if selected_country == "honduras" else "Ecuador"

st.markdown(f"""
<style>
    /* Let Streamlit handle the global theme natively */
    .tool-badge {{ 
        background: linear-gradient(90deg, #4f46e5, #7c3aed); 
        color: white !important;
        padding: 4px 10px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: 600; 
        margin-right: 8px; 
        display: inline-block;
    }}
    .metric-card {{
        background-color: rgba(150, 150, 150, 0.1);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(150, 150, 150, 0.2);
    }}
    .status-pass {{ color: #10B981; font-weight: bold; font-size: 1.2rem; }}
    .status-fail {{ color: #EF4444; font-weight: bold; font-size: 1.2rem; }}
</style>
""", unsafe_allow_html=True)

# --- Model Caching ---
# Environment Configuration
# Use dynamic path detection to support both local and EC2
current_dir = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BASE_DIR = os.environ.get("BASE_DIR", current_dir)

@st.cache_resource(show_spinner=False)
def load_dialect_model(country):
    model_folder = "honduras_dialect_binary_classifier" if country == "honduras" else "ecuador_dialect_binary_classifier"
    model_path = os.path.join(DEFAULT_BASE_DIR, "models", model_folder)
    
    if not os.path.exists(model_path):
        return None
        
    device = 0 if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else -1
    return pipeline("text-classification", model=model_path, tokenizer=model_path, device=device)

@st.cache_resource(show_spinner=False)
def load_clip_model():
    device = "mps" if hasattr(torch.backends, "mps") and torch.backends.mps.is_available() else "cpu"
    clip_id = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(clip_id).to(device)
    processor = CLIPProcessor.from_pretrained(clip_id)
    return model, processor, device

@st.cache_resource(show_spinner=False)
def load_whisper_model():
    return WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")

@st.cache_resource(show_spinner=False)
def load_ocr_model():
    return easyocr.Reader(['en', 'es'], gpu=False)

@st.cache_resource(show_spinner=False)
def load_video_validator(country):
    import sys
    base_dir = os.environ.get("BASE_DIR", "/app" if os.path.exists("/app/models") else "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System")
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    return VideoValidator(country=country, device="cpu")

mode = st.sidebar.radio("Select Analysis Mode:", ["🏠 Home Overview", "📝 Text Validator", "🖼️ Image Validation", "🔊 Audio Transcription", "🎥 Video End-to-End"])

# ----------------- HOME -----------------
if mode == "🏠 Home Overview":
    st.title(f"{country_flag} {country_name} AI Validation & Dialect System")
    st.markdown("### Interactive ML Studio")
    st.markdown("""
    Welcome to the fully containerized evaluation frontend. This interface allows you to test raw unformatted inputs against the AI infrastructure directly.
    
    **Under the Hood (Toolchain):**
    - <span class='tool-badge'>HuggingFace Transformers</span> Validates linguistic slang boundaries.
    - <span class='tool-badge'>OpenAI CLIP</span> Maps multimodal visual grounding against texts.
    - <span class='tool-badge'>Faster-Whisper (large-v3-turbo)</span> State-of-the-art multilingual ASR with auto language detection.
    - <span class='tool-badge'>FFmpeg</span> Slices MP4 boundaries into discrete visual/audio payloads.
    - <span class='tool-badge'>PyTorch</span> Hardware-accelerated Apple Silicon & CPU matrix computations.
    """, unsafe_allow_html=True)
    
    st.info("👈 Select a mode from the sidebar to begin processing an asset!")

# ----------------- TEXT -----------------
elif mode == "📝 Text Validator":
    st.title("📝 Text Dialect Validation")
    st.markdown(f"<span class='tool-badge'>Tools: HuggingFace Pipeline -> {country_name} Binary Check</span>", unsafe_allow_html=True)
    
    default_text = "Vos sos maje si pensás que salir temprano es fácil." if selected_country == "honduras" else "Habla ñaño, qué tal todo por Guayaquil?"
    text_to_validate = st.text_area("Enter conversational Spanish text to test dialect:", default_text)
    
    if text_to_validate:
        if st.button("Validate Dialect Integrity"):
            with st.spinner("Analyzing Linguistic Patterns..."):
                validator = load_video_validator(selected_country)
                results = validator.validate_text(text_to_validate)
                
                prediction = results['prediction']
                confidence = results['confidence']
                
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("Analysis Results")
            st.metric("Detected Dialect", prediction, f"{confidence*100:.2f}% Confidence")
            
            if results.get('slang_found') or results.get('entities_found'):
                st.success(f"✅ **Localisms Detected:** {results['slang_found'] + results['entities_found']}")
            elif results.get('is_neutral'):
                st.warning("ℹ️ **Neutral Spanish Alert:** This text appears generic/international. No specific regional markers detected.")
            
            if results['pass']:
                st.success(f"✅ Text aligns with {country_name} dialect standards.")
            else:
                st.error(f"❌ Text does not meet {country_name} dialect requirements (Too generic or incorrect region).")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- IMAGE -----------------
elif mode == "🖼️ Image Validation":
    st.title("🖼️ Image Semantic Validation")
    st.markdown("<span class='tool-badge'>Tools: Pillow (PIL) -> OpenAI CLIP-ViT -> Cosine Similarity</span>", unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg", "webp"])
    default_topic = f"{country_name} scenery, beautiful people"
    expected_topic = st.text_input("Expected Content / Topic", default_topic)
    
    if uploaded_image and st.button("Validate Image"):
        image = Image.open(uploaded_image).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        with st.spinner("Extracting Multi-modal Vector Embeddings & OCR Arrays..."):
            clip_model, clip_processor, device = load_clip_model()
            ocr_reader = load_ocr_model()
            
            # --- OCR CHECK ---
            st.info("🔍 Running OCR Text Sweep...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmpimg:
                image.save(tmpimg, format="JPEG")
                img_path = tmpimg.name
            
            ocr_results = ocr_reader.readtext(img_path, detail=0)
            text_embedded = " ".join(ocr_results).lower()
            os.remove(img_path)
            
            blacklist_map = {
                "honduras": ["ecuador", "mexico", "costa rica", "guatemala", "colombia", "peru"],
                "ecuador": ["honduras", "mexico", "colombia", "peru", "chile", "argentina"]
            }
            blacklist = blacklist_map[selected_country]
            ocr_trigger = False
            for b in blacklist:
                if b in text_embedded:
                    st.error(f"🚨 [FAIL - BLACKLIST] OCR intercepted banned term: '{b.upper()}' embedded natively on the image payload!")
                    ocr_trigger = True
                    break
                    
            if ocr_trigger:
                score = 0.0
            else:
                # --- ADVANCED ENSEMBLE CLIP ---
                st.info("🔍 Running Advanced Visual Scene Grounding (Ensemble)...")
                validator = load_video_validator(selected_country)
                
                scene_results = validator.validate_scene(image, clip_model, clip_processor, device)
                score = scene_results['visual_score']
                
                # Show top detected contexts for explainability
                # Aligning with contrastive pool to differentiate national markers
                other_country_anchors = []
                for c_code, c_data in validator.COUNTRY_CONFIG.items():
                    if c_code != selected_country:
                        other_country_anchors.extend(c_data.get('visual_anchors', []))
                
                all_prompts = validator.config.get('visual_anchors', []) + validator.GLOBAL_ANCHORS + other_country_anchors
                inputs = clip_processor(text=all_prompts, images=image, return_tensors="pt", padding=True)
                for k, v in inputs.items():
                    if hasattr(v, 'to'): inputs[k] = v.to(device)
                with torch.no_grad():
                    outputs = clip_model(**inputs)
                probs = outputs.logits_per_image.softmax(dim=1).cpu().numpy()[0]
                
                # Get Top 3
                top_3_indices = probs.argsort()[-3:][::-1]
                st.write("**Top 3 Detected Visual Contexts:**")
                for idx in top_3_indices:
                    label = all_prompts[idx]
                    prob = probs[idx]
                    
                    # Highlight if it's an explicit mismatch from another country
                    mismatch_warning = ""
                    if label in other_country_anchors:
                        mismatch_warning = " ⚠️ (CROSS-COUNTRY MISMATCH)"
                    
                    st.write(f"- {label}: **{prob*100:.1f}%** {mismatch_warning}")
            
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader(f"CLIP Similarity Score: {score}")
            st.progress(score)
            
            if score > 0.5:
                st.success(f"✅ Visuals align sufficiently with the target context: '{expected_topic}' (Detected as explicitly {country_name})")
            else:
                st.error(f"❌ Visuals diverge from the requested marketing target. (Identified as Non-{country_name} or explicitly Blacklisted)")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- AUDIO -----------------
elif mode == "🔊 Audio Transcription":
    st.title("🔊 Audio Execution & Dialect Recognition")
    st.markdown("<span class='tool-badge'>Tools: Faster-Whisper (large-v3-turbo) -> HuggingFace Transformers</span>", unsafe_allow_html=True)
    
    uploaded_audio = st.file_uploader("Drop Speech/Audio Track", type=["mp3", "wav", "m4a"])
    
    if uploaded_audio:
        st.audio(uploaded_audio)
        if st.button("Process Audio Pipeline"):
            with st.spinner("Loading Whisper & Extracting Transcript..."):
                whisper_model = load_whisper_model()
                classifier = load_dialect_model(selected_country)
                
                if classifier is None:
                    st.error(f"Error: Dialect model for {country_name} not found. Please run training first.")
                    st.stop()
                
                # Write to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(uploaded_audio.read())
                    temp_path = tmp.name
                    
                # 1. Transcribe (faster-whisper large-v3-turbo, auto-detect language)
                segments, info = whisper_model.transcribe(temp_path, beam_size=5, vad_filter=False, no_speech_threshold=0.8)
                transcript = " ".join([segment.text for segment in segments]).strip()
                detected_lang = info.language
                os.remove(temp_path)
                
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("1. Transcription Output (Whisper)")
            st.write(f"> *{transcript if transcript else '[Silence / No Speech Detected]'}*")
            
            if transcript:
                # 2. Re-route to Refined Dialect Check
                with st.spinner("Analyzing Dialect & Localisms..."):
                    validator = load_video_validator(selected_country)
                    text_results = validator.validate_text(transcript)
                    
                    prediction = text_results['prediction']
                    confidence = text_results['confidence']
                    
                st.subheader("2. Dialect Check (HuggingFace + Localisms)")
                st.metric("Detected Dialect", prediction, f"{confidence*100:.2f}% Confidence")
                
                if text_results.get('slang_found') or text_results.get('entities_found'):
                    st.success(f"✅ **Localisms Detected:** {text_results['slang_found'] + text_results['entities_found']}")
                elif text_results.get('is_neutral'):
                    st.warning("ℹ️ **Neutral Spanish Alert:** No country-specific slang or entities detected in this recording.")
            else:
                st.error("Pipeline Terminated: Missing spoken word parameters.")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- VIDEO -----------------
elif mode == "🎥 Video End-to-End":
    st.title("🎥 Full E2E Video Validation")
    st.markdown("""
        <span class='tool-badge'>FFmpeg (Audio/Frame Slicing)</span>
        <span class='tool-badge'>Faster-Whisper (large-v3-turbo)</span>
        <span class='tool-badge'>PyTorch CLIP</span>
        <span class='tool-badge'>HuggingFace Dialect Engine</span>
    """, unsafe_allow_html=True)
    
    uploaded_video = st.file_uploader("Upload Marketing MP4 Reel", type=["mp4", "mov"])
    default_video_topic = f"{country_name} scenery, beautiful people"
    expected_topic_vid = st.text_input("Expected Video Context", default_video_topic)
    
    if uploaded_video:
        st.video(uploaded_video)
        
        if st.button("Initialize Master Inference Engine"):
            st.info("⚙️ Routing MP4 to native VideoValidator Class...")

            # Write in 8MB chunks to avoid loading entire file into RAM
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpvid:
                chunk_size = 8 * 1024 * 1024  # 8MB
                uploaded_video.seek(0)
                while True:
                    chunk = uploaded_video.read(chunk_size)
                    if not chunk:
                        break
                    tmpvid.write(chunk)
                temp_vid_path = tmpvid.name

            validator = load_video_validator(selected_country)

            with st.spinner("Processing FFmpeg, Whisper, and CLIP nodes (sampling 8 frames max)... Large videos take ~60-90s on CPU."):
                res = validator.validate_video(temp_vid_path, expected_content=expected_topic_vid)
                os.remove(temp_vid_path)
                
            if res:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                cols = st.columns(2)
                cols[0].metric("Final Validation Score", f"{res['validation_score']:.4f}")
                status_color = "status-pass" if res['validation_status'] == "PASS" else "status-fail"
                cols[1].markdown(f"Status: <span class='{status_color}'>{res['validation_status']}</span>", unsafe_allow_html=True)
                
                st.markdown("### Process Breakdown")
                st.write(f"**🗣️ Audio Layer (large-v3-turbo + HF)**:")
                if res.get('mute_detected'):
                    st.warning("🔇 Mute or Silence detected. Validation shifted 100% to Vision/OCR.")
                else:
                    lang_info = f" [Detected: {res.get('detected_language', '?')}]" if res.get('detected_language') else ""
                    st.write(f"- Transcript: '{res['transcript']}'{lang_info}")
                    st.write(f"- Dialect Found: {res['dialect_predicted']} ({res['dialect_check'].upper()})")
                
                st.write(f"**👁️ Vision Layer (CLIP + OCR)**:")
                st.write(f"- Context Evaluated: '{expected_topic_vid}'")
                st.write(f"- Semantic Match: {res['content_match_score']:.4f}")
                if res.get('ocr_positive_match'):
                    st.success("✅ Positive local markers (OCR) detected in media frames.")

                st.write(f"**🌍 Geographic & Localism Verification**:")
                if not res.get('geographic_verification'):
                    st.error(f"⚠️ **Geographic Mismatch!** Detected international entities: {res.get('detected_entities', [])}")
                    st.info("Validation fail: Video content belongs to a different geographic region (e.g., European sports).")
                elif res.get('detected_entities'):
                    st.success(f"✅ **Localism Verified.** Detected local entities/slang: {res.get('detected_entities')}")
                else:
                    st.info("ℹ️ Neutral context. No specific local markers or international mismatches detected.")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Pipeline Crashed: Video structurally compromised or codec fault.")
