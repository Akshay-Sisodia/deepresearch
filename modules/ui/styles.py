import streamlit as st
from modules.ui.theme import get_full_css, TYPOGRAPHY, COLORS
import os

# Add a print statement to verify the theme is being loaded
print("Styles module loaded - about to load CSS from theme")

def inject_font_links():
    """Inject font links directly into the HTML head for more reliable font loading"""
    font_links = [
        '<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">'
    ]
    
    # Inject the font links
    for link in font_links:
        st.markdown(link, unsafe_allow_html=True)

def load_custom_css():
    """Load custom CSS for the application"""
    # First inject font links
    inject_font_links()
    
    # Then load the CSS
    css = get_full_css()
    
    # Apply the CSS with unsafe_allow_html=True and hide the container
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # Add additional font-forcing CSS
    force_fonts_css = """
    <style>
    /* Force fonts with !important on all elements */
    body * {
        font-family: 'Geist Mono', monospace !important;
    }
    </style>
    """
    st.markdown(force_fonts_css, unsafe_allow_html=True)
    
    # Add direct styling for chat avatars
    chat_avatar_css = """
    <style>
    /* Direct styling for chat avatars */
    /* User avatar - yellow */
    [data-testid="stChatMessageAvatar"][data-avatar-for-user="true"] {
        background-color: #ffd803 !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Assistant avatar - purple */
    [data-testid="stChatMessageAvatar"]:not([data-avatar-for-user="true"]) {
        background-color: #7f5af0 !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Override any SVG colors inside avatars */
    [data-testid="stChatMessageAvatar"] svg {
        fill: #16161a !important;
    }
    
    /* Style for the message input bar */
    .stChatInputContainer {
        background-color: #242629 !important;
        border: 1px solid #2e3035 !important;
        border-radius: 0.75rem !important;
    }
    
    /* Style for the chat input textarea */
    .stChatInputContainer textarea {
        background-color: #242629 !important;
        color: #fffffe !important;
        border: none !important;
    }
    
    /* Style for the chat input button */
    .stChatInputContainer button {
        background-color: #7f5af0 !important;
        color: #fffffe !important;
    }
    
    /* Style for the chat input button on hover */
    .stChatInputContainer button:hover {
        background-color: #6a48d7 !important;
    }
    </style>
    """
    st.markdown(chat_avatar_css, unsafe_allow_html=True)
    
    # Load custom theme CSS if it exists
    custom_theme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.streamlit', 'custom_theme.css')
    if os.path.exists(custom_theme_path):
        try:
            with open(custom_theme_path, 'r') as f:
                custom_css = f.read()
                st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
                print("Loaded custom theme CSS from", custom_theme_path)
        except Exception as e:
            print(f"Error loading custom theme CSS: {e}")
    
    # Load custom theme JavaScript if it exists
    custom_js_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.streamlit', 'custom_theme.js')
    if os.path.exists(custom_js_path):
        try:
            with open(custom_js_path, 'r') as f:
                custom_js = f.read()
                st.markdown(f"""
                <script>
                {custom_js}
                </script>
                """, unsafe_allow_html=True)
                print("Loaded custom theme JavaScript from", custom_js_path)
        except Exception as e:
            print(f"Error loading custom theme JavaScript: {e}")
