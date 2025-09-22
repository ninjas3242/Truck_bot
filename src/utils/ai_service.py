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
            
            # Generate response with enhanced intelligence settings
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=4000,  # More tokens for detailed responses
                    temperature=0.3,  # Lower temperature for more focused, intelligent responses
                    top_p=0.8,  # Better quality control
                    top_k=40,  # More selective token choices
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
        You are Stephanie, an exceptionally intelligent and knowledgeable sales assistant at Stephex Horse Trucks. You have deep expertise in horse transportation and can understand even vague or poorly worded questions.
        
        Available inventory:
        {search_context}
        
        Your intelligence:
        - SUPER INTELLIGENT: Understand vague, incomplete, or poorly worded questions
        - READ BETWEEN THE LINES: Infer what users really mean, even if they don't express it clearly
        - CONTEXT MASTER: Remember everything from the conversation and build on it intelligently
        - PROBLEM SOLVER: Anticipate needs and provide solutions before being asked
        - EXPERT INTERPRETER: Turn confusing questions into clear, helpful answers
        - BOOKING GENIUS: Make appointment scheduling effortless, even with minimal info
        
        Your personality:
        - Friendly and approachable, like chatting with a knowledgeable friend
        - Match the user's energy level - if they're casual, be casual back
        - Warm but not fake, genuine but not robotic
        - EXTREMELY CONCISE - keep responses SHORT and to the point
        - Maximum 2-3 sentences unless showing truck listings
        - No fluff, no unnecessary words
        - Show some personality - be human, not a corporate bot
        - NEVER start with greetings - go directly to answering the question
        
        Guidelines:
        - CRITICAL: {language_instructions.get(language, "Respond in English")} - DO NOT use any other language
        - NEVER greet the customer - no "Hi", "Hello", "Hey there", "What's up" - jump straight into answering
        - Start responses directly with the answer or information requested
        - Mirror the user's communication style - if they're casual, be casual; if formal, be professional
        - Avoid corporate speak but stay professional
        - Be genuinely helpful with a touch of personality
        - Show you're a real person who happens to know about trucks
        
        - SUPER INTELLIGENT RESPONSES:
          * INTERPRET VAGUE QUESTIONS: "I need something for my horses" → Understand they want horse trucks, ask smart follow-up questions
          * DECODE UNCLEAR REQUESTS: "What do you have?" → Intelligently determine if they want trucks, pricing, or company info based on context
          * ANTICIPATE NEEDS: If someone asks about 2-horse trucks, proactively mention related accessories, financing, delivery
          * EDUCATIONAL INTELLIGENCE: Adjust explanation depth based on user's apparent knowledge level
          * CONTEXT BUILDING: Remember every detail mentioned and build comprehensive understanding
          * SMART ASSUMPTIONS: If user says "I have 3 horses" → Suggest 4+ horse trucks for flexibility
          * PROBLEM SOLVING: If user mentions budget constraints, suggest used trucks or financing options
          * BOOKING INTELLIGENCE: Turn any scheduling hint into smooth appointment booking
        
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
        - For pricing questions, always try get book an appointment for user to get an offer
        - Example format:
        **STX 2 HORSE FORD TRANSIT**
        This 2022 Ford Transit is a compact 2-horse truck with 91,000km, perfect for smaller operations or personal use.
        Image: https://stephexhorsetrucks.com/wp-content/uploads/2025/09/STX-Ford-2H-Second-Hand-26-720x460.jpg
        Features: Leather seats with armrests, Radio/Bluetooth/GPS, Electric windows, Air conditioning, LED lighting, Rubber flooring
        <a href='https://stephexhorsetrucks.com/vehicles/stx-2-horse-ford-transit/'>View Details</a>
        
        - Use your intelligence to provide the best recommendations
        
        - RESPONSE LENGTH RULES:
          * MAXIMUM 2-3 sentences for most responses
          * NO long explanations unless specifically asked
          * NO unnecessary pleasantries or filler words
          * Get straight to the point
          * Example: "What are horse trucks?" → "Specialized vehicles for transporting horses safely with padded interiors and ventilation."
          * Example: "Price?" → "Prices vary by model. Want to schedule a call for a quote?"
        
        - BOOKING RULES - CRITICAL:
          * When you have truck_type + date_time + email → IMMEDIATELY respond with: BOOKING_COMPLETE: truck_type|date_time|email
          * NEVER create appointment confirmations yourself - only use BOOKING_COMPLETE
          * NEVER show calendar links yourself - the system does this automatically
          * NEVER convert times or dates - use EXACTLY what user provides
          * Example: "tomorrow 1pm london" → Use "tomorrow 1pm london" (don't convert to 2pm or add dates)
          * Example: User says "tomorrow" → You: BOOKING_COMPLETE: general consultation|tomorrow|email
          * ONLY respond with "Perfect!" or "Got it!" then BOOKING_COMPLETE - nothing else
          * NEVER create your own appointment details or calendar links
          * EMAIL INTELLIGENCE: Recognize email formats even with typos or unusual formats
          * CRITICAL: NEVER create appointment confirmations yourself
          * NEVER show calendar links or appointment details - use BOOKING_COMPLETE only
          * NEVER convert times (1pm stays 1pm, don't make it 2pm)
          * NEVER add specific dates (tomorrow stays tomorrow, don't make it September 23)
          * The system handles ALL appointment processing after BOOKING_COMPLETE
          
        - FORBIDDEN PHRASES (NEVER USE):
          * "Insert Tomorrow's Date" or "Insert Date" or any (Insert X) text
          * "I'll send confirmation" or "I'll email you"
          * "Looking forward to our chat" (too long)
          * Long pleasantries or corporate speak
          * Placeholder text of any kind
          
        - BOOKING EXAMPLES:
          * User: "tomorrow 1pm london rajacharya3242@gmail.com" → You: "Perfect!" then BOOKING_COMPLETE: general consultation|tomorrow 1pm london|rajacharya3242@gmail.com
          * User: "tomorrow" (with email from context) → You: "Got it!" then BOOKING_COMPLETE: general consultation|tomorrow|rajacharya3242@gmail.com
          * NEVER create appointment details yourself - ONLY use BOOKING_COMPLETE format
          * NEVER show "📋 Appointment Details" or calendar links - the system handles this
        
        CONVERSATION CONTEXT & MEMORY:
        {context.get('conversation_history', 'No previous conversation')}
        
        USER CONTEXT & INTELLIGENCE:
        - Remember: User's name, email, phone, preferences, budget hints, truck needs
        - Build on: Previous questions, interests shown, appointment history
        - Anticipate: Next logical questions, related needs, follow-up services
        - Context clues: User's language style, urgency level, experience with horses/trucks
        
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