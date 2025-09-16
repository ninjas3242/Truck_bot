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
        self.trucks_df = self._load_trucks_data()
        self.company_df = self._load_company_data()
    
    def _load_trucks_data(self):
        """Load truck data from CSV files"""
        try:
            # Load new trucks
            new_trucks_path = Path(__file__).parent.parent.parent / "data" / "new_trucks.csv"
            new_trucks = pd.read_csv(new_trucks_path)
            new_trucks['condition'] = 'New'
            
            # Load used trucks  
            used_trucks_path = Path(__file__).parent.parent.parent / "data" / "used_trucks.csv"
            used_trucks = pd.read_csv(used_trucks_path)
            used_trucks['condition'] = 'Used'
            
            # Combine both datasets
            all_trucks = pd.concat([new_trucks, used_trucks], ignore_index=True)
            return all_trucks
        except Exception as e:
            print(f"Error loading truck data: {e}")
            return pd.DataFrame()
    
    def _load_company_data(self):
        """Load company data from CSV"""
        try:
            csv_path = Path(__file__).parent.parent.parent / "data" / "company_data.csv"
            return pd.read_csv(csv_path)
        except Exception as e:
            print(f"Error loading company data: {e}")
            return pd.DataFrame()
    
    def process_message(self, user_message: str, language: str = "en") -> str:
        """Process user message and generate appropriate response"""
        
        # Only handle greetings
        if any(word in user_message.lower() for word in ["hi", "hello", "hey"]) and len(user_message.split()) <= 2:
            return "👋 Welcome to Stephex Horse Trucks! I'm your AI assistant specializing in premium horse transportation solutions. I can help you find the perfect truck, provide pricing information, arrange test drives, and answer any questions about our inventory. What can I assist you with today?"
        
        # Everything else goes to Gemini AI
        context = {
            'trucks_data': self.trucks_df.to_dict('records'),
            'company_data': self.company_df.to_dict('records'),
            'user_message': user_message
        }
        return ai_service.generate_response(user_message, context, language)

# Global chatbot engine instance
chatbot_engine = ChatbotEngine()