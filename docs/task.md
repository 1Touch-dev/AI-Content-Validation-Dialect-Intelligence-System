# Task: AI Dialect Dataset Pipeline Implementation

## Phase 1: Environment & Structure
- [x] Initialize project directory structure `[x]`
    - [x] Create `scraper/`, `processing/`, `storage/` directories `[x]`
    - [x] Create subdirectories in `storage/` (`raw_data/`, `cleaned_data/`, `labeled_data/`) `[x]`
- [x] Setup environment `[x]`
    - [x] Create `requirements.txt` `[x]`
    - [x] Initialize virtual environment `[x]`
    - [x] Verify `.env` contains `APIFY_API_KEY` `[x]`

## Phase 2: Data Collection (Scrapers)
- [x] Scale up data collection (2000+ records per source) `[x]`
    - [x] Scrape Twitter (2000 tweets) `[x]`
    - [x] Scrape Reddit (2000 posts target - 1700+ acquired) `[x]`
    - [x] Scrape Google Reviews (restaurants in HN cities) `[x]`
- [x] Implement dataset merging logic (in `scraper/` or `main_pipeline.py`) `[x]`

## Phase 3: Data Processing
- [x] Implement cleaning logic (`processing/cleaner.py`) `[x]`
- [x] Implement language filtering (`processing/language_filter.py`) `[x]`
- [x] Implement LLM labeling (`processing/labeling.py`) `[x]`
    - [x] Labeling 3139 items with gpt-4o-mini `[x]`

## Phase 4: Pipeline Integration
- [x] Create `main_pipeline.py` `[x]`
- [x] Implement scheduling/automation support (daily/weekly) `[x]`
- [x] Add logging and error handling `[x]`

## Phase 5: Export & Verification
- [x] Implement export logic (JSON, CSV, Parquet) `[x]`
- [x] Verify the pipeline with actual dataset `[x]`
- [x] Update `walkthrough.md` `[x]`

## Phase 6: Dataset Separation
- [x] Create `split_datasets_by_dialect.py` `[x]`
- [x] Verify dataset splitting and record counts `[x]`

## Phase 7: Data Expansion (Scraping - Paused due to Credits)
- [x] Design targeted search queries and scraping plan `[x]`
- [x] Implement `expand_dataset.py` orchestration script `[x]`
- [x] Perform targeted scraping for Mexico (+12k raw) `[x]`
- [/] Perform targeted scraping for Ecuador (In Progress) `[/]`
- [ ] Perform targeted scraping for Honduras (Blocked) `[ ]`

## Phase 8: Synthetic Expansion (Honduras)
- [x] Implement `expand_honduras_synthetic.py` with multi-threading `[x]`
- [x] Generate 3,300+ authentic Honduran variations `[x]`
- [x] Verify final dataset `honduras_dataset_expanded.json` `[x]`
- [x] Repair and balance synthetic dataset `[x]`

## Phase 9: Model Training (Honduran Dialect Classifier)
- [x] Setup PyTorch/HuggingFace ML environment `[x]`
- [x] Load and verify 80/10/10 split datasets `[x]`
- [x] Initialize `dccuchile/bert-base-spanish-wwm-cased` tokenizer and model `[x]`
- [x] Configure `TrainingArguments` (max_len=128, epochs=3, lr=2e-5) `[x]`
- [x] Train the dialect classification model `[x]`
- [x] Evaluate on test split (accuracy, F1) `[x]`
- [x] Run quick inference check on sample sentences `[x]`
- [x] Export trained model and tokenizer to `models/honduras_dialect_classifier/` `[x]`
- [x] Generate final training report `[x]`

## Phase 10: Binary Dialect Classifier (Honduras vs Other)
- [x] Merge Honduras and Other Spanish datasets `[x]`
- [x] Balance dataset representations and create binary labels `[x]`
- [x] Recreate 80/10/10 JSONL data splits `[x]`
- [x] Train `dccuchile/bert-base-spanish-wwm-cased` for 3 epochs `[x]`
- [x] Evaluate model on test set (accuracy, F1, confusion matrix) `[x]`
- [x] Save model to `models/honduras_dialect_binary_classifier/` `[x]`
- [x] Run inference test ("Vos sos maje..." vs "Qué onda wey...") `[x]`

## Phase 11: Video Validation Pipeline
- [x] Set up environment with `ffmpeg`, `openai-whisper`, and `transformers` (CLIP) `[x]`
- [x] Implement video input and `ffmpeg` audio/frame extraction `[x]`
- [x] Implement audio transcription via Whisper `[x]`
- [x] Implement dialect validation using our custom binary classifier `[x]`
- [x] Implement vision analysis using CLIP to match frames against an expected topic `[x]`
- [x] Assemble `video_validator.py` returning JSON validation results `[x]`
- [x] Save inference logs to `reports/video_validation_results.json` `[x]`
- [x] Run a test validation on a sample video `[x]`

## Phase 12: System Validation Testing
- [x] Setup testing framework (`tests/` directory structure) `[x]`
- [x] Generate synthetic text test cases (Honduran vs Negative cases) `[x]`
- [x] Generate synthetic audio samples (using `gTTS` or MacOS `say`) `[x]`
- [x] Generate 50+ localized synthetic test videos (`moviepy` / `ffmpeg`) `[x]`
- [x] Run Component Tests (Dialect Model, Whisper WER, CLIP) `[x]`
- [x] Run End-to-End Pipeline Testing on all generated videos `[x]`
- [x] Run Edge Case and Performance Stress Testing (100 videos) `[x]`
- [x] Generate final `system_validation_report.md` and export CSV metrics `[x]`

## Phase 13: Production Validation Service
- [x] Design service architecture and create `services/` directory `[x]`
- [x] Implement `services/schemas.py` and `services/config.py` `[x]`
- [x] Update `VideoValidator` with 50/50 scoring logic and `validation_status` (PASS/FAIL) `[x]`
- [x] Implement robust file logging to `logs/video_validation.log` `[x]`
- [x] Build FastAPI REST server (`services/api_server.py`) exposing `POST /validate-video` `[x]`
- [x] Build concurrent batch processor (`services/batch_validator.py`) exporting to CSV `[x]`
- [x] Create `tests/test_api.py` and verify endpoint functionality `[x]`
- [x] Generate final `reports/deployment_report.md` with performance metrics `[x]`

## Phase 14: System Monitoring and Drift Detection
- [x] Design monitoring modular architecture (`monitoring/`) `[x]`
- [x] Implement inference metric CSV logging in `video_validator.py` (`logs/inference_metrics.csv`) `[x]`
- [x] Build performance analytics script (`monitoring/model_metrics.py`) exporting `model_performance_report.md` `[x]`
- [x] Create Data Drift detector (`monitoring/drift_detector.py`) checking pass rates and confidence shifts `[x]`
- [x] Implement automated drift alerts to `logs/drift_alert.log` `[x]`
- [x] Construct Streamlit system dashboard (`monitoring/system_dashboard.py`) `[x]`
- [x] Automate Weekly Model Health report generator `[x]`

## Phase 16: Advanced Visual Scene Grounding
- [x] Implement "Comparative Anchor Ensemble" for Image Validation `[x]`
- [x] Add "Top 3 Visual Contexts" display to UI `[x]`
- [x] Refactor VideoValidator frames to use ensemble prompts `[x]`
- [x] Verify image-only accuracy against generic international stills `[x]`
- [x] Synthetic Audio format testing (MP3, WAV, M4A) `[x]`

## Phase 27: Transcription & Vision Optimization
- [x] Migrate to `faster-whisper` (int8 quantized) `[x]`
- [x] Refine CLIP Target labels for better visual grounding `[x]`
- [x] Implement Hierarchical Scoring (Lower threshold for high-confidence dialect) `[x]`
- [x] Verify ASR accuracy on real Ecuadorian videos `[x]`

## Phase 28: Audio Transcription Robustness
- [x] Disable `vad_filter` in `faster-whisper` for musical content `[x]`
- [x] Implement `loudnorm` audio normalization via FFmpeg `[x]`
- [x] Increase ASR logging verbosity (language/probability) `[x]`
- [x] Verify transcription of the "Piero Hincapie" video `[x]`

## Phase 29: ASR Engine Upgrade (large-v3-turbo)
- [x] Upgrade Whisper model from `base` to `large-v3-turbo` `[x]`
- [x] Enable auto language detection (remove forced `language="es"`) `[x]`
- [x] Implement smart dialect routing based on detected language `[x]`
- [x] Deploy to EC2 and verify with Piero Hincapie video `[x]`

## Geographic & Localism Refinement
- [x] Expand `COUNTRY_CONFIG` with local slang keywords `[x]`
- [x] Implement AI-Confidence-Balanced Neutrality Override `[x]`
- [x] Unify Audio & Video validation logic in `app.py` `[x]`
- [x] Deploy to EC2 with 2GB Swap buffer and headless flags `[x]`

## Phase 15: Full System Stress Testing
- [x] Initialize `tests/full_system/` architecture framework `[x]`
- [x] Generate 500 text validation metrics & confusion matrix `[x]`
- [x] Generate 200 audio tests (Speech variations, Noise edge-cases) `[x]`
- [x] Generate 200 image matching tests mapping CLIP distributions `[x]`
- [x] Generate 150 E2E `moviepy` videos corrupting logic boundaries `[x]`
- [x] Deploy 200 API load tests checking REST latency and Memory limits `[x]`
- [x] Batch process 200 videos checking throughput scalability `[x]`
- [x] Test pipeline crash guards (Corrupted files, 1-sec clips, No audio) `[x]`
- [x] Trigger Monitoring drift checks deliberately to verify logs `[x]`
- [x] Load Test synchronously over 500 total video loops evaluating max RAM `[x]`
- [x] Output `reports/full_system_validation_report.md` `[x]`

## Phase 16: Containerization and Production Deployment
- [x] Create production `Dockerfile` for `video-validator:latest` `[x]`
- [x] Install system dependencies (`ffmpeg`, `libsm6`, `libxext6`) in Docker image `[x]`
- [x] Set up `docker-compose.yml` for `api_server` and `monitoring_dashboard` `[x]`
- [x] Map environment variables (`MODEL_PATH`, `LOG_PATH`, `VALIDATION_THRESHOLD`) `[x]`
- [x] Configure volume mounts for `videos/`, `logs/`, and `reports/` `[x]`
- [x] Test container orchestration with `docker-compose up` (Validated configurations offline) `[x]`
- [x] Verify `POST /validate-video` endpoint on the containerized API `[x]`
- [x] Generate final `reports/container_deployment_report.md` `[x]`

## Phase 17: Client Validation Testing (Ruhani Data)
- [x] Install `gdown` and download Google Drive folder (`1_spPj20MGKhVEbibAxqJjw9RhKDbnEUt`) `[x]`
- [x] Save the 12 text comments into `datasets/ruhani_test/comments.json` `[x]`
- [x] Validate 12 Text comments against Dialect binary classifier `[x]`
- [x] Validate 10 Images securely against PyTorch CLIP models `[x]`
- [x] Validate 10 Video Reels using the `VideoValidator` pipeline `[x]`
- [x] Compile testing outputs into `reports/ruhani_marketing_test_report.md` `[x]`

## Phase 18: Interactive User Frontend
- [x] Initialize `app.py` scaling a premium interactive Streamlit environment `[x]`
- [x] Design 4 isolated testing modes (Text, Image, Audio, Video) `[x]`
- [x] Write logic evaluating Dialect NLP Text nodes directly onto UI `[x]`
- [x] Integrate local Image evaluation evaluating CLIP vision metrics `[x]`
- [x] Stitch `gTTS`/`Whisper` Audio pipeline transcriptions visually `[x]`
- [x] Connect `VideoValidator` class natively visualizing FFmpeg frame extractions `[x]`
- [x] Inject markdown alerts verifying which AI tools process which layers natively `[x]`

## Phase 19: Advanced OCR & Strict Multimodal Validation
- [x] Install `easyocr` to map explicit visual text parsing natively `[x]`
- [x] Update `VideoValidator.py` adding OCR blacklist forcing frame-based Fail overrides `[x]`
- [x] Refactor `CLIPModel` utilizing comparative Softmax probabilities (`Honduras` vs `Ecuador` vs `Mexico`) `[x]`
- [x] Implement OCR Text Extraction arrays seamlessly mapping directly to `app.py` Image Mode `[x]`
- [x] Implement robust Image Mode visual rendering logging comparative CLIP matrices on UI `[x]`

## Phase 20: Git Repository Deployment
- [x] Configure strict `.gitignore` mapping explicit macOS/USB ghosts and heavy 100MB media overrides `[x]`
- [x] Document Streamlit Share Cloud deployment logic seamlessly into `README.md` natively `[x]`
- [x] Commit and push the structural platform directly to `1Touch-dev` explicitly `[x]`
- [ ] Document repository migration to `ecuador-branch` `[ ]`

## Phase 21: Ecuador Expansion (Data)
- [x] Initialize `ecuador-branch` environment `[x]`
- [x] Research and select most cost-effective Apify scrapers `[x]`
- [x] Implement and run `scraper/ecuador_twitter_scraper.py` (Target: 1000 items) `[x]`
- [x] Implement and run `scraper/ecuador_reddit_scraper.py` (Target: 500 items) `[x]`
- [x] Implement and run `scraper/ecuador_reviews_scraper.py` (Target: 500 items) `[x]`
- [x] Run cleanup and language filtering for Ecuador raw data `[x]`
- [x] Implement `expand_ecuador_synthetic.py` (Target: 1500+ items) `[x]`
- [x] Merge and balance Ecuador Binary Dataset (7,000 samples) `[x]`
- [x] Verify dataset readiness and sync to EC2 `[x]`

## Phase 22: Ecuador Model Training
- [x] Create training script for BETO fine-tuning `[x]`
- [x] Run high-speed local training on M4 (96.14% Accuracy) `[x]`
- [x] Export final model and verify metrics `[x]`

## Phase 23: Logic Refactor (Multi-Country)
- [x] Add multi-country configuration mapping `[x]`
- [x] Support dynamic model loading based on selection `[x]`
- [x] Update vision blacklists and comparative targets `[x]`

## Phase 24: UI Extension (Streamlit)
- [x] Add country selector to sidebar `[x]`
- [x] Support dynamic UI updates per selection `[x]`

## Phase 25: Production Validation
- [x] E2E test with real Ecuadorian marketing reels `[x]`
- [x] Verify validation reports accuracy `[x]`
- [x] Deploy to EC2 production environment `[x]`


