"""
Google Calendar integration for Streamlit Cloud
"""
import streamlit as st
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlencode, parse_qs, urlparse
import json

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
    
    def handle_oauth_callback(self, authorization_code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        try:
            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': authorization_code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                st.session_state.google_access_token = access_token
                return access_token
        except Exception as e:
            print(f"OAuth callback error: {e}")
        return None
    
    def create_appointment_from_session(self) -> bool:
        """Create calendar event from session booking data"""
        booking_data = st.session_state.get('booking_data', {})
        if not booking_data:
            return False
        
        # Parse date string to datetime (simple parsing)
        from datetime import datetime, timedelta
        date_str = booking_data.get('date_time_str', '')
        
        # Simple date parsing for "tomorrow 2pm"
        if 'tomorrow' in date_str.lower():
            tomorrow = datetime.now() + timedelta(days=1)
            if '2pm' in date_str.lower() or '2 pm' in date_str.lower():
                appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
            else:
                appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)  # default 2pm
        else:
            # Default to tomorrow 2pm if can't parse
            tomorrow = datetime.now() + timedelta(days=1)
            appointment_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        
        summary = f"Stephex Horse Trucks - {booking_data.get('truck_type', 'Truck')} Consultation"
        description = f"Consultation for {booking_data.get('truck_type', 'truck')} with {booking_data.get('email', 'customer')}"
        
        return self.create_calendar_event(summary, appointment_time, 1, description)
    
    def create_calendar_event(self, summary: str, start_time: datetime, duration_hours: int = 1, description: str = "") -> bool:
        """Create actual calendar event using Google Calendar API"""
        access_token = st.session_state.get('google_access_token')
        if not access_token:
            return False
        
        try:
            end_time = start_time + timedelta(hours=duration_hours)
            
            event_data = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Europe/Brussels'
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Europe/Brussels'
                },
                'attendees': [
                    {'email': 'sales@stephex.test'},
                    {'email': 'demo@stephex.test'}
                ]
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://www.googleapis.com/calendar/v3/calendars/primary/events',
                headers=headers,
                data=json.dumps(event_data)
            )
            
            return response.status_code == 200
                
        except Exception as e:
            print(f"Calendar event creation error: {e}")
        
        return False
    
    def create_event_simple(self, summary: str, start_time: datetime, attendee_email: str) -> str:
        """Create a simple calendar event (placeholder for now)"""
        return f"Appointment '{summary}' scheduled for {start_time.strftime('%B %d, %Y at %I:%M %p')}"

# Global instance
calendar_service = GoogleCalendarService()