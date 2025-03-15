import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Model Configuration
MODEL_NAME = "deepseek/deepseek-r1:free"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/"

# Cache Configuration
CACHE_EXPIRATION = {
    "news": 60 * 60 * 24 * 3,  # 3 days
    "academic": 60 * 60 * 24 * 30 * 3,  # 3 months
    "historical": 60 * 60 * 24 * 30 * 12,  # 12 months
}

# Source Credibility Configuration
DOMAIN_CREDIBILITY = {
    "edu": 0.9,
    "gov": 0.9,
    "org": 0.7,
    "default": 0.5,
}

# Credibility Factors
CREDIBILITY_WEIGHTS = {
    "domain_authority": 0.3,
    "freshness": 0.2,
    "citations": 0.2,
    "author_credentials": 0.15,
    "content_quality": 0.15,
}

# Search Configuration
MAX_SEARCH_RESULTS = 10
SEARCH_TIMEOUT = 30  # seconds

# UI Configuration
MAX_CHAT_HISTORY = 50
CHAT_PREVIEW_LENGTH = 100 