"""
Custom UI components for the Deep Research Assistant.
"""

import streamlit as st
import os
from modules.ui.theme import TYPOGRAPHY

def font_loader():
    """
    A custom component that ensures fonts are loaded properly.
    This should be called at the beginning of the app.
    """
    # Get the current font family from the theme
    font_family = TYPOGRAPHY["font_family"]
    
    # Load custom CSS file if it exists
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.streamlit', 'custom_theme.css')
    js_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.streamlit', 'custom_theme.js')
    local_fonts_css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.streamlit', 'local_fonts.css')
    
    custom_css = ""
    custom_js = ""
    local_fonts_css = ""
    
    # Try to load the custom CSS file
    try:
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                custom_css = f.read()
    except Exception as e:
        st.error(f"Error loading custom CSS: {e}")
    
    # Try to load the custom JS file
    try:
        if os.path.exists(js_path):
            with open(js_path, 'r') as f:
                custom_js = f.read()
    except Exception as e:
        st.error(f"Error loading custom JS: {e}")
    
    # Try to load the local fonts CSS file
    try:
        if os.path.exists(local_fonts_css_path):
            with open(local_fonts_css_path, 'r') as f:
                local_fonts_css = f.read()
    except Exception as e:
        st.error(f"Error loading local fonts CSS: {e}")
    
    # Apply the CSS with style tags
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)
    
    # Apply local fonts CSS if available
    if local_fonts_css:
        st.markdown(f"<style>{local_fonts_css}</style>", unsafe_allow_html=True)
    
    # Apply font forcing CSS
    st.markdown("""
    <style>
    @font-face {
        font-family: 'Geist Mono';
        src: url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700&display=swap');
        font-weight: normal;
        font-style: normal;
    }
    
    /* Force Geist Mono on EVERYTHING */
    html, body, div, span, applet, object, iframe, h1, h2, h3, h4, h5, h6, p, blockquote, pre, a, 
    abbr, acronym, address, big, cite, code, del, dfn, em, img, ins, kbd, q, s, samp, small, 
    strike, strong, sub, sup, tt, var, b, u, i, center, dl, dt, dd, ol, ul, li, fieldset, form, 
    label, legend, table, caption, tbody, tfoot, thead, tr, th, td, article, aside, canvas, details, 
    embed, figure, figcaption, footer, header, hgroup, menu, nav, output, ruby, section, summary, 
    time, mark, audio, video, button, input, textarea, select, option {
        font-family: 'Geist Mono', monospace !important;
    }
    
    /* Target Streamlit specific elements */
    .stApp, .stMarkdown, .stMarkdown p, .stMarkdown span, .stButton button, 
    .stTextInput input, .stTextArea textarea, .stSelectbox, .stMultiselect,
    [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="baseButton-secondary"],
    .css-1offfwp, .css-10trblm, .css-16idsys p, .stAlert, .stAlert p {
        font-family: 'Geist Mono', monospace !important;
    }
    
    /* Override any other font that might be set */
    * {
        font-family: 'Geist Mono', monospace !important;
    }
    
    /* Set font-family directly on body */
    body {
        font-family: 'Geist Mono', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Apply custom CSS if available
    if custom_css:
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
    
    # Apply custom JS if available
    if custom_js:
        st.markdown(f"<script>{custom_js}</script>", unsafe_allow_html=True)
    
    # Add a hidden div to force font loading
    st.markdown("""
    <div style="display: none; font-family: 'Geist Mono', monospace;">
        Font preloader
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we have local fonts and load them directly
    fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.streamlit', 'fonts')
    if os.path.exists(fonts_dir):
        # Try to find font files
        font_files = []
        for root, dirs, files in os.walk(fonts_dir):
            for file in files:
                if file.endswith(('.woff', '.woff2', '.ttf', '.otf')):
                    font_files.append(os.path.join(root, file))
        
        if font_files:
            st.markdown(f"<!-- Found {len(font_files)} local font files -->", unsafe_allow_html=True)
    
    return True 