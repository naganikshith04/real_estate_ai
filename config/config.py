"""
Configuration management for Real Estate AI
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = BASE_DIR / 'data'
REPORTS_DIR = DATA_DIR / 'reports'
ANALYSIS_DIR = DATA_DIR / 'analysis'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Data file paths
PROPERTY_LISTINGS_FILE = DATA_DIR / 'property_listings.json'
HISTORICAL_PRICES_FILE = DATA_DIR / 'historical_prices.json'
INFRASTRUCTURE_PROJECTS_FILE = DATA_DIR / 'infrastructure_projects.json'
FINAL_RECOMMENDATIONS_FILE = REPORTS_DIR / 'final_recommendations.json'
ROI_ANALYSIS_FILE = REPORTS_DIR / 'roi_analysis_sample.json'

# API Configuration defaults
DEFAULT_MODEL = "gpt-4o"  # Default model when API is available
FALLBACK_MODE = True      # Whether to fall back to demo mode if API is unavailable

# Target cities
TARGET_CITIES = ["Mumbai", "Bangalore", "Hyderabad", "Pune", "Delhi-NCR"]

# Free alternatives for APIs
FREE_LLM_ENDPOINTS = [
    {
        "name": "Ollama",
        "api_base": "http://localhost:11434/api",
        "models": ["llama3", "mistral", "mixtral"]
    },
    {
        "name": "LocalAI",
        "api_base": "http://localhost:8080/v1",
        "models": ["gpt4all", "orca-mini"]
    }
]

# Geocoding API alternatives (free)
GEOCODING_APIS = [
    {
        "name": "Nominatim",
        "url": "https://nominatim.openstreetmap.org/search",
        "params": {"format": "json", "limit": 1}
    }
]

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "real_estate_ai.log",
            "formatter": "standard"
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        }
    },
    "loggers": {
        "": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True
        }
    }
}