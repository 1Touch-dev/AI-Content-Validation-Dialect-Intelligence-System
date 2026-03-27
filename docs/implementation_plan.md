# Geographic Guardrails & RAG Grounding (Phase 30)

The system currently produces false positives on neutral international Spanish (e.g., Premier League Commentary) because the dialect model confuses "Formal Neutral Spanish" with "Formal Ecuadorian Spanish". CLIP also gives high scores for green grass and crowds in stadiums.

## Proposed Fix: Contextual Grounding Layer

We will implement a **Geographic Sanitizer** that acts as a "RAG-lite" guardrail, verifying if the entities mentioned in the video actually belong to the target country.

### 1. Enhanced `COUNTRY_CONFIG`
We will add `positive_entities` and `negative_entities` to the configuration for each country.

- **Ecuador 🇪🇨**:
  - `positive`: LDU, Barcelona SC, Emelec, Quito, Guayaquil, FEF, Tricolor.
  - `negative`: Chelsea, Newcastle, Premier League, London, Europe, Honduras, Tegucigalpa.
- **Honduras 🇭🇳**:
  - `positive`: Olimpia, Motagua, Tegucigalpa, San Pedro Sula, Catracho, H.
  - `negative`: Ecuador, Quito, Guayaquil, Chelsea, Premier League.

### 2. Logic Updates (`video_validator.py`)
- **Keyword Scan**: Extract all nouns/entities from the transcript and OCR.
- **Context Score**: 
  - If `negative_entities` are found (e.g., "Chelsea", "Stamford Bridge"), we apply a **severe penalty** (-0.4) to the final score.
  - If `positive_entities` are found, we provide a boost.
- **Strict Neutrality Check**: If the transcript is >50 words but contains ZERO localisms (slang) AND ZERO `positive_entities`, we will reduce the Dialect Confidence by 50%. This forces formal/neutral international news to FAIL.

### Visual Scene Grounding [Phase 31]
Improve accuracy for images/stills that contain NO text by using "Comparative Anchor Ensembles".

#### [MODIFY] [app.py](file:///Volumes/Seagate/AI%20Content%20Validation%20&%20Dialect%20Intelligence%20System/app.py)
- Refactor `Image Validation` mode to use `validate_image_scene`.
- Implement a "Decision Forest" of 10+ CLIP prompts (Regional vs. Global Hard Negatives).
- Add "Top 3 Visual Contexts" display to the UI for explainability.

#### [MODIFY] [video_validator.py](file:///Volumes/Seagate/AI%20Content%20Validation%20&%20Dialect%20Intelligence%20System/video_validator.py)
- Update `VideoValidator` to use the same ensemble strategy for frame extraction, improving visual score reliability.
- Standardize all toolchain labels to **"Faster-Whisper (large-v3-turbo)"**.
- Add a new "Context Grounding" status indicator in the process breakdown.

## Verification Plan

### Negative Test (Chelsea Video)
- Re-run the Chelsea vs Newcastle video.
- **Expected Result**: **FAIL**. The system should detect "Chelsea" / "Premier League" as negative entities and trigger a Context Mismatch penalty.

### Positive Test (Ecuador Reel)
- Re-run an authentic Ecuadorian reel.
- **Expected Result**: **PASS**. The system should confirm local entities or slang.
- **Phase 31 (Visual Scene Grounding)**: Hardening image-only validation for scenery without text.
- **Phase 32 (Performance & Memory)**: Optimization for concurrent users.
