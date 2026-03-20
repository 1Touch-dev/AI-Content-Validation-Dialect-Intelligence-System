import os
import sys

# Ensure parent path for VideoValidator resolution natively
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from services.schemas import VideoValidationRequest, VideoValidationResponse
from services.config import VALIDATION_THRESHOLD

# Load the heavy ML model uniquely into app state during startup
from video_validator import VideoValidator
import uvicorn

app = FastAPI(title="Video Validation Service")
validator = None

@app.on_event("startup")
def startup_event():
    global validator
    # Initialize the validator explicitly on startup preventing cold-starts
    validator = VideoValidator()

@app.post("/validate-video", response_model=VideoValidationResponse)
def validate_video(request: VideoValidationRequest):
    if not os.path.exists(request.video_path):
        raise HTTPException(status_code=400, detail="Video file not found.")
        
    try:
        result = validator.validate_video(request.video_path, expected_content=request.expected_topic)
        if not result:
            raise HTTPException(status_code=500, detail="Validation failed internally.")
            
        result["dialect_prediction"] = result.pop("dialect_predicted", "Other")
        return VideoValidationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("services.api_server:app", host="0.0.0.0", port=8000, reload=False)
