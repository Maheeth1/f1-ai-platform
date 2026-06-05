import os
from pathlib import Path
import sys

# Environment configurations
ENV = os.getenv("ENV", "development")

# Detect if running in Google Colab
IN_COLAB = 'google.colab' in sys.modules

if IN_COLAB:
    # Use Google Drive for persistent storage when in Colab
    ROOT_DIR = Path('/content/drive/MyDrive/F1_AI_Data')
    DATA_DIR = ROOT_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    CACHE_DIR = Path('/content/f1_cache')
else:
    # Project Roots for local/docker execution
    # If DOCKER_ROOT is set, use it, otherwise use file relative path
    docker_root = os.getenv("APP_ROOT")
    if docker_root:
        ROOT_DIR = Path(docker_root)
    else:
        ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
        
    DATA_DIR = ROOT_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    CACHE_DIR = ROOT_DIR / "cache"

# FastF1 Settings
FASTF1_CACHE_DIR = CACHE_DIR
TARGET_YEARS = [2022, 2023, 2024, 2025]

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)
