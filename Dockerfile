FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg for Whisper extraction, libgl1 for OpenCV)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch FIRST (separate index)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy and install remaining Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY video_validator.py .
COPY services/ ./services/
COPY monitoring/ ./monitoring/
COPY .streamlit/ ./.streamlit/

# Create volume mount points
RUN mkdir -p /app/videos /app/models /app/logs /app/reports

# Environment
ENV MODEL_PATH=/app/models/honduras_dialect_binary_classifier
ENV LOG_PATH=/app/logs/video_validation.log
ENV VALIDATION_THRESHOLD=0.7

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Default command (overridden by docker-compose per service)
CMD ["uvicorn", "services.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
