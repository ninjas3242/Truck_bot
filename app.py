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
        # Language selector
        selected_language = ui.render_language_selector()
        
        # Quick actions
        quick_action = ui.render_quick_actions(selected_language)
        
        # Sidebar info
        ui.render_sidebar_info()
    
    # Main chat interface
    chat_history = chat_session.get_history()
    
    if not chat_history:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffffff, #f8fafc);
            color: #2c3e50;
            padding: 1.2rem 1.8rem;
            border-radius: 25px 25px 25px 8px;
            margin: 0.8rem 0;
            border-left: 4px solid #00d4aa;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
            max-width: 75%;
        ">
            <strong>🤖 TruckBot:</strong> 👋 Welcome to Stephex Horse Trucks! How can I help you today?
        
        """, unsafe_allow_html=True)
    else:
        for msg in chat_history:
            if msg.is_user:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 1.2rem 1.8rem;
                    border-radius: 25px 25px 8px 25px;
                    margin: 0.8rem 0 0.8rem auto;
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                    max-width: 75%;
                    margin-left: 25%;
                ">
                    <strong>👤 You:</strong> {msg.content}
                
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #ffffff, #f8fafc);
                    color: #2c3e50;
                    padding: 1.2rem 1.8rem;
                    border-radius: 25px 25px 25px 8px;
                    margin: 0.8rem 0;
                    border-left: 4px solid #00d4aa;
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
                    max-width: 75%;
                ">
                    <strong>🤖 TruckBot:</strong> {msg.content}
                
                """, unsafe_allow_html=True)
    
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
            
            # Add user message to chat
            chat_session.add_message(user_input.strip(), is_user=True)
            app_logger.info(f"User message: {user_input[:50]}...")
            
            # Show typing indicator (faster response)
            with st.empty():
                ui.render_typing_indicator()
                time.sleep(0.1)
            
            # Generate bot response
            bot_response = chatbot_engine.process_message(user_input.strip(), selected_language)
            chat_session.add_message(bot_response, is_user=False)
            app_logger.info(f"Bot response generated successfully")
            
        except ChatbotError as e:
            app_logger.error(f"Chatbot error: {e}")
            error_msg = language_manager.get_text("error_message", selected_language)
            chat_session.add_message(error_msg, is_user=False)
            st.error("⚠️ I encountered an issue. Please try again.")
        except Exception as e:
            app_logger.error(f"Unexpected error: {e}")
            error_msg = language_manager.get_text("error_message", selected_language)
            chat_session.add_message(error_msg, is_user=False)
            st.error("❌ Something went wrong. Please refresh and try again.")
        
        # Rerun to update chat display
        st.rerun()
    
    # Handle empty input submission
    elif send_clicked and not user_input.strip():
        ui.show_error_message("Please enter a message before sending.")
    
    # Footer with enhanced info
    ui.render_footer()
    
    # Fix for arrow symbol display issues
    st.markdown("""
    <style>
    /* Hide problematic Material Design icons */
    .material-icons, .material-symbols-outlined {
        display: none !important;
    }
    
    /* Fix for keyboard_double_arrow_right display */
    [data-testid*="arrow"], [class*="arrow"], [class*="keyboard"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Replace arrow symbols with proper Unicode */
    .stButton button::after {
        content: '' !important;
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
        app_logger.info(f"New session initialized: {st.session_state.session_id}")

def _check_system_health():
    """Check system health and dependencies"""
    try:
        # Check AI service
        from src.utils.ai_service import ai_service
        if settings.use_ai and not ai_service.model:
            app_logger.warning("AI service not available, using fallback mode")
        
        # Check data integrity
        if chatbot_engine.trucks_df.empty:
            app_logger.warning("No truck data available")
        
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