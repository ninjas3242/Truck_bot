"""
Configuration settings for the Truck Sales Chatbot
"""
import os
from typing import Dict, List
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

# Streamlit secrets support
try:
    import streamlit as st
    USE_STREAMLIT_SECRETS = True
except ImportError:
    USE_STREAMLIT_SECRETS = False
    # Fallback to dotenv for local development
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

class Settings(BaseSettings):
    """Application settings with validation"""
    
    # App Configuration
    app_title: str = "Stephex Horse Trucks - AI Assistant"
    app_icon: str = "🚛"
    company_name: str = "Stephex Horse Trucks"
    
    # Environment
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Keys
    gemini_api_key: str = Field(default="")
    google_client_id: str = Field(default="")
    google_client_secret: str = Field(default="")
    google_redirect_uri: str = Field(default="http://localhost:8501")
    
    def __init__(self, **kwargs):
        # Get API keys from Streamlit secrets or environment
        if USE_STREAMLIT_SECRETS and hasattr(st, 'secrets'):
            try:
                kwargs['gemini_api_key'] = st.secrets["GEMINI_API_KEY"]
                kwargs['google_client_id'] = st.secrets.get("GOOGLE_CLIENT_ID", "")
                kwargs['google_client_secret'] = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
                kwargs['google_redirect_uri'] = st.secrets.get("GOOGLE_REDIRECT_URI", "http://localhost:8501")
            except KeyError:
                pass
        else:
            kwargs['gemini_api_key'] = os.getenv("GEMINI_API_KEY", "")
            kwargs['google_client_id'] = os.getenv("GOOGLE_CLIENT_ID", "")
            kwargs['google_client_secret'] = os.getenv("GOOGLE_CLIENT_SECRET", "")
            kwargs['google_redirect_uri'] = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
        
        super().__init__(**kwargs)
    
    # AI Configuration
    use_ai: bool = True
    ai_model: str = "gemini-2.5-flash"
    max_tokens: int = 300000
    temperature: float = 0.7
    
    # Chat Configuration
    max_chat_history: int = 50
    typing_delay: float = 0.5
    
    # Cache Configuration
    cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 500
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Español", 
    "fr": "Français",
    "it": "Italiano",
    "nl": "Nederlands"
}

# Default Language
DEFAULT_LANGUAGE = "en"

# UI Colors
COLORS = {
    "primary": "#1f2937",
    "secondary": "#3b82f6", 
    "accent": "#10b981",
    "background": "#f8fafc",
    "text": "#1f2937",
    "border": "#e5e7eb",
    "success": "#059669",
    "warning": "#d97706",
    "error": "#dc2626"
}

# Bot Personality
BOT_NAME = "Stephanie"
BOT_AVATAR = "🤖"
USER_AVATAR = "👤"

# Legacy support for existing code
settings = get_settings()
APP_TITLE = settings.app_title
APP_ICON = settings.app_icon
DEBUG = settings.debug
GEMINI_API_KEY = settings.gemini_api_key
USE_AI = settings.use_ai
AI_MODEL = settings.ai_model
MAX_TOKENS = settings.max_tokens
TEMPERATURE = settings.temperature
MAX_CHAT_HISTORY = settings.max_chat_history
TYPING_DELAY = settings.typing_delay