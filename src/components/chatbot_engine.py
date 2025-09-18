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
            return "👋 Welcome to Stephex Horse Trucks! I'm your AI assistant specializing in premium horse transportation solutions. I can help you find the perfect truck, and answer any questions about our inventory. What can I assist you with today?"
        
        # Enhanced appointment booking detection
        booking_indicators = [
            'book', 'appointment', 'schedule', 'meeting', 'visit', 'see trucks', 
            'showroom', 'come see', 'meet', 'consultation', 'demo', 'test drive'
        ]
        time_indicators = ['tomorrow', 'today', 'next week', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'pm', 'am']
        
        message_lower = user_message.lower()
        has_booking_word = any(word in message_lower for word in booking_indicators)
        has_time_word = any(word in message_lower for word in time_indicators)
        
        # Let AI handle booking intelligently - no complex state management
        if has_booking_word or has_time_word:
            # Just pass to AI with special booking context
            # Add user memory to context for smart booking
            import streamlit as st
            user_email = st.session_state.get('user_email', '')
            user_prefs = st.session_state.get('user_preferences', {})
            
            context = {
                'knowledge_base': self.knowledge_base,
                'user_message': user_message,
                'booking_mode': True,
                'user_email': user_email,
                'user_preferences': user_prefs
            }
            response = ai_service.generate_response(user_message, context, language)
            
            # Check if AI completed booking
            if "BOOKING_COMPLETE:" in response:
                try:
                    import streamlit as st
                    from ..utils.calendar_service import calendar_service
                    
                    print(f"DEBUG: Detected BOOKING_COMPLETE in response: {response}")
                    
                    # Parse booking data
                    booking_info = response.split("BOOKING_COMPLETE:")[1].strip()
                    parts = booking_info.split("|")
                    
                    print(f"DEBUG: Parsed booking parts: {parts}")
                    print(f"DEBUG: Current date/time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                except Exception as e:
                    print(f"DEBUG: Error in booking processing: {e}")
                    return "Sorry, there was an error processing your booking. Please try again."
                
                if len(parts) >= 3:
                    truck_type = parts[0].strip()
                    date_time_str = parts[1].strip()
                    email = parts[2].strip()
                    
                    # Store in session for calendar creation AND remember for future bookings
                    st.session_state.booking_data = {
                        'truck_type': truck_type,
                        'date_time_str': date_time_str,
                        'email': email
                    }
                    
                    # Remember user info for future bookings
                    st.session_state.user_email = email
                    st.session_state.user_preferences = {
                        'last_truck_type': truck_type,
                        'email': email
                    }
                    
                    print(f"DEBUG: Stored booking data: {st.session_state.booking_data}")
                    
                    # Remove OAuth generation
                    
                    # Create simple Google Calendar link (no OAuth needed)
                    from datetime import datetime, timedelta
                    from urllib.parse import quote
                    
                    print(f"DEBUG: Starting date parsing for: '{date_time_str}'")
                    
                    # Parse date for calendar link
                    now = datetime.now()
                    print(f"DEBUG: Current datetime: {now.strftime('%Y-%m-%d %H:%M')}")
                    
                    if 'tomorrow' in date_time_str.lower():
                        target_date = now + timedelta(days=1)
                        print(f"DEBUG: Detected 'tomorrow', setting to: {target_date.strftime('%Y-%m-%d')}")
                    elif '2 days' in date_time_str.lower() or 'two days' in date_time_str.lower():
                        target_date = now + timedelta(days=2)
                        print(f"DEBUG: Detected '2 days', setting to: {target_date.strftime('%Y-%m-%d')}")
                    elif '3 days' in date_time_str.lower() or 'three days' in date_time_str.lower():
                        target_date = now + timedelta(days=3)
                    elif '20th' in date_time_str.lower() or '20' in date_time_str:
                        # For 20th of current month
                        target_date = now.replace(day=20)
                        if target_date < now:  # If 20th already passed, next month
                            if now.month == 12:
                                target_date = target_date.replace(year=now.year + 1, month=1)
                            else:
                                target_date = target_date.replace(month=now.month + 1)
                    else:
                        target_date = now + timedelta(days=1)  # default tomorrow
                    
                    # Parse time - remove hardcoded default
                    hour = None
                    if '1 pm' in date_time_str.lower() or '1pm' in date_time_str.lower():
                        hour = 13
                    elif '2 pm' in date_time_str.lower() or '2pm' in date_time_str.lower():
                        hour = 14
                    elif '3 pm' in date_time_str.lower() or '3pm' in date_time_str.lower():
                        hour = 15
                    elif '4 pm' in date_time_str.lower() or '4pm' in date_time_str.lower():
                        hour = 16
                    elif '5 pm' in date_time_str.lower() or '5pm' in date_time_str.lower():
                        hour = 17
                    elif '9 am' in date_time_str.lower() or '9am' in date_time_str.lower():
                        hour = 9
                    elif '10 am' in date_time_str.lower() or '10am' in date_time_str.lower():
                        hour = 10
                    elif '11 am' in date_time_str.lower() or '11am' in date_time_str.lower():
                        hour = 11
                    elif '12 pm' in date_time_str.lower() or '12pm' in date_time_str.lower():
                        hour = 12
                    
                    if hour is None:
                        hour = 14  # only default if no time found
                    
                    print(f"DEBUG: Time parsing - Input: '{date_time_str}', Extracted hour: {hour}")
                    
                    start_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    print(f"DEBUG: Final parsed datetime: {start_time.strftime('%Y-%m-%d %H:%M')}")
                    
                    end_time = start_time + timedelta(hours=1)
                    
                    print(f"DEBUG: Calendar will show: {start_time.strftime('%B %d, %Y at %I:%M %p')}")
                    
                    # Create Google Calendar link that auto-fills user's calendar
                    title = f"Stephex Horse Trucks - {truck_type}"
                    details = f"Consultation with Stephex Horse Trucks\nContact: {email}\nSales: Tom Kerkhofs +32 478 44 76 63 or Dimitri Engels +32 470 10 13 40"
                    location = "Stephex Horse Trucks Showroom"
                    
                    calendar_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(title)}&dates={start_time.strftime('%Y%m%dT%H%M%S')}/{end_time.strftime('%Y%m%dT%H%M%S')}&details={quote(details)}&location={quote(location)}"
                    
                    formatted_date = start_time.strftime('%B %d, %Y at %I:%M %p')
                    print(f"DEBUG: Final display: {formatted_date}")
                    
                    return f"Perfect! Your appointment is ready:\n\n📋 **Appointment Details:**\n• **Service:** {truck_type}\n• **Date & Time:** {formatted_date}\n• **Contact:** {email}\n\nClick below to add this to your Google Calendar:\n\n<a href='{calendar_url}' target='_blank' style='background: #007bff; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;'>📅 Add to My Calendar</a>\n\nOur team will contact you to confirm details."
                
                except Exception as e:
                    print(f"DEBUG: Error in date parsing: {e}")
                    return f"I've noted your appointment request. Our sales team will contact you at {parts[2] if len(parts) > 2 else 'your email'} to schedule the appointment. Contact: Tom Kerkhofs +32 478 44 76 63"
            
            return response
        
        # Use AI for everything else
        context = {
            'knowledge_base': self.knowledge_base,
            'user_message': user_message
        }
        response = ai_service.generate_response(user_message, context, language)
        
        return response

# Global chatbot engine instance
chatbot_engine = ChatbotEngine()