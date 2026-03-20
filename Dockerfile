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

# Copy python dependencies
COPY requirements.txt .

# Install Python packages
# We force CPU PyTorch to avoid massive CUDA images for basic testing, 
# but in a real prod environment we might use nvidia-docker.
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn pydantic python-multipart torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy application files
COPY app.py .
COPY video_validator.py .
COPY services/ ./services/
COPY monitoring/ ./monitoring/

# Create volume mount points
RUN mkdir -p /app/videos /app/models /app/logs /app/reports

# Map Envs
ENV MODEL_PATH=/app/models/honduras_dialect_binary_classifier
ENV LOG_PATH=/app/logs/video_validation.log
ENV VALIDATION_THRESHOLD=0.7

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Command to run the FastAPI server natively via Uvicorn
CMD ["uvicorn", "services.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
