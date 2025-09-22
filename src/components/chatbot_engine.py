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
            
            # Extract specific time
            time_match = re.search(r'(\d{1,2})\s*(am|pm)', message_lower)
            if time_match:
                time_info += f' {time_match.group()}'
            
            # Extract location/timezone
            if 'london' in message_lower:
                time_info += ' london'
            
            print(f"DEBUG: Direct booking - Email: {email}, Time: {time_info}")
            
            # If we have enough info, create booking directly
            if email and time_info:
                try:
                    import streamlit as st
                    from datetime import datetime, timedelta
                    from urllib.parse import quote
                    
                    print(f"DEBUG: Direct booking processing - Email: {email}, Time: {time_info}")
                    
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
                        
                        # Parse date
                        now = datetime.now()
                        
                        if 'tomorrow' in date_time_str.lower():
                            target_date = now + timedelta(days=1)
                        elif '2 days' in date_time_str.lower():
                            target_date = now + timedelta(days=2)
                        elif '20th' in date_time_str.lower() or ' 20 ' in date_time_str:
                            target_date = now.replace(day=20)
                            if target_date < now:
                                if now.month == 12:
                                    target_date = target_date.replace(year=now.year + 1, month=1)
                                else:
                                    target_date = target_date.replace(month=now.month + 1)
                        else:
                            target_date = now + timedelta(days=1)
                        
                    # Parse time from user input
                    hour = 14  # default
                    if '1 am' in date_time_str.lower():
                        hour = 1
                    elif '2 am' in date_time_str.lower():
                        hour = 2
                    elif '3 am' in date_time_str.lower():
                        hour = 3
                    elif '4 am' in date_time_str.lower():
                        hour = 4
                    elif '5 am' in date_time_str.lower():
                        hour = 5
                    elif '6 am' in date_time_str.lower():
                        hour = 6
                    elif '7 am' in date_time_str.lower():
                        hour = 7
                    elif '8 am' in date_time_str.lower():
                        hour = 8
                    elif '9 am' in date_time_str.lower():
                        hour = 9
                    elif '10 am' in date_time_str.lower():
                        hour = 10
                    elif '11 am' in date_time_str.lower():
                        hour = 11
                    elif '12 pm' in date_time_str.lower():
                        hour = 12
                    elif '1 pm' in date_time_str.lower():
                        hour = 13
                    elif '2 pm' in date_time_str.lower():
                        hour = 14
                    elif '3 pm' in date_time_str.lower():
                        hour = 15
                    elif '4 pm' in date_time_str.lower():
                        hour = 16
                    elif '5 pm' in date_time_str.lower():
                        hour = 17
                    elif '6 pm' in date_time_str.lower():
                        hour = 18
                        
                        start_time = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                        end_time = start_time + timedelta(hours=1)
                        
                        # Create calendar link
                        title = f"Stephex Horse Trucks - {truck_type}"
                        details = f"Consultation with Stephex Horse Trucks\nContact: {email}"
                        location = "Stephex Horse Trucks Showroom"
                        
                        calendar_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={quote(title)}&dates={start_time.strftime('%Y%m%dT%H%M%S')}/{end_time.strftime('%Y%m%dT%H%M%S')}&details={quote(details)}&location={quote(location)}"
                        
                        formatted_date = start_time.strftime('%B %d, %Y at %I:%M %p')
                        
                    return f"Perfect! Your appointment is ready:\n\n📋 **Appointment Details:**\n• **Service:** {truck_type}\n• **Date & Time:** {formatted_date}\n• **Contact:** {email}\n\n<a href='{calendar_url}' target='_blank' style='background: #007bff; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;'>📅 Add to Google Calendar</a>\n\nOur team will contact you to confirm details."
                    
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