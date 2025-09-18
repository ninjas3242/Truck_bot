"""
Main Streamlit application for Truck Sales Chatbot
"""
import streamlit as st
import time
import sys
import os
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Import after path setup
from src.components.ui_components import ui
from src.components.chatbot_engine import chatbot_engine
from src.utils.chat_utils import chat_session
from src.utils.language_manager import language_manager
from src.config.settings import get_settings
from src.core.logger import app_logger
from src.core.exceptions import ChatbotError

settings = get_settings()

# Page configuration
st.set_page_config(
    page_title=settings.app_title,
    page_icon=settings.app_icon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://stephexhorsetrucks.com/contact',
        'Report a bug': 'https://stephexhorsetrucks.com/support',
        'About': 'AI-powered chatbot for Stephex Horse Trucks'
    }
)

def main():
    """Main application function with comprehensive error handling"""
    
    # Handle OAuth callback first
    query_params = st.query_params
    if 'code' in query_params:
        from src.utils.calendar_service import calendar_service
        auth_code = query_params['code']
        access_token = calendar_service.handle_oauth_callback(auth_code)
        if access_token:
            # Create the actual calendar event
            event_created = calendar_service.create_appointment_from_session()
            if event_created:
                st.success("✅ Appointment booked successfully! Check your Google Calendar.")
                # Clear booking data
                if 'booking_data' in st.session_state:
                    del st.session_state.booking_data
                if 'booking_step' in st.session_state:
                    del st.session_state.booking_step
            else:
                st.error("❌ Failed to create calendar event")
        else:
            st.error("❌ Failed to connect Google Calendar")
        # Clear URL parameters
        st.query_params.clear()
        st.rerun()
    
    try:
        # Initialize logging
        app_logger.info("Starting Stephex Horse Trucks Chatbot")
        
        # Load custom CSS
        ui.load_custom_css()
        
        # Check system health
        _check_system_health()
        
    except Exception as e:
        app_logger.error(f"Initialization error: {e}")
        st.error(f"⚠️ System initialization error. Please refresh the page.")
        return
    
    # Render header
    ui.render_header()
    
    # Sidebar components
    with st.sidebar:
        # Language selector with auto-detection and error handling
        auto_detected = st.session_state.get('auto_detected_language', 'en')
        try:
            selected_language = ui.render_language_selector(auto_detected)
        except Exception as e:
            app_logger.error(f"Language selector error: {e}")
            selected_language = 'en'
        
        # Quick actions
        quick_action = ui.render_quick_actions(selected_language)
        
        # Sidebar info
        ui.render_sidebar_info()
        
        # Footer in sidebar
        ui.render_footer()
    
    # Main chat interface - use the UI component that handles images
    ui.render_chat_interface(selected_language)
    
    # Input area
    user_input, send_clicked, clear_clicked = ui.render_input_area(selected_language)
    
    # Handle clear chat
    if clear_clicked:
        chat_session.clear_history()
        st.rerun()
    
    # Handle quick actions
    if quick_action:
        user_input = quick_action
        send_clicked = True
    
    # Handle user input
    if send_clicked and user_input.strip():
        try:
            # Validate input
            if len(user_input.strip()) > 500:
                st.error("❌ Message too long. Please keep it under 500 characters.")
                return
            
            # Add user message to chat immediately
            chat_session.add_message(user_input.strip(), is_user=True)
            app_logger.info(f"User message: {user_input[:50]}...")
            
            # Rerun to show user message immediately
            st.rerun()
            
        except Exception as e:
            app_logger.error(f"Unexpected error: {e}")
            st.error("❌ Something went wrong. Please refresh and try again.")
    
    # Generate AI response if there's a new user message without response
    chat_history = chat_session.get_history()
    if chat_history and chat_history[-1].is_user:
        # Check if last message needs a response
        if len(chat_history) == 1 or not chat_history[-2].is_user:
            try:
                # Show typing indicator
                typing_placeholder = st.empty()
                with typing_placeholder:
                    ui.render_typing_indicator()
                
                # Generate bot response
                bot_response = chatbot_engine.process_message(chat_history[-1].content, selected_language)
                chat_session.add_message(bot_response, is_user=False)
                app_logger.info(f"Bot response generated successfully")
                
                # Clear typing indicator and rerun
                typing_placeholder.empty()
                st.rerun()
                
            except Exception as e:
                app_logger.error(f"Bot response error: {e}")
                error_msg = language_manager.get_text("error_message", selected_language)
                chat_session.add_message(error_msg, is_user=False)
                typing_placeholder.empty()
                st.rerun()
    
    # Handle empty input submission
    elif send_clicked and not user_input.strip():
        ui.show_error_message("Please enter a message before sending.")
    
    # Auto-scroll to bottom
    st.markdown("""
    <script>
    setTimeout(function() {
        window.scrollTo(0, document.body.scrollHeight);
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # Fix for arrow symbol display issues
    st.markdown("""
    <style>
    /* Hide all Material Design icons and symbols */
    .material-icons, .material-symbols-outlined, .material-symbols {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Fix keyboard_double_arrow_right specifically */
    *:contains("keyboard_double_arrow_right") {
        font-size: 0 !important;
    }
    
    /* Replace with proper arrow */
    button[kind="primary"]::after {
        content: "→" !important;
        font-family: Arial, sans-serif !important;
        margin-left: 5px;
    }
    
    /* Hide text content that shows keyboard_double_arrow_right */
    button span:contains("keyboard_double_arrow_right") {
        display: none !important;
    }
    
    /* General fix for any element containing this text */
    *[title*="keyboard_double_arrow_right"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables with validation"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.chat_history = []
        st.session_state.user_context = {}
        st.session_state.session_id = f"session_{int(time.time())}"
        
        # Auto-detect language from IP with better error handling
        st.session_state.auto_detected_language = 'en'  # Default
        try:
            from src.utils.geolocation import detect_language_from_ip
            detected_language = detect_language_from_ip()
            if detected_language:
                st.session_state.auto_detected_language = detected_language
                app_logger.info(f"Auto-detected language: {detected_language}")
        except ImportError:
            app_logger.warning("Geolocation module not available")
        except Exception as e:
            app_logger.warning(f"Language detection failed: {e}")
        
        app_logger.info(f"New session initialized: {st.session_state.session_id}")

def _check_system_health():
    """Check system health and dependencies"""
    try:
        # Check AI service
        from src.utils.ai_service import ai_service
        if settings.use_ai and not ai_service.model:
            app_logger.warning("AI service not available, using fallback mode")
        
        # Check data integrity
        if not chatbot_engine.knowledge_base:
            app_logger.warning("No knowledge base data available")
        
        app_logger.info("System health check completed")
        
    except Exception as e:
        app_logger.error(f"System health check failed: {e}")
        raise ChatbotError(f"System health check failed: {e}")

if __name__ == "__main__":
    try:
        # Initialize session state
        initialize_session_state()
        
        # Run main application
        main()
        
    except Exception as e:
        app_logger.critical(f"Application startup failed: {e}")
        st.error("❌ Application failed to start. Please contact support.")
        if settings.debug:
            st.exception(e)