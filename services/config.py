import os

BASE_DIR = os.environ.get("BASE_DIR", "/app" if os.path.exists("/app/models") else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DIALECT_MODEL_PATH = os.path.join(MODELS_DIR, "honduras_dialect_binary_classifier")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Thresholds
VALIDATION_THRESHOLD = 0.70
