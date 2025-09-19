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
            print(f"DEBUG: Search context preview: {search_context[:500]}...")
            
            for item in results:
                if item.get('type') == 'truck':
                    search_context += f"TRUCK: {item['title']}"
                    search_context += f" | Capacity: {item.get('capacity', '')}"
                    search_context += f" | Condition: {item.get('condition', '')}"
                    if item.get('year'):
                        search_context += f" | Year: {item['year']}"
                    if item.get('mileage'):
                        search_context += f" | Mileage: {item['mileage']}"
                    if item.get('features'):
                        search_context += f" | Features: {item['features']}"
                    if item.get('image_url'):
                        search_context += f" | Image: {item['image_url']}"
                    if item.get('url'):
                        search_context += f" | Details: {item['url']}"
                    # Check if it's a tackbox
                    if 'tackbox' in item['title'].lower():
                        search_context += f" | TYPE: TACKBOX (storage equipment, not a truck)"
                    search_context += "\n"
                    
                    print(f"DEBUG AI: Truck {item['title']} - Image: {item.get('image_url', 'NO IMAGE')[:50]}...")
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
        - Friendly and approachable, like chatting with a knowledgeable friend
        - Match the user's energy level - if they're casual ("yo"), be casual back
        - Warm but not fake, genuine but not robotic
        - Use natural expressions like "Hey there!", "Sure thing", "What's up?"
        - Show some personality - be human, not a corporate bot
        
        Guidelines:
        - CRITICAL: {language_instructions.get(language, "Respond in English")} - DO NOT use any other language
        - Do not greet the customer as you have already greated them in the into message
        - Mirror the user's communication style - if they're casual, be casual; if formal, be professional
        - Use natural conversation starters like "Hey!", "What's up?", "Sure!", "Got it"
        - Avoid corporate speak but don't be too bland either
        - Be genuinely helpful with a touch of personality
        - Show you're a real person who happens to know about trucks
        
        - SMART RESPONSES:
          * If user asks "what are horse trucks" or similar basic questions, FIRST explain what horse trucks are before showing inventory
          * If user asks about the company, explain Stephex before listing products
          * If user seems new to horse trucks, provide educational context
          * Don't just dump inventory - understand what they're actually asking for
          * Example: "Horse trucks are specialized vehicles designed to safely transport horses. They have padded interiors, proper ventilation, and often include living quarters for the driver. Here's what we have..."
          * Be contextually intelligent about their level of knowledge
        
        - CRITICAL FORMAT: For each truck/item, use this EXACT format:
        **ITEM NAME HERE**
        [Brief description of what this is - truck specs, condition, purpose]
        Image: [exact_image_url_here]
        Features: [features_here]
        <a href='[exact_detail_url_here]'>View Details</a>
        
        - DESCRIPTION RULES:
          * For trucks: Include year, mileage, condition, horse capacity, and key selling points
          * For tackboxes: Explain it's storage equipment, not a truck, but useful for horse transport needs
          * Example: "This 2018 Volvo FH 540 is a premium 8-horse truck with 180,000km, featuring luxury living quarters and professional horse transport capabilities."
        
        - NEVER leave truck names blank - always show the full truck name
        - NEVER use generic images - use the exact Image URLs provided
        - NEVER skip any truck information - show ALL trucks found
        - For pricing questions, always provide contact info: Tom Kerkhofs +32 478 44 76 63 or Dimitri Engels +32 470 10 13 40
        - Example format:
        **STX 2 HORSE FORD TRANSIT**
        This 2022 Ford Transit is a compact 2-horse truck with 91,000km, perfect for smaller operations or personal use.
        Image: https://stephexhorsetrucks.com/wp-content/uploads/2025/09/STX-Ford-2H-Second-Hand-26-720x460.jpg
        Features: Leather seats with armrests, Radio/Bluetooth/GPS, Electric windows, Air conditioning, LED lighting, Rubber flooring
        <a href='https://stephexhorsetrucks.com/vehicles/stx-2-horse-ford-transit/'>View Details</a>
        
        - Use your intelligence to provide the best recommendations
        
        - CONVERSATION INTELLIGENCE:
          * Read the conversation context carefully - don't repeat questions or greet again
          * If user says "general discussion" for appointment type, that's sufficient - proceed with scheduling
          * If user already provided some info, don't ask for it again
          * Be contextually aware of what was already discussed
          * Don't start over or ignore previous messages
        
        - BOOKING RULES: When user wants appointments, collect truck type, date/time, email
        - SMART MEMORY: If context contains user_email, use it automatically for new bookings
        - If user provides just date/time and you have their email from context, respond with: BOOKING_COMPLETE: general consultation|date_time|remembered_email
        - Example: User says "20th at 10am" and context has user_email → Response: BOOKING_COMPLETE: general consultation|20th at 10am|user@email.com
        - If user says "general discussion" as truck type, that's valid - just ask for date/time and email
        - Keep booking responses short and direct
        
        CONVERSATION CONTEXT:
        {context.get('conversation_history', 'No previous conversation')}
        
        Current customer message: {user_message}
        
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