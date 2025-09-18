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
            context = {
                'knowledge_base': self.knowledge_base,
                'user_message': user_message,
                'booking_mode': True
            }
            return ai_service.generate_response(user_message, context, language)
        
        # Use AI for everything else
        context = {
            'knowledge_base': self.knowledge_base,
            'user_message': user_message
        }
        response = ai_service.generate_response(user_message, context, language)
        
        return response

# Global chatbot engine instance
chatbot_engine = ChatbotEngine()