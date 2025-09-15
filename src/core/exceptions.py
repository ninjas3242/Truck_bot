"""
Custom exceptions for better error handling
"""

class ChatbotError(Exception):
    """Base exception for chatbot errors"""
    pass

class AIServiceError(ChatbotError):
    """AI service related errors"""
    pass

class LanguageError(ChatbotError):
    """Language processing errors"""
    pass

class ValidationError(ChatbotError):
    """Data validation errors"""
    pass

class ConfigurationError(ChatbotError):
    """Configuration related errors"""
    pass