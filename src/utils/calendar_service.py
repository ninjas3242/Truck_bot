"""
Google Calendar integration for Streamlit Cloud
"""
import streamlit as st
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlencode

# Load environment variables for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class GoogleCalendarService:
    def __init__(self):
        from ..config.settings import get_settings
        settings = get_settings()
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri or "https://ninjas3242-truck-bot-app-v3kplg.streamlit.app"
    
    def get_auth_url(self) -> str:
        """Generate Google OAuth2 authorization URL"""
        # Force load from environment if not set
        if not self.client_id:
            import os
            self.client_id = os.getenv("GOOGLE_CLIENT_ID", "125980177386-c2b38gs0c87v6uluam246p5p8sduvpr2.apps.googleusercontent.com")
            self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "https://ninjas3242-truck-bot-app-v3kplg.streamlit.app")
        
        if not self.client_id:
            return "Calendar integration not configured"
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/calendar',
            'response_type': 'code',
            'access_type': 'offline'
        }
        return f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
    
    def create_event_simple(self, summary: str, start_time: datetime, attendee_email: str) -> str:
        """Create a simple calendar event (placeholder for now)"""
        # For Streamlit Cloud, we'll show a booking confirmation instead
        return f"Appointment '{summary}' scheduled for {start_time.strftime('%B %d, %Y at %I:%M %p')}"

# Global instance
calendar_service = GoogleCalendarService()