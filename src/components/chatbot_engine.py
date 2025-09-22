"""
Main chatbot engine with conversation logic
"""
import pandas as pd
from pathlib import Path
from ..utils.ai_service import ai_service
from ..config.settings import get_settings

settings = get_settings()

class ChatbotEngine:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Load all data files as comprehensive knowledge base"""
        data_path = Path(__file__).parent.parent.parent / "data"
        knowledge = {}
        
        try:
            # Load new trucks inventory
            new_trucks_df = pd.read_csv(data_path / "new_trucks.csv")
            knowledge['new_trucks'] = new_trucks_df.to_dict('records')
            
            # Load used trucks inventory
            used_trucks_df = pd.read_csv(data_path / "used_trucks.csv")
            knowledge['used_trucks'] = used_trucks_df.to_dict('records')
            
            # Load contact information
            with open(data_path / "contact.txt", 'r', encoding='utf-8') as f:
                knowledge['contact_info'] = f.read()
            
            # Load all dealer information
            dealer_files = ['Dealer name stx.txt', 'Dealer names AKX.txt', 'dealer names KETTERER copy.txt']
            knowledge['dealers'] = {}
            for dealer_file in dealer_files:
                try:
                    with open(data_path / dealer_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'stx' in dealer_file.lower():
                            knowledge['dealers']['STX'] = content
                        elif 'akx' in dealer_file.lower():
                            knowledge['dealers']['AKX'] = content
                        elif 'ketterer' in dealer_file.lower():
                            knowledge['dealers']['KETTERER'] = content
                except Exception as e:
                    print(f"Error loading {dealer_file}: {e}")
            
            # Load all remaining text files
            text_files = ['new trucks detialed.txt', 'used trucks Details.txt']
            knowledge['detailed_info'] = {}
            for text_file in text_files:
                try:
                    with open(data_path / text_file, 'r', encoding='utf-8') as f:
                        knowledge['detailed_info'][text_file] = f.read()
                except:
                    pass
            
            # Load legacy data if exists
            try:
                company_df = pd.read_csv(data_path / "company_data.csv")
                knowledge['company'] = company_df.to_dict('records')
            except:
                pass
                
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            
        return knowledge
    
    def process_message(self, user_message: str, language: str = "en") -> str:
        """Process user message and generate appropriate response"""
        
        # Handle greetings
        if any(word in user_message.lower() for word in ["hi", "hello", "hey"]) and len(user_message.split()) <= 2:
            return "👋 Welcome to Stephex Horse Trucks! I'm your AI assistant specializing in premium horse transportation solutions. I can help you find the perfect truck, What can I assist you with today?"
        
        # Enhanced appointment booking detection
        booking_indicators = [
            'book', 'appointment', 'schedule', 'meeting', 'visit', 'see trucks', 
            'showroom', 'come see', 'meet', 'consultation', 'demo', 'test drive'
        ]
        time_indicators = ['tomorrow', 'today', 'next week', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'pm', 'am']
        email_indicators = ['@', '.com', '.org', '.net', 'gmail', 'email']
        
        message_lower = user_message.lower()
        has_booking_word = any(word in message_lower for word in booking_indicators)
        has_time_word = any(word in message_lower for word in time_indicators)
        has_email = any(word in message_lower for word in email_indicators)
        
        # Direct booking detection - bypass AI for booking
        if has_booking_word and (has_time_word or has_email):
            import re
            
            # Extract email
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', user_message)
            email = email_match.group() if email_match else ''
            
            # Extract time info
            time_info = ''
            if 'tomorrow' in message_lower:
                time_info = 'tomorrow'
            elif 'today' in message_lower:
                time_info = 'today'
            elif 'next week' in message_lower:
                time_info = 'next week'
            
            # Extract specific time - handle both "9am" and "9 am"
            time_match = re.search(r'(\d{1,2})\s*(am|pm)', message_lower)
            if time_match:
                time_info += f' {time_match.group()}'
            
            # Extract location/timezone
            if 'london' in message_lower:
                time_info += ' london'
            
            print(f"DEBUG: Extracted - Email: {email}, Time: '{time_info}'")
            if 'london' in time_info.lower():
                print(f"DEBUG: Detected London timezone request")
            
            # If we have enough info, create booking directly
            if email and time_info:
                try:
                    import streamlit as st
                    from datetime import datetime, timedelta
                    from urllib.parse import quote
                    import pytz
                    

                    
                    truck_type = 'general consultation'
                    date_time_str = time_info
                    
                    # Store in session
                    st.session_state.booking_data = {
                        'truck_type': truck_type,
                        'date_time_str': date_time_str,
                        'email': email
                    }
                    
                    # Remember user info
                    st.session_state.user_email = email
                    
                    # Detect timezone from user input
                    user_timezone = None
                    if 'london' in time_info.lower():
                        user_timezone = pytz.timezone('Europe/London')
                    elif 'new york' in time_info.lower() or 'ny' in time_info.lower():
                        user_timezone = pytz.timezone('America/New_York')
                    elif 'tokyo' in time_info.lower():
                        user_timezone = pytz.timezone('Asia/Tokyo')
                    elif 'sydney' in time_info.lower():
                        user_timezone = pytz.timezone('Australia/Sydney')
                    elif 'paris' in time_info.lower():
                        user_timezone = pytz.timezone('Europe/Paris')
                    elif 'berlin' in time_info.lower():
                        user_timezone = pytz.timezone('Europe/Berlin')
                    elif 'dubai' in time_info.lower():
                        user_timezone = pytz.timezone('Asia/Dubai')
                    
                    # Parse date (always start with naive datetime)
                    now = datetime.now()
                    print(f"DEBUG: Using timezone: {user_timezone.zone if user_timezone else 'local'}")
                    
                    # Create target date as naive datetime
                    if 'tomorrow' in date_time_str.lower():
                        target_date = (now + timedelta(days=1)).replace(tzinfo=None)
                    elif '2 days' in date_time_str.lower():
                        target_date = (now + timedelta(days=2)).replace(tzinfo=None)
                    elif '20th' in date_time_str.lower() or ' 20 ' in date_time_str:
                        target_date = now.replace(day=20, tzinfo=None)
                        if target_date < now.replace(tzinfo=None):
                            if now.month == 12:
                                target_date = target_date.replace(year=now.year + 1, month=1)
                            else:
                                target_date = target_date.replace(month=now.month + 1)
                    else:
                        target_date = (now + timedelta(days=1)).replace(tzinfo=None)
                        
                    # Parse time from user input - handle both "9am" and "9 am" formats
                    hour = 14  # default
                    time_str = date_time_str.lower()
                    
                    print(f"DEBUG: Parsing time from: '{time_str}' with timezone detection")
                    
                    # Check longer patterns first to avoid partial matches
                    if '12pm' in time_str or '12 pm' in time_str:
                        hour = 12
                    elif '11am' in time_str or '11 am' in time_str:
                        hour = 11
                    elif '10am' in time_str or '10 am' in time_str:
                        hour = 10
                    elif '1am' in time_str or '1 am' in time_str:
                        hour = 1
                    elif '2am' in time_str or '2 am' in time_str:
                        hour = 2
                    elif '3am' in time_str or '3 am' in time_str:
                        hour = 3
                    elif '4am' in time_str or '4 am' in time_str:
                        hour = 4
                    elif '5am' in time_str or '5 am' in time_str:
                        hour = 5
                    elif '6am' in time_str or '6 am' in time_str:
                        hour = 6
                    elif '7am' in time_str or '7 am' in time_str:
                        hour = 7
                    elif '8am' in time_str or '8 am' in time_str:
                        hour = 8
                    elif '9am' in time_str or '9 am' in time_str:
                        hour = 9
                    elif '1pm' in time_str or '1 pm' in time_str:
                        hour = 13
                    elif '2pm' in time_str or '2 pm' in time_str:
                        hour = 14
                    elif '3pm' in time_str or '3 pm' in time_str:
                        hour = 15
                    elif '4pm' in time_str or '4 pm' in time_str:
                        hour = 16
                    elif '5pm' in time_str or '5 pm' in time_str:
                        hour = 17
                    elif '6pm' in time_str or '6 pm' in time_str:
                        hour = 18
                    

                    
                    # Create appointment time in specified timezone
                    if user_timezone:
                        # Create naive datetime first, then localize
                        naive_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0, tzinfo=None)
                        start_time = user_timezone.localize(naive_time)
                        timezone_note = f" ({user_timezone.zone})"
                    else:
                        # Use local timezone
                        start_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                        timezone_note = ""
                    
                    end_time = start_time + timedelta(hours=1)
                    
                    print(f"DEBUG: Appointment time: {start_time} in {user_timezone.zone if user_timezone else 'local timezone'}")
                    
                    # Create calendar link
                    title = f"Stephex Horse Trucks - {truck_type}"
                    details = f"Consultation with Stephex Horse Trucks\nContact: {email}"
                    location = "Stephex Horse Trucks Showroom"
                    
                    # Format for Google Calendar (always in UTC)
                    if user_timezone:
                        # Convert to UTC for Google Calendar
                        start_utc = start_time.astimezone(pytz.UTC)
                        end_utc = end_time.astimezone(pytz.UTC)
                        calendar_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(title)}&dates={start_utc.strftime('%Y%m%dT%H%M%SZ')}/{end_utc.strftime('%Y%m%dT%H%M%SZ')}&details={quote(details)}&location={quote(location)}"
                    else:
                        calendar_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(title)}&dates={start_time.strftime('%Y%m%dT%H%M%S')}/{end_time.strftime('%Y%m%dT%H%M%S')}&details={quote(details)}&location={quote(location)}"
                    
                    formatted_date = start_time.strftime('%B %d, %Y at %I:%M %p') + timezone_note

                    
                    timezone_info = f" in {user_timezone.zone}" if user_timezone else ""
                    return f"Perfect! Your appointment is ready{timezone_info}:\n\n📋 **Appointment Details:**\n• **Service:** {truck_type}\n• **Date & Time:** {formatted_date}\n• **Contact:** {email}\n\n<a href='{calendar_url}' target='_blank' style='background: #007bff; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;'>📅 Add to Google Calendar</a>\n\nOur team will contact you to confirm details."
                    
                except Exception as e:
                    print(f"DEBUG: Error in booking: {e}")
                    return "Sorry, there was an error processing your booking. Please try again."
            
            # If missing info, ask for it
            if not email:
                return "I'd be happy to book an appointment! What's your email address?"
            if not time_info:
                return "What date and time works for you?"
        
        # For non-booking queries, use AI
        if has_booking_word or has_time_word or has_email:
            # Pass to AI for booking-related questions that aren't complete bookings
            try:
                import streamlit as st
                user_email = st.session_state.get('user_email', '')
                user_prefs = st.session_state.get('user_preferences', {})
                chat_history = st.session_state.get('chat_history', [])
            except:
                user_email = ''
                user_prefs = {}
                chat_history = []
            
            conversation_context = ""
            if chat_history:
                for msg in chat_history[-6:]:
                    role = "User" if msg.is_user else "Stephanie"
                    conversation_context += f"{role}: {msg.content}\n"
            
            context = {
                'knowledge_base': self.knowledge_base,
                'user_message': user_message,
                'booking_mode': True,
                'user_email': user_email,
                'user_preferences': user_prefs,
                'conversation_history': conversation_context
            }
            return ai_service.generate_response(user_message, context, language)
        
        # Use AI for everything else
        import streamlit as st
        chat_history = st.session_state.get('chat_history', [])
        
        # Format conversation history for context
        conversation_context = ""
        if chat_history:
            for msg in chat_history[-6:]:  # Last 6 messages for context
                role = "User" if msg.is_user else "Stephanie"
                conversation_context += f"{role}: {msg.content}\n"
        
        context = {
            'knowledge_base': self.knowledge_base,
            'user_message': user_message,
            'conversation_history': conversation_context
        }
        response = ai_service.generate_response(user_message, context, language)
        
        return response

# Global chatbot engine instance
chatbot_engine = ChatbotEngine()