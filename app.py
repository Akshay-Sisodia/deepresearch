import streamlit as st
import os

# Set page configuration
st.set_page_config(page_title="Deep Research Assistant", page_icon="🔍", layout="wide")

# Import utils
from utils.cache import search_cache, report_cache
from utils.logger import app_logger

# Import theme customization (must be imported before other UI modules)
from modules.ui.theme import customize_theme
from theme_config import get_active_theme

# Apply the active theme
customize_theme(get_active_theme())

# Import modules
from modules.ui import load_custom_css, render_sidebar, render_main_content
from modules.ui.components import font_loader
from modules.session import initialize_session_state

# Load the font loader component first
font_loader()

# Ensure caches are initialized
if search_cache and report_cache:
    app_logger.info(f"Caches initialized - Search: {len(search_cache._cache)} items, Report: {len(report_cache._cache)} items")

# Initialize model API
try:
    from utils.model import model_api
    model_api_initialized = model_api is not None
except Exception as e:
    app_logger.error(f"Error importing model_api: {str(e)}")
    model_api_initialized = False

# Add a session state flag to prevent duplicate initializations
if "app_initialized" not in st.session_state:
    app_logger.info("First-time initialization of the app")
    st.session_state.app_initialized = True

def main():
    try:
        # Log app start only once per session
        if not st.session_state.get("_logged_app_start", False):
            app_logger.info("Starting Deep Research Assistant application")
            st.session_state._logged_app_start = True

        # Check for API keys and model initialization
        if not model_api_initialized:
            app_logger.error("Model API not initialized - check API keys")
            st.error(
                "AI model could not be initialized. Please check that you've set the OPENROUTER_API_KEY in your secrets.toml file or as an environment variable."
            )
            # Display instructions for setting up API keys
            st.markdown("""
            ### How to set up your API keys:
            
            1. **For local development**:
               - Create a `.streamlit/secrets.toml` file with:
               ```
               OPENROUTER_API_KEY = "your-api-key-here"
               SERPER_API_KEY = "your-api-key-here"
               ```
               
            2. **For Streamlit Cloud deployment**:
               - Go to your app settings
               - Click on "Secrets"
               - Add the same keys and values
            """)
            return

        if not (st.secrets.get("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")):
            app_logger.error("SERPER_API_KEY not found in secrets or environment variables")
            st.error("SERPER_API_KEY not found. Please set this in your secrets.toml file or as an environment variable.")
            return

        # Load custom CSS
        load_custom_css()

        # Initialize session state
        initialize_session_state()

        # Sidebar for chat management
        render_sidebar()

        # Main content area
        render_main_content(model_api)

    except Exception as e:
        error_msg = str(e)
        app_logger.critical(f"Unhandled exception in main application: {error_msg}", exc_info=True)
        st.error(f"An unexpected error occurred: {error_msg}")

if __name__ == "__main__":
    main()
