"""
Chat utility functions and helpers
"""
import time
import streamlit as st
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatMessage:
    def __init__(self, content: str, is_user: bool, timestamp: Optional[datetime] = None):
        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "is_user": self.is_user,
            "timestamp": self.timestamp.isoformat()
        }

class ChatSession:
    def __init__(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "user_context" not in st.session_state:
            st.session_state.user_context = {}
    
    def add_message(self, content: str, is_user: bool):
        """Add a message to chat history"""
        message = ChatMessage(content, is_user)
        st.session_state.chat_history.append(message)
    
    def get_history(self) -> List[ChatMessage]:
        """Get chat history"""
        return st.session_state.chat_history
    
    def clear_history(self):
        """Clear chat history"""
        st.session_state.chat_history = []
        st.session_state.user_context = {}
    
    def update_context(self, key: str, value: Any):
        """Update user context"""
        st.session_state.user_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get user context value"""
        return st.session_state.user_context.get(key, default)

def simulate_typing(duration: float = 1.0):
    """Simulate typing delay for more natural conversation"""
    time.sleep(duration)

def format_truck_info(truck_data: Dict[str, Any]) -> str:
    """Format truck information for display"""
    return f"""
    **{truck_data.get('name', 'Unknown Truck')}**
    - Price: ${truck_data.get('price', 'N/A'):,}
    - Year: {truck_data.get('year', 'N/A')}
    - Condition: {truck_data.get('condition', 'N/A')}
    - Features: {', '.join(truck_data.get('features', []))}
    """

def extract_intent(user_message: str) -> str:
    """Simple intent extraction from user message"""
    message_lower = user_message.lower()
    
    # Intent keywords mapping
    intents = {
        "greeting": ["hello", "hi", "hey", "good morning", "good afternoon"],
        "truck_inquiry": ["truck", "vehicle", "horse truck", "trailer", "all trucks", "list", "stx trucks", "what do you do", "best truck"],
        "pricing": ["price", "cost", "budget", "expensive", "cheap", "affordable"],
        "financing": ["finance", "loan", "payment", "monthly", "credit", "financing options"],
        "contact": ["contact", "phone", "email", "address", "visit", "appointment"],
        "new_trucks": ["new", "brand new", "latest"],
        "used_trucks": ["used", "second hand", "pre-owned"],
        "features": ["features", "specifications", "specs", "details"]
    }
    
    for intent, keywords in intents.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent
    
    return "general"

# Global chat session instance
chat_session = ChatSession()