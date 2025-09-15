"""
Configuration settings for the Truck Sales Chatbot
"""
import os
from typing import Dict, List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

# Load environment variables
load_dotenv()

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
    gemini_api_key: str = Field(env="GEMINI_API_KEY")
    
    # AI Configuration
    use_ai: bool = True
    ai_model: str = "gemini-2.5-flash"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Chat Configuration
    max_chat_history: int = 50
    typing_delay: float = 0.5
    
    # Cache Configuration
    cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 128
    
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
BOT_NAME = "TruckBot"
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