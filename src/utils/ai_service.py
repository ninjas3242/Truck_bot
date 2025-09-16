"""
AI Service using Google Gemini for intelligent responses
"""
import google.generativeai as genai
from typing import Optional, Dict, Any
from ..config.settings import get_settings
from ..core.logger import app_logger

settings = get_settings()

class AIService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the AI model with error handling"""
        try:
            if not self.api_key:
                app_logger.error("Gemini API key not provided")
                return
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(settings.ai_model)
            app_logger.info(f"AI Service initialized successfully with model: {settings.ai_model}")
        except Exception as e:
            app_logger.error(f"AI Service initialization failed: {e}")
            self.model = None
    
    def generate_response(self, user_message: str, context: Dict[str, Any], language: str = "en") -> str:
        """Generate AI response using Gemini"""
        if not self.model:
            return "AI service not available. Model failed to initialize."
        
        try:
            # Create context-aware prompt
            prompt = self._create_prompt(user_message, context, language)
            print(f"DEBUG: Prompt length: {len(prompt)}")
            print(f"DEBUG: Trucks data count: {len(context.get('trucks_data', []))}")
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2000,
                    temperature=0.7,
                )
            )
            
            result = response.text.strip()
            print(f"DEBUG: AI Response: {result[:100]}...")
            return result
            
        except Exception as e:
            print(f"DEBUG: AI Error: {str(e)}")
            app_logger.error(f"AI Service Error: {e}")
            return f"AI Error: {str(e)[:100]}... Please check your API key and try again."
    
    def _create_prompt(self, user_message: str, context: Dict[str, Any], language: str) -> str:
        """Create context-aware prompt for Gemini"""
        
        # Get truck data from context
        trucks_data = context.get('trucks_data', [])
        company_data = context.get('company_data', [])
        
        # Build truck inventory context (simplified)
        truck_context = "TRUCKS:\n"
        for truck in trucks_data[:10]:  # Limit to first 10 trucks
            name = truck.get('Name', truck.get('name', 'Unknown'))
            condition = truck.get('condition', truck.get('Condition', 'Unknown'))
            horses = truck.get('Horses', truck.get('horses', truck.get('capacity', 'N/A')))
            
            truck_context += f"- {name} ({horses} horses, {condition})\n"
        
        # Build company context
        company_context = "COMPANY INFORMATION:\n"
        for item in company_data:
            if item.get('Category') == 'Contact':
                company_context += f"- {item['Title']}: {item['Description']}\n"
        
        # Language-specific instructions
        language_instructions = {
            "en": "Respond in English",
            "es": "Responde en español",
            "fr": "Répondez en français", 
            "it": "Rispondi in italiano",
            "nl": "Antwoord in het Nederlands"
        }
        
        # Main prompt (simplified)
        prompt = f"""
        You are Stephex Horse Trucks AI assistant.
        
        {truck_context}
        
        Rules:
        - {language_instructions.get(language, "Respond in English")}
        - Show truck details from the list above
        - For pricing say "Contact us for quote"
        - Be helpful and direct
        
        Question: {user_message}
        
        Answer:
        """
        
        return prompt

# Global AI service instance
ai_service = AIService()