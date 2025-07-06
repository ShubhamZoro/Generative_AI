import os
from pathlib import Path

# API Keys
OPENAI_API_KEY = 
GEMINI_API_KEY = 

# Directories
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "test_results"
SCREENSHOTS_DIR = RESULTS_DIR / "screenshots"
VIDEOS_DIR = RESULTS_DIR / "videos"

# Ensure directories exist
RESULTS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

# Recruter.ai Configuration
RECRUTER_CONFIG = {
    "base_url": "https://app.recruter.ai/",
    "credentials": {
        "email": "shubham.20gcebcs091@galgotiacollege.edu",
        "password": "Piratehunter1@"
    },
    "test_data": {
        "job_description": "Python Developer with 2+ years of experience needed for developing web applications using Django and Flask frameworks.",
        "skills": ["Python", "Django"],
        "experience_years": 2,
        "job_title": "Senior Python Developer",
        "company_name": "TechCorp Solutions"
    }
}

# Browser Configuration
BROWSER_CONFIG = {
    "headless": False,
    "slow_mo": 800,
    "viewport": {"width": 1280, "height": 720},
    "timeout": 30000
}

# LLM Configuration
LLM_CONFIG = {
    "model": "gpt-4o",
    "temperature": 0,
    "max_tokens": 4000
}

# Default video URL for testing
DEFAULT_VIDEO_URL = "https://www.youtube.com/watch?v=IK62Rk47aas"
