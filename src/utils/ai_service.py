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
            print(f"DEBUG: Context keys: {list(context.keys())}")
            # This debug was moved to after search
            
            # Generate response with safety settings
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=3000,
                    temperature=0.6,
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            )
            
            result = response.text.strip()
            print(f"DEBUG: AI Response length: {len(result)} characters")
            print(f"DEBUG: AI Response preview: {result[:200]}...")
            return result
            
        except Exception as e:
            print(f"DEBUG: AI Error: {str(e)}")
            app_logger.error(f"AI Service Error: {e}")
            return f"AI Error: {str(e)[:100]}... Please check your API key and try again."
    
    def _create_prompt(self, user_message: str, context: Dict[str, Any], language: str) -> str:
        """Create context-aware prompt for Gemini"""
        
        search_context = "AVAILABLE TRUCKS:\n"
        
        try:
            # Smart search for relevant content
            from ..utils.smart_search import search_knowledge
            # Increase results for truck queries
            max_results = 8 if any(word in user_message.lower() for word in ['truck', '5', 'suggest', 'list']) else 3
            results = search_knowledge(user_message, max_results=max_results)
            
            print(f"DEBUG: Found {len(results)} search results")
            print(f"DEBUG: Truck results: {[r['type'] for r in results if r.get('type') == 'truck']}")
            
            for item in results:
                if item.get('type') == 'truck':
                    search_context += f"TRUCK: {item['title']}"
                    search_context += f" | Capacity: {item.get('capacity', '')}"
                    search_context += f" | Condition: {item.get('condition', '')}"
                    if item.get('year'):
                        search_context += f" | Year: {item['year']}"
                    if item.get('features'):
                        search_context += f" | Features: {item['features']}"
                    if item.get('image_url'):
                        search_context += f" | Image: {item['image_url']}"
                    if item.get('url'):
                        search_context += f" | Details: {item['url']}"
                    search_context += "\n"
                elif item.get('type') == 'dealer':
                    search_context += f"DEALER: {item['title']}: {item['content']}\n"
                    
        except Exception as e:
            print(f"DEBUG: Search error: {e}")
            search_context += "No trucks found in search\n"
        
        # ALWAYS respect user's language selection - NO auto-detection override
        print(f"DEBUG: Using user selected language: {language} (no auto-detection)")
        
        # Language-specific instructions (expanded)
        language_instructions = {
            "en": "Respond in English",
            "es": "Responde en español",
            "fr": "Répondez en français", 
            "it": "Rispondi in italiano",
            "nl": "Antwoord in het Nederlands",
            "da": "Svar på dansk",  # Danish
            "de": "Antworte auf Deutsch",  # German
            "sv": "Svara på svenska",  # Swedish
            "no": "Svar på norsk",  # Norwegian 
        }
        
        # Main prompt with explicit truck count
        truck_count = len([r for r in results if r.get('type') == 'truck'])
        
        prompt = f"""
        You are Stephanie, a friendly and knowledgeable sales assistant at Stephex Horse Trucks. You're passionate about helping customers find the perfect horse truck.
        
        Available inventory:
        {search_context}
        
        Your personality:
        - Friendly, enthusiastic, and genuinely helpful with hint of professionalism 
        - Smart and knowledgeable about trucks
        - Natural marketing tone (not pushy, just passionate about the products)
        - Fun to talk to and engaging
        - Professional but approachable
        
        Guidelines:
        - CRITICAL: {language_instructions.get(language, "Respond in English")} - DO NOT use any other language
        - Do not greet the customer as you have already greated them in the into message
        - Be smart about understanding what customers need
        - Give detailed, helpful information about trucks and the company
        - When showing trucks: Name, Image: [url], Features, <a href='[url]'>View Details</a>
        - For pricing questions, always provide contact info: Tom Kerkhofs +32 478 44 76 63 or Dimitri Engels +32 470 10 13 40
        - Use your intelligence to provide the best recommendations
        - BOOKING RULES: When user wants appointments, collect truck type, date/time, email
        - If user provides date/time + email (even without specific truck), respond with: BOOKING_COMPLETE: general consultation|date_time|email
        - Example: User says "meeting tomorrow 2pm, email@test.com" → Response: BOOKING_COMPLETE: general consultation|tomorrow 2pm|email@test.com
        - If missing info, ask clearly: "I need: [missing items]. Please provide them."
        - Keep booking responses short and direct
        - Don't be overly chatty or ask too many follow-up questions for bookings
        
        Customer: {user_message}
        
        Your response:
        """ 
        
        return prompt
    
    def _detect_language_from_text(self, text: str) -> Optional[str]:
        """Simple language detection from text patterns"""
        text_lower = text.lower()
        
        # Danish indicators
        danish_words = ['fortæl', 'mig', 'noget', 'om', 'din', 'virksomhed', 'jeg', 'vil', 'gerne', 'hvad', 'hvor', 'hvordan']
        if any(word in text_lower for word in danish_words):
            return 'da'
        
        # German indicators  
        german_words = ['ich', 'bin', 'das', 'ist', 'und', 'der', 'die', 'mit', 'für', 'von', 'auf', 'über', 'können', 'möchte']
        if any(word in text_lower for word in german_words):
            return 'de'
            
        # Swedish indicators
        swedish_words = ['jag', 'är', 'det', 'och', 'att', 'en', 'på', 'med', 'för', 'av', 'till', 'från', 'kan', 'vill']
        if any(word in text_lower for word in swedish_words):
            return 'sv'
            
        # Norwegian indicators
        norwegian_words = ['jeg', 'er', 'det', 'og', 'å', 'en', 'på', 'med', 'for', 'av', 'til', 'fra', 'kan', 'vil']
        if any(word in text_lower for word in norwegian_words):
            return 'no'
            
        # Dutch indicators
        dutch_words = ['kunt', 'mij', 'iets', 'vertellen', 'over', 'uw', 'bedrijf', 'ik', 'ben', 'het', 'en', 'van', 'met', 'voor', 'aan', 'op', 'kan', 'wil']
        if any(word in text_lower for word in dutch_words):
            return 'nl'
        
        return None

# Global AI service instance
ai_service = AIService()