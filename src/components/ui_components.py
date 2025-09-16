"""
UI Components for the chatbot interface
"""
import streamlit as st
from typing import List, Dict, Any, Optional
import time
from functools import lru_cache

try:
    from ..config.settings import SUPPORTED_LANGUAGES, COLORS, BOT_NAME, BOT_AVATAR, USER_AVATAR, get_settings
    settings = get_settings()
except ImportError:
    # Fallback for development
    SUPPORTED_LANGUAGES = {"en": "English", "es": "Español", "fr": "Français", "it": "Italiano", "nl": "Nederlands"}
    COLORS = {"primary": "#1f2937"}
    BOT_NAME = "TruckBot"
    BOT_AVATAR = "🤖"
    USER_AVATAR = "👤"
    settings = None
from ..utils.language_manager import language_manager
from ..utils.chat_utils import chat_session
try:
    from ..core.logger import app_logger
    from ..core.exceptions import ValidationError
except ImportError:
    # Fallback for development
    import logging
    app_logger = logging.getLogger(__name__)
    class ValidationError(Exception):
        pass

class UIComponents:
    
    @staticmethod
    @lru_cache(maxsize=1)
    def load_custom_css():
        """Load custom CSS styling with caching and error handling"""
        try:
            with open("assets/css/style.css", "r", encoding="utf-8") as f:
                css_content = f.read()
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
                app_logger.debug("Custom CSS loaded successfully")
        except FileNotFoundError:
            app_logger.warning("Custom CSS file not found, using default styling")
            st.warning("⚠️ Custom styling not available")
        except Exception as e:
            app_logger.error(f"Error loading CSS: {e}")
            st.error("❌ Error loading custom styling")
    
    @staticmethod
    def render_header():
        """Render the main header with improved accessibility"""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            box-shadow: 0 16px 32px rgba(0, 0, 0, 0.2);
            position: relative;
            overflow: hidden;
        " role="banner">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;" aria-label="Stephex Horse Trucks">
                🚛 Stephex Horse Trucks
            </h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;" role="doc-subtitle">
                ✨ Your AI Assistant for Premium Horse Transportation ✨
            </p>
            <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;">
                🌍 Serving customers worldwide | 📞 24/7 AI Support | ⚙️ Custom Solutions
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_language_selector() -> str:
        """Render language selector and return selected language"""
        st.sidebar.markdown("""
        <div class="language-selector">
            <h3>🌐 Language / Idioma</h3>
        </div>
        """, unsafe_allow_html=True)
        
        selected_language = st.sidebar.selectbox(
            "Select Language:",
            options=list(SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: f"{SUPPORTED_LANGUAGES[x]} ({x.upper()})",
            key="language_selector"
        )
        
        return selected_language
    
    @staticmethod
    def render_quick_actions(language: str) -> str:
        """Render quick action buttons and return selected action"""
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        quick_actions = {
            "new_trucks": language_manager.get_text("new_trucks", language),
            "used_trucks": language_manager.get_text("used_trucks", language),
            "financing": language_manager.get_text("financing", language),
            "contact": language_manager.get_text("contact", language)
        }
        
        # Language-specific queries
        queries = {
            "en": {
                "new_trucks": "Show me new trucks available",
                "used_trucks": "Show me used trucks available", 
                "financing": "Tell me about financing options",
                "contact": "I want to contact you"
            },
            "es": {
                "new_trucks": "Muéstrame camiones nuevos disponibles",
                "used_trucks": "Muéstrame camiones usados disponibles",
                "financing": "Cuéntame sobre las opciones de financiamiento", 
                "contact": "Quiero contactarte"
            },
            "fr": {
                "new_trucks": "Montrez-moi les nouveaux camions disponibles",
                "used_trucks": "Montrez-moi les camions d'occasion disponibles",
                "financing": "Parlez-moi des options de financement",
                "contact": "Je veux vous contacter"
            },
            "it": {
                "new_trucks": "Mostrami i camion nuovi disponibili",
                "used_trucks": "Mostrami i camion usati disponibili", 
                "financing": "Dimmi delle opzioni di finanziamento",
                "contact": "Voglio contattarti"
            },
            "nl": {
                "new_trucks": "Toon me nieuwe beschikbare vrachtwagens",
                "used_trucks": "Toon me gebruikte beschikbare vrachtwagens",
                "financing": "Vertel me over financieringsopties",
                "contact": "Ik wil contact met je opnemen"
            }
        }
        
        selected_action = None
        cols = st.sidebar.columns(2)
        
        with cols[0]:
            if st.button(quick_actions["new_trucks"], key="new_trucks_btn"):
                selected_action = queries.get(language, queries["en"])["new_trucks"]
            if st.button(quick_actions["financing"], key="financing_btn"):
                selected_action = queries.get(language, queries["en"])["financing"]
        
        with cols[1]:
            if st.button(quick_actions["used_trucks"], key="used_trucks_btn"):
                selected_action = queries.get(language, queries["en"])["used_trucks"]
            if st.button(quick_actions["contact"], key="contact_btn"):
                selected_action = queries.get(language, queries["en"])["contact"]
        
        return selected_action
    
    @staticmethod
    def render_chat_interface(language: str):
        """Render the main chat interface"""
        # Chat container with proper styling
        st.markdown("""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            border: 1px solid #e5e7eb;
            margin-bottom: 2rem;
            min-height: 400px;
            max-height: 600px;
            overflow-y: auto;
        ">
        """, unsafe_allow_html=True)
        
        # Display chat history
        chat_history = chat_session.get_history()
        
        if not chat_history:
            # Show welcome message
            welcome_msg = language_manager.get_text("welcome", language)
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #ffffff, #f8fafc);
                color: #2c3e50;
                padding: 1.2rem 1.8rem;
                border-radius: 25px 25px 25px 8px;
                margin: 0.8rem 0;
                margin-right: 15%;
                border-left: 4px solid #00d4aa;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                word-wrap: break-word;
                max-width: 75%;
                position: relative;
            ">
                <strong>🤖 {BOT_NAME}:</strong> {welcome_msg}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display chat messages
            for msg in chat_history:
                if msg.is_user:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        color: white;
                        padding: 1.2rem 1.8rem;
                        border-radius: 25px 25px 8px 25px;
                        margin: 0.8rem 0;
                        margin-left: 15%;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                        word-wrap: break-word;
                        max-width: 75%;
                        position: relative;
                    ">
                        <strong>👤 You:</strong> {msg.content}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #ffffff, #f8fafc);
                        color: #2c3e50;
                        padding: 1.2rem 1.8rem;
                        border-radius: 25px 25px 25px 8px;
                        margin: 0.8rem 0;
                        margin-right: 15%;
                        border-left: 4px solid #00d4aa;
                        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                        word-wrap: break-word;
                        max-width: 75%;
                        position: relative;
                    ">
                        <strong>🤖 {BOT_NAME}:</strong> {msg.content}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_typing_indicator():
        """Show typing indicator"""
        st.markdown("""
        <div class="typing-indicator">
            <span>TruckBot is typing</span>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_input_area(language: str) -> tuple:
        """Render input area with validation and accessibility"""
        st.markdown("---")
        
        # Chat input with integrated send button
        user_input = st.chat_input(
            placeholder=language_manager.get_text("chat_placeholder", language),
            key="chat_input",
            max_chars=500
        )
        
        # Clear button in sidebar or separate area
        col1, col2 = st.columns([4, 1])
        with col2:
            clear_clicked = st.button(
                language_manager.get_text("clear_chat", language),
                key="clear_btn",
                help="Clear chat history"
            )
        
        # Check if user pressed enter or sent message
        send_clicked = bool(user_input)
        
        return user_input or "", send_clicked, clear_clicked
    
    @staticmethod
    def render_sidebar_info():
        """Render additional information in sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Chat Statistics")
        
        chat_history = chat_session.get_history()
        user_messages = len([msg for msg in chat_history if msg.is_user])
        bot_messages = len([msg for msg in chat_history if not msg.is_user])
        
        st.sidebar.metric("Your Messages", user_messages)
        st.sidebar.metric("Bot Responses", bot_messages)
        
        # User context info
        user_context = st.session_state.get("user_context", {})
        if user_context:
            st.sidebar.markdown("### 🎯 Your Preferences")
            if "budget" in user_context:
                st.sidebar.write(f"💰 Budget: ${user_context['budget']:,}")
            if "truck_preference" in user_context:
                st.sidebar.write(f"🚛 Preference: {user_context['truck_preference'].title()}")
    
    @staticmethod
    def render_footer():
        """Render footer information"""
        st.markdown("---")
        st.markdown("""
        <div style="
            text-align: center;
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            padding: 2rem;
            border-radius: 16px;
            margin-top: 2rem;
            border: 1px solid #e1e8ed;
        ">
            <p style="margin: 0 0 0.5rem 0; font-size: 1.1rem; font-weight: 600; color: #2c3e50;">
                🚛 <strong>Stephex Horse Trucks</strong> - Premium Horse Transportation Solutions
            </p>
            <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">
                Powered by AI • Built with ❤️ for better customer experience
            </p>
            <div style="margin-top: 1rem; font-size: 0.8rem; color: #9ca3af;">
                © 2024 Stephex Horse Trucks | 🌍 Global Shipping Available
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_success_message(message: str):
        """Show success message"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def show_error_message(message: str):
        """Show error message"""
        st.error(f"❌ {message}")
    
    @staticmethod
    def show_info_message(message: str):
        """Show info message"""
        st.info(f"ℹ️ {message}")

# Global UI components instance
ui = UIComponents()