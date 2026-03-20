import streamlit as st
import os
import time
import json
import torch
import tempfile
from PIL import Image
import easyocr

# ML Models
import whisper
from transformers import pipeline, CLIPProcessor, CLIPModel
from video_validator import VideoValidator

# --- Setup & CSS ---
st.set_page_config(page_title="Honduras AI Validation Studio", page_icon="🇭🇳", layout="wide")

st.markdown("""
<style>
    /* Let Streamlit handle the global theme natively */
    .tool-badge { 
        background: linear-gradient(90deg, #4f46e5, #7c3aed); 
        color: white !important;
        padding: 4px 10px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: 600; 
        margin-right: 8px; 
        display: inline-block;
    }
    .metric-card {
        background-color: rgba(150, 150, 150, 0.1);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(150, 150, 150, 0.2);
    }
    .status-pass { color: #10B981; font-weight: bold; font-size: 1.2rem; }
    .status-fail { color: #EF4444; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# --- Model Caching ---
@st.cache_resource(show_spinner=False)
def load_dialect_model():
    base_dir = os.environ.get("BASE_DIR", "/app" if os.path.exists("/app/models") else "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System")
    model_path = os.path.join(base_dir, "models", "honduras_dialect_binary_classifier")
    device = 0 if torch.backends.mps.is_available() else -1
    return pipeline("text-classification", model=model_path, tokenizer=model_path, device=device)

@st.cache_resource(show_spinner=False)
def load_clip_model():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    clip_id = "openai/clip-vit-base-patch32"
    model = CLIPModel.from_pretrained(clip_id).to(device)
    processor = CLIPProcessor.from_pretrained(clip_id)
    return model, processor, device

@st.cache_resource(show_spinner=False)
def load_whisper_model():
    return whisper.load_model("base", device="cpu")

@st.cache_resource(show_spinner=False)
def load_ocr_model():
    return easyocr.Reader(['en', 'es'], gpu=False)

@st.cache_resource(show_spinner=False)
def load_video_validator():
    import sys
    base_dir = os.environ.get("BASE_DIR", "/app" if os.path.exists("/app/models") else "/Volumes/Seagate/AI Content Validation & Dialect Intelligence System")
    if base_dir not in sys.path:
        sys.path.append(base_dir)
    return VideoValidator(device="cpu")

# --- UI Sidebar ---
st.sidebar.title("🇭🇳 Validation Engine")
st.sidebar.markdown("Test marketing assets instantly against the Dialect & Vision layers.")

mode = st.sidebar.radio("Select Analysis Mode:", ["🏠 Home Overview", "📝 Text Validator", "🖼️ Image Validation", "🔊 Audio Transcription", "🎥 Video End-to-End"])

# ----------------- HOME -----------------
if mode == "🏠 Home Overview":
    st.title("🇭🇳 AI Content Validation & Dialect Intelligence System")
    st.markdown("### Interactive ML Studio")
    st.markdown("""
    Welcome to the fully containerized evaluation frontend. This interface allows you to test raw unformatted inputs against the AI infrastructure directly.
    
    **Under the Hood (Toolchain):**
    - <span class='tool-badge'>HuggingFace Transformers</span> Validates linguistic slang boundaries.
    - <span class='tool-badge'>OpenAI CLIP</span> Maps multimodal visual grounding against texts.
    - <span class='tool-badge'>OpenAI Whisper</span> Converts raw audio sequences to Spanish strings.
    - <span class='tool-badge'>FFmpeg</span> Slices MP4 boundaries into discrete visual/audio payloads.
    - <span class='tool-badge'>PyTorch</span> Hardware-accelerated Apple Silicon & CPU matrix computations.
    """, unsafe_allow_html=True)
    
    st.info("👈 Select a mode from the sidebar to begin processing an asset!")

# ----------------- TEXT -----------------
elif mode == "📝 Text Validator":
    st.title("📝 Text Dialect Validation")
    st.markdown("<span class='tool-badge'>Tools: HuggingFace Pipeline -> Honduran Binary Check</span>", unsafe_allow_html=True)
    
    text_input = st.text_area("Enter conversational Spanish text to test dialect:", "Vos sos maje si pensás que salir temprano es fácil.")
    
    if st.button("Validate Text"):
        with st.spinner("Executing NLP Inference..."):
            classifier = load_dialect_model()
            res = classifier(text_input)[0]
            
            prediction = res['label']
            confidence = res['score']
            
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("Inference Result")
            cols = st.columns(2)
            cols[0].metric("Predicted Dialect", prediction)
            cols[1].metric("Model Confidence", f"{confidence*100:.2f}%")
            
            if prediction == "Honduras":
                st.success("✅ Semantic Match: This text aligns with Honduran colloquialisms / dialect patterns.")
            else:
                st.error("❌ Semantic Mismatch: This text appears to be standard Spanish or an alternative regional dialect.")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- IMAGE -----------------
elif mode == "🖼️ Image Validation":
    st.title("🖼️ Image Semantic Validation")
    st.markdown("<span class='tool-badge'>Tools: Pillow (PIL) -> OpenAI CLIP-ViT -> Cosine Similarity</span>", unsafe_allow_html=True)
    
    uploaded_image = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg", "webp"])
    expected_topic = st.text_input("Expected Content / Topic", "Honduras scenery, beautiful people")
    
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
            
            blacklist = ["ecuador", "mexico", "costa rica", "guatemala", "colombia", "peru", "argentina", "chile", "uruguay", "paraguay", "bolivia", "venezuela"]
            ocr_trigger = False
            for b in blacklist:
                if b in text_embedded:
                    st.error(f"🚨 [FAIL - BLACKLIST] OCR intercepted banned term: '{b.upper()}' embedded natively on the image payload!")
                    ocr_trigger = True
                    break
                    
            if ocr_trigger:
                score = 0.0
            else:
                # --- COMPARATIVE SOFTMAX CLIP ---
                st.info("🔍 Running Comparative Zero-Shot CLIP Models...")
                target_list = [expected_topic, "Ecuador scenery or people", "Mexico scenery or people", "Generic unbranded people or background"]
                
                inputs = clip_processor(text=target_list, images=image, return_tensors="pt", padding=True)
                for k, v in inputs.items():
                    if hasattr(v, 'to'): inputs[k] = v.to(device)
                    
                with torch.no_grad():
                    outputs = clip_model(**inputs)
                    
                probs = outputs.logits_per_image.softmax(dim=1)
                score = round(probs[:, 0].mean().item(), 4)
            
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader(f"CLIP Similarity Score: {score}")
            st.progress(score)
            
            if score > 0.5:
                st.success(f"✅ Visuals align sufficiently with the target context: '{expected_topic}' (Detected as explicitly Honduran)")
            else:
                st.error(f"❌ Visuals diverge from the requested marketing target. (Identified as Non-Honduran or explicitly Blacklisted)")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- AUDIO -----------------
elif mode == "🔊 Audio Transcription":
    st.title("🔊 Audio Execution & Dialect Recognition")
    st.markdown("<span class='tool-badge'>Tools: OpenAI Whisper (ASR) -> HuggingFace Transformers</span>", unsafe_allow_html=True)
    
    uploaded_audio = st.file_uploader("Drop Speech/Audio Track", type=["mp3", "wav", "m4a"])
    
    if uploaded_audio:
        st.audio(uploaded_audio)
        if st.button("Process Audio Pipeline"):
            with st.spinner("Loading Whisper & Extracting Transcript..."):
                whisper_model = load_whisper_model()
                classifier = load_dialect_model()
                
                # Write to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(uploaded_audio.read())
                    temp_path = tmp.name
                    
                # 1. Transcribe
                result = whisper_model.transcribe(temp_path, language="es")
                transcript = result["text"].strip()
                os.remove(temp_path)
                
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.subheader("1. Transcription Output (Whisper)")
            st.write(f"> *{transcript if transcript else '[Silence / No Speech Detected]'}*")
            
            if transcript:
                # 2. Re-route to Dialect Check
                with st.spinner("Passing string to Dialect Classifier..."):
                    res = classifier(transcript)[0]
                    prediction = res['label']
                    confidence = res['score']
                    
                st.subheader("2. Dialect Check (HuggingFace)")
                st.metric("Detected Dialect", prediction, f"{confidence*100:.2f}% Confidence")
            else:
                st.error("Pipeline Terminated: Missing spoken word parameters.")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- VIDEO -----------------
elif mode == "🎥 Video End-to-End":
    st.title("🎥 Full E2E Video Validation")
    st.markdown("""
        <span class='tool-badge'>FFmpeg (Audio/Frame Slicing)</span>
        <span class='tool-badge'>OpenAI Whisper</span>
        <span class='tool-badge'>PyTorch CLIP</span>
        <span class='tool-badge'>HuggingFace Dialect Engine</span>
    """, unsafe_allow_html=True)
    
    uploaded_video = st.file_uploader("Upload Marketing MP4 Reel", type=["mp4", "mov"])
    expected_topic_vid = st.text_input("Expected Video Context", "Honduras scenery, beautiful people")
    
    if uploaded_video:
        st.video(uploaded_video)
        
        if st.button("Initialize Master Inference Engine"):
            st.info("⚙️ Routing MP4 to native VideoValidator Class...")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpvid:
                tmpvid.write(uploaded_video.read())
                temp_vid_path = tmpvid.name
                
            validator = load_video_validator()
            
            with st.spinner("Processing FFmpeg, Whisper, and CLIP nodes asynchronously... (May take 30s)"):
                res = validator.validate_video(temp_vid_path, expected_content=expected_topic_vid)
                os.remove(temp_vid_path)
                
            if res:
                st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
                cols = st.columns(2)
                cols[0].metric("Final Validation Score", f"{res['validation_score']:.4f}")
                status_color = "status-pass" if res['validation_status'] == "PASS" else "status-fail"
                cols[1].markdown(f"Status: <span class='{status_color}'>{res['validation_status']}</span>", unsafe_allow_html=True)
                
                st.markdown("### Process Breakdown")
                st.write(f"**🗣️ Audio Layer (Whisper + HF)**:")
                st.write(f"- Transcript: '{res['transcript']}'")
                st.write(f"- Dialect Found: {res['dialect_predicted']} ({res['dialect_check'].upper()})")
                
                st.write(f"**👁️ Vision Layer (CLIP)**:")
                st.write(f"- Context Evaluated: '{expected_topic_vid}'")
                st.write(f"- Semantic Frame Match Score: {res['content_match_score']:.4f}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Pipeline Crashed: Video structurally compromised or codec fault.")
