# 🇭🇳 AI Content Validation & Dialect Intelligence System

A state-of-the-art Multi-Modal Artificial Intelligence platform engineered explicitly to validate and filter geographical marketing assets. The system ensures that all processed Text, Images, Audio, and Video files authentically align with Honduran linguistic dialects and visual aesthetics, utilizing comparative zero-shot modeling.

---

## 🧠 Core Architecture & Toolchain

The validation infrastructure heavily relies on synchronized neural networks running natively on PyTorch (optimized for CPU/MPS stability).

1. **HuggingFace Transformers (NLP & Dialect)**
   - **Role**: Validates written strings and spoken transcriptions against a custom-trained Binary Dialect Classifier.
   - **Function**: Recognizes authentic Honduran colloquialisms (slang, sentence structures) vs standard/other Spanish dialects.

2. **OpenAI CLIP-ViT (Comparative Vision Analysis)**
   - **Role**: Extracts visual frames and matrices, mapping them against comparative text prompts.
   - **Function**: Utilizes a strict "Comparative Softmax" approach (e.g., `["Honduras", "Ecuador", "Mexico"]`) mathematically forcing geographical separation rather than standard loose cosine similarity overlaps.

3. **OpenAI Whisper (Automatic Speech Recognition)**
   - **Role**: Transcribes complex MP4 audio tracks and `.wav` files into pure Spanish text.
   - **Function**: Ignores background music and explicitly isolates spoken human dialogue for the Dialect Engine.

4. **EasyOCR (Strict Optical Fallback)**
   - **Role**: Reads structural text overlaid natively on Images and Video Frames.
   - **Function**: Hard-codes explicit blacklists (`["ecuador", "mexico", "costa rica"]`). If these are detected visually, the model completely aborts and executes a `FAIL` override.

5. **FFmpeg (Media Slicing)**
   - **Role**: Operates natively in the background splitting `.mp4` payloads into distinct `.wav` tracks and `.jpg` sampling frames.
   
6. **Docker & FastAPI / Streamlit**
   - **Role**: Containerizes the application into an interactive UI and arbitrary RestAPIs.

---

## 🚀 Execution & Deployment Commands

### 1. The Interactive Dashboard (Streamlit)
The premium UI provides a 4-mode playground explicitly visualizing the inference engines (supports massive Gigabit file structures via socket bypasses).

```bash
# 1. Activate your environment
source venv/bin/activate

# 2. Launch the UI App
streamlit run app.py
```
*Note: The Streamlit engine is configured in `.streamlit/config.toml` to safely accept >1GB files.*

### 2. The Headless API (FastAPI)
To run the background server explicitly for programmatic endpoint requests instead of the UI:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```
*Endpoint Example: Send a generic `POST` request to `/validate-video` containing your MP4 payload.*

### 3. Native Python Pipeline Execution
You can bypass the APIs entirely and process massive dataset folders using the core class bindings:

```python
# Create a test script using the native VideoValidator
from video_validator import VideoValidator

validator = VideoValidator(device="cpu")
result = validator.validate_video("path_to_video.mp4", expected_content="Honduras scenery, beautiful people")
print(result)
```

### 4. Docker E2E Containerization
To deploy the entire environment (OS dependencies, FFmpeg, PyTorch, Whisper, Models) gracefully onto a production EC2/Ubuntu cloud wrapper:

```bash
# Build and orchestrate both the API Server and Streamlit Dashboard simultaneously
docker-compose up --build
```

---

## 📂 Project Structure Map

```plaintext
AI Content Validation & Dialect Intelligence System/
│
├── app.py                      # Interactive Streamlit Frontend (GUI)
├── video_validator.py          # Core Engine orchestrating CLIP, OCR, Whisper, FFmpeg calls natively
├── docker-compose.yml          # Production Container orchestrator
├── Dockerfile                  # Base Python 3.12-Slim architecture
├── .streamlit/                 # UI configurations (Global 1GB upload bypass limits)
│
├── models/
│   └── honduras_dialect_...    # Fine-Tuned HuggingFace NLP Model weights
│
├── datasets/                   # Test assets / Synthetic strings
├── logs/                       # Automated persistent run logs
└── reports/                    # Human-readable markdown test reports
```

---
*Architected strictly to combat geographical hallucination and marketing overlap.*
