import streamlit as st
st.set_page_config(page_title="Deep Research Assistant", page_icon="🔍", layout="wide")
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
import traceback
import time
from pathlib import Path
import logging
import markdown
import re
import hashlib
import requests
import uuid

from utils.search import SearchAPI
from utils.cache import search_cache, report_cache
try:
    from utils.model import model_api
    model_api_initialized = model_api is not None
except Exception as e:
    app_logger.error(f"Error importing model_api: {str(e)}")
    model_api_initialized = False
from utils.logger import app_logger

# Add a session state flag to prevent duplicate initializations
if "app_initialized" not in st.session_state:
    app_logger.info("First-time initialization of the app")
    st.session_state.app_initialized = True
else:
    # Skip redundant logging during re-runs
    pass

# Initialize APIs only once
@st.cache_resource
def initialize_search_api():
    """Initialize and cache the search API instance"""
    # Try to get API key from secrets first, then fall back to environment variables
    serper_api_key = st.secrets.get("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        app_logger.error("SERPER_API_KEY not found in secrets or environment variables")
        return None
    api = SearchAPI(serper_api_key)
    app_logger.info("SearchAPI initialized (cached instance)")
    return api

# Function to get a unique session ID
def get_session_id():
    """Get a unique session ID using Streamlit's session state"""
    if "session_id" not in st.session_state:
        # Generate a new random session ID for this session
        session_id = str(uuid.uuid4())
        st.session_state.session_id = session_id
        app_logger.info(f"Generated new session ID: {session_id[:8]}...")
    return st.session_state.session_id

# Cache the chats loading function
@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_chats() -> Dict:
    """
    Load chats from persistent storage and filter out ones older than 24 hours
    """
    chats_file = Path("chats.json")
    current_time = datetime.now()
    
    if chats_file.exists():
        try:
            with open(chats_file, "r") as f:
                all_chats = json.load(f)
                
            # Filter out chats older than 24 hours
            filtered_chats = {}
            removed_count = 0
            
            for chat_id, chat_data in all_chats.items():
                chat_time = datetime.fromisoformat(chat_data["timestamp"])
                time_diff = current_time - chat_time
                
                # Keep chats newer than 24 hours
                if time_diff.total_seconds() < 86400:  # 24 hours in seconds
                    # Ensure all chats have a session_id field
                    if "session_id" not in chat_data:
                        # For backward compatibility - assign a default session ID
                        chat_data["session_id"] = "legacy_session"
                        app_logger.warning(f"Added missing session_id to chat {chat_id}")
                    
                    filtered_chats[chat_id] = chat_data
                else:
                    removed_count += 1
            
            if removed_count > 0:
                app_logger.info(f"Removed {removed_count} chats older than 24 hours")
                # Save the filtered chats back to storage
                save_chats(filtered_chats)
                
            return filtered_chats
            
        except Exception as e:
            app_logger.error(f"Error loading chats: {e}")
    return {}


def save_chats(chats: Dict) -> None:
    """Save chats to persistent storage"""
    try:
        with open("chats.json", "w") as f:
            json.dump(chats, f, indent=2)
    except Exception as e:
        app_logger.error(f"Error saving chats: {e}")


# Get session-specific chats
def get_session_chats(all_chats: Dict, session_id: str) -> Dict:
    """Filter chats to only include those belonging to the current session"""
    session_chats = {}
    for chat_id, chat_data in all_chats.items():
        # Check if this chat belongs to the current session
        if chat_data.get("session_id") == session_id:
            session_chats[chat_id] = chat_data
    
    app_logger.info(f"Filtered {len(session_chats)} chats for session {session_id[:8]}... out of {len(all_chats)} total chats")
    return session_chats


# Initialize session state - use a function to control this
def initialize_session_state():
    # Get the session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = get_session_id()
        app_logger.info(f"Initialized session_id in session state: {st.session_state.session_id[:8]}...")

    # Load all chats
    if "all_chats" not in st.session_state:
        st.session_state.all_chats = load_chats()
        app_logger.info(f"Loaded {len(st.session_state.all_chats)} total chats from storage")
    
    # Filter chats for this session
    if "chats" not in st.session_state:
        st.session_state.chats = get_session_chats(st.session_state.all_chats, st.session_state.session_id)
        app_logger.info(f"Filtered {len(st.session_state.chats)} chats for current session")

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
        app_logger.info("Initialized current_chat_id as None in session state")
        
    # Add a variable to store the streaming response
    if "streaming_response" not in st.session_state:
        st.session_state.streaming_response = ""
        
    # Add a variable to track if we're currently streaming
    if "is_streaming" not in st.session_state:
        st.session_state.is_streaming = False
        
    # Add a variable to control the query input
    if "query_value" not in st.session_state:
        st.session_state.query_value = ""

# Call initialization only once at the top level
initialize_session_state()

# Custom CSS for chat interface with Streamlit native elements
st.markdown(
    """
<style>
    /* Import Geist Mono font */
    @import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700&display=swap');

    /* Set the base dark theme with improved color palette */
    :root {
        --primary: #00E5A0;
        --primary-hover: #00C88A;
        --primary-light: #3DFFB6;
        --background: #0A0C0F;
        --background-secondary: #141820;
        --background-gradient: linear-gradient(135deg, #0A0C0F, #141820);
        --surface: #141820;
        --surface-gradient: linear-gradient(135deg, #141820, #202830);
        --surface-hover: #202830;
        --text: #F2F2F2;
        --text-secondary: #B0B0B8;
        --border: #202830;
        --border-accent: #E54C00;
        --border-radius: 0.75rem;
        --success: #00E5A0;
        --warning: #E54C00;
        --error: #F24236;
        --info: #00E5A0;
        --font-size-base: 1.1rem;
        --font-size-sm: 0.95rem;
        --font-size-lg: 1.25rem;
        --font-size-xl: 1.4rem;
        --input-height: 120px;
    }

    /* Apply Geist Mono font globally */
    * {
        font-family: 'Geist Mono', monospace !important;
        font-size: var(--font-size-base);
    }
    
    /* Style for code blocks with consistent font size */
    pre, code {
        font-family: 'Geist Mono', monospace !important;
        font-size: var(--font-size-base) !important;
        background-color: rgba(0, 0, 0, 0.3) !important;
        border-radius: 0.25rem !important;
        padding: 0.2rem 0.4rem !important;
    }
    
    pre {
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-radius: 0.75rem !important;
        border: 1px solid #333333 !important;
    }
    
    /* Style for LaTeX equations */
    .math-inline {
        font-size: var(--font-size-base) !important;
        color: #c5a6ff !important;
    }
    
    .math-display {
        font-size: var(--font-size-lg) !important;
        color: #c5a6ff !important;
        display: block !important;
        margin: 1rem 0 !important;
        text-align: center !important;
    }
    
    /* Style for subscripts and superscripts */
    sub, sup {
        font-size: 0.75em !important;
        line-height: 0 !important;
        position: relative !important;
        vertical-align: baseline !important;
    }
    
    sup {
        top: -0.5em !important;
    }
    
    sub {
        bottom: -0.25em !important;
    }

    /* Override Streamlit's default colors */
    .stApp {
        background: var(--background);
        color: var(--text);
    }
    
    /* Split the layout into two distinct sections */
    .chat-layout {
        display: flex;
        flex-direction: column;
        height: 100vh;
        overflow: hidden;
    }
    
    /* The chat area that scrolls */
    .chat-area {
        flex: 1;
        overflow-y: auto;
        padding-bottom: calc(var(--input-height) + 20px);
    }
    
    /* Fixed input area at the bottom */
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--background);
        border-top: 1px solid var(--border);
        padding: 1rem;
        z-index: 1000;
        height: var(--input-height);
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.5);
    }
    
    /* Style the containers with depth */
    [data-testid="stContainer"] {
        background: var(--surface-gradient);
        border-radius: var(--border-radius);
        border: 1px solid var(--border);
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.4), 0 4px 8px -1px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    
    /* Modify Streamlit form styling */
    .chat-form {
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Remove form border */
    .chat-form div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background-color: transparent !important;
    }
    
    /* Style form button */
    .chat-form div[data-testid="stForm"] button {
        background-color: var(--primary);
        color: var(--background);
        font-weight: 600;
    }
    
    /* Style expander with animation */
    .streamlit-expanderHeader {
        background-color: var(--surface);
        color: var(--text);
        border-radius: var(--border-radius);
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--surface-hover);
    }
    
    .streamlit-expanderContent {
        background-color: var(--surface);
        color: var(--text);
        border-radius: 0 0 var(--border-radius) var(--border-radius);
        padding: 1.25rem;
        border-top: 1px solid var(--border);
    }
    
    /* Style info boxes */
    .stAlert {
        background-color: var(--surface);
        color: var(--text);
        border-radius: var(--border-radius);
        border: 1px solid var(--border);
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Style text elements with improved typography */
    p, li {
        color: var(--text);
        line-height: 1.6;
        font-size: var(--font-size-base);
    }
    
    h1 {
        color: var(--text);
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        font-size: var(--font-size-xl);
    }
    
    h2, h3 {
        color: var(--text);
        font-weight: 700;
        margin-top: 1.25rem;
        margin-bottom: 0.75rem;
        font-size: var(--font-size-lg);
    }
    
    h4, h5, h6 {
        color: var(--text);
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-size: var(--font-size-base);
    }
    
    a {
        color: var(--primary-light);
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: var(--primary);
        text-decoration: underline;
    }
    
    code {
        background-color: rgba(0, 0, 0, 0.3);
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-family: 'Geist Mono', monospace;
        font-size: var(--font-size-sm);
        color: var(--primary-light);
    }
    
    pre {
        background-color: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        overflow-x: auto;
        border: 1px solid var(--border);
    }
    
    /* Style the input area */
    .stTextArea textarea {
        background-color: var(--surface);
        color: var(--text);
        border: 1px solid var(--border);
        border-radius: var(--border-radius);
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(230, 161, 112, 0.3);
    }
    
    /* Style buttons with hover effects */
    .stButton button {
        background-color: var(--primary);
        color: var(--background);
        border-radius: var(--border-radius);
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
        border: none;
        cursor: pointer;
        font-size: var(--font-size-base);
    }
    
    .stButton button:hover {
        background-color: var(--primary-hover);
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Style sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A0C0F, #141820);
        border-right: 1px solid var(--border);
        padding: 1.5rem 0.75rem;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0.5rem;
        padding-bottom: 1.5rem;
    }
    
    /* Completely reset ALL button styles in the sidebar first */
    [data-testid="stSidebar"] button {
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--border-radius) !important;
        box-shadow: none !important;
        font-weight: normal !important;
        text-align: left !important;
    }
    
    /* Style the "New Research Chat" button ONLY - using the button inside stButton */
    [data-testid="stSidebar"] div.stButton > button {
        background-color: #00876E !important; /* Darker shade of teal */
        color: #F2F2F2 !important;
        font-weight: 600 !important;
        width: 100% !important;
        padding: 0.6rem 1rem !important;
        text-align: center !important;
        border: none !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Hover state for New Research Chat button */
    [data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #00A989 !important; /* Slightly lighter on hover */
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4) !important;
    }
    
    /* Style the chat history buttons specifically */
    [data-testid="stSidebar"] [data-testid="column"] > div > button {
        background-color: rgba(20, 24, 32, 0.9) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--border-radius) !important;
        text-align: left !important;
        margin-bottom: 0.5rem !important;
        padding: 0.5rem 0.75rem !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
        font-weight: normal !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    /* Hover state for chat history buttons */
    [data-testid="stSidebar"] [data-testid="column"] > div > button:hover {
        background-color: rgba(32, 40, 48, 0.9) !important;
        border-color: var(--primary) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Active state for chat history buttons */
    [data-testid="stSidebar"] [data-testid="column"] > div > button:active,
    [data-testid="stSidebar"] [data-testid="column"] > div > button:focus {
        background-color: rgba(0, 229, 160, 0.15) !important;
        border-left: 3px solid var(--primary) !important;
    }
    
    /* Style for timestamp inside button */
    [data-testid="stSidebar"] [data-testid="stButton"] span {
        float: right !important;
        color: #888888 !important;
        font-size: 0.8rem !important;
        opacity: 0.8 !important;
    }
    
    /* Improve header styling */
    [data-testid="stSidebar"] h1 {
        color: var(--primary) !important;
        font-size: 1.75rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.75rem !important;
        border-bottom: 1px solid rgba(0, 229, 160, 0.2) !important;
    }
    
    /* Make "Previous Research" header styling stronger */
    [data-testid="stSidebar"] .stSubheader p {
        color: var(--primary) !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 1px solid rgba(0, 229, 160, 0.1) !important;
    }
    
    /* Fix timestamp display */
    [data-testid="stSidebar"] [data-testid="column"]:nth-of-type(2) .stCaption p {
        color: #FFFFFF !important;
        background-color: rgba(229, 76, 0, 0.3) !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 3px !important;
        font-size: 0.75rem !important;
        text-align: center !important;
        display: inline-block !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Chat session timestamp with better contrast */
    [data-testid="stSidebar"] [data-testid="column"]:last-child .stCaption {
        background-color: rgba(229, 76, 0, 0.2);
        color: #e6e6e6;
        padding: 0.15rem 0.4rem;
        border-radius: 3px;
        font-size: 0.7rem;
        text-align: center;
        display: inline-block;
        margin-top: 0.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    /* Chat message styling */
    .user-message {
        background: var(--surface-gradient);
        color: var(--text);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid var(--border);
        box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.4), 0 4px 8px -1px rgba(0, 0, 0, 0.3);
        font-size: var(--font-size-base);
    }
    
    .assistant-message {
        background: var(--surface-gradient);
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid var(--border);
        box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.4), 0 4px 8px -1px rgba(0, 0, 0, 0.3);
        font-size: var(--font-size-base);
    }
    
    /* Style markdown content within containers */
    .markdown-content {
        color: var(--text);
    }

    .markdown-content h1,
    .markdown-content h2,
    .markdown-content h3,
    .markdown-content h4,
    .markdown-content h5,
    .markdown-content h6 {
        color: var(--text);
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }

    .markdown-content p {
        margin-bottom: 1rem;
        line-height: 1.6;
    }

    .markdown-content ul,
    .markdown-content ol {
        margin-bottom: 1rem;
        padding-left: 1.5rem;
    }

    .markdown-content li {
        margin-bottom: 0.5rem;
    }

    .markdown-content code {
        background-color: rgba(0, 0, 0, 0.3);
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-family: 'Geist Mono', monospace;
        font-size: var(--font-size-sm);
        color: var(--primary-light);
    }

    .markdown-content pre {
        background-color: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        overflow-x: auto;
        border: 1px solid var(--border);
    }

    .markdown-content a {
        color: var(--primary-light);
        text-decoration: none;
        transition: all 0.2s ease;
    }

    .markdown-content a:hover {
        color: var(--primary);
        text-decoration: underline;
    }

    .markdown-content blockquote {
        border-left: 3px solid var(--primary);
        padding-left: 1rem;
        margin: 1rem 0;
        color: var(--text-secondary);
    }

    .markdown-content hr {
        border: none;
        height: 1px;
        background-color: var(--border);
        margin: 1.5rem 0;
    }
    
    /* Subheader styling */
    .research-header {
        color: #00E5A0;
        font-weight: 700;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #202830;
        padding-bottom: 0.75rem;
        font-size: 1.2rem;
    }
    
    /* Source styling */
    .source-item {
        border-left: 3px solid #E54C00;
        padding-left: 1rem;
        margin: 1rem 0;
    }
    
    /* Improve divider */
    hr {
        border: none;
        height: 1px;
        background-color: var(--border);
        margin: 1.5rem 0;
    }
    
    /* Badges for credibility scores */
    .credibility-high {
        background-color: var(--success);
        color: var(--background);
        padding: 0.2rem 0.4rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
        white-space: nowrap;
    }
    
    .credibility-medium {
        background-color: var(--warning);
        color: var(--background);
        padding: 0.2rem 0.4rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
        white-space: nowrap;
    }
    
    .credibility-low {
        background-color: var(--error);
        color: var(--background);
        padding: 0.2rem 0.4rem;
        border-radius: 0.5rem;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
        white-space: nowrap;
    }
</style>
""",
    unsafe_allow_html=True,
)


def create_new_chat() -> str:
    """Create a new chat session and return its ID."""
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Add the chat to both the session-specific and all chats collections
    st.session_state.chats[chat_id] = {
        "messages": [],
        "query": "",
        "title": "New Chat",
        "timestamp": datetime.now().isoformat(),
        "is_first_message_done": False,  # Track if first deep research message is done
        "session_id": st.session_state.session_id  # Associate chat with current session
    }
    
    # Also add to all_chats
    st.session_state.all_chats[chat_id] = st.session_state.chats[chat_id]
    
    # Save all chats to persistent storage
    save_chats(st.session_state.all_chats)
    app_logger.info(f"Created new chat with ID: {chat_id} for session: {st.session_state.session_id[:8]}...")
    return chat_id


def update_chat_title(chat_id: str, query: str) -> None:
    """Update the chat title based on the first message."""
    if chat_id in st.session_state.chats:
        # Create a concise title from the query
        words = query.split()
        if len(words) <= 3:
            title = query
        else:
            # Take first 3 words and add ellipsis
            title = " ".join(words[:3]) + "..."
        
        # Update in both collections
        st.session_state.chats[chat_id]["title"] = title
        st.session_state.all_chats[chat_id]["title"] = title
        
        # Save to persistent storage
        save_chats(st.session_state.all_chats)
        app_logger.info(f"Updated chat title to: {title}")


def switch_chat(chat_id: str) -> None:
    """Switch to a different chat session."""
    st.session_state.current_chat_id = chat_id
    app_logger.info(f"Switched to chat ID: {chat_id}")


def format_report(report: Dict) -> str:
    """Format a research report as markdown for Streamlit display."""
    app_logger.debug(f"Formatting report for query: {report['query']}")

    # Remove the report title line since we'll display it separately
    content = report["content"].strip()
    
    # Remove any lines starting with "## Research Report" or similar
    content_lines = content.split('\n')
    filtered_lines = []
    
    # Flag to track if we're in the sources section generated by the LLM
    in_sources_section = False
    
    for i, line in enumerate(content_lines):
        # Skip the title line that matches our query
        if line.lower().startswith(('# research report', '## research report')) and report['query'].lower() in line.lower():
            continue
            
        # Skip any potential subtitle that might appear right after the title
        if i > 0 and content_lines[i-1].startswith(('#', '##')) and line.strip() and not line.startswith(('#', '##', '-', '*', '1.')):
            continue
            
        # Detect the beginning of a sources section
        if line.lower().startswith(('# sources', '## sources', '### sources')):
            in_sources_section = True
            continue
            
        # Skip lines while in the sources section
        if in_sources_section:
            # Detect the end of the sources section (next heading)
            if line.startswith('#'):
                in_sources_section = False
            else:
                continue
                
        # Add the line if it's not in a sources section
        filtered_lines.append(line)
    
    # Recombine the content
    content = '\n'.join(filtered_lines)
    
    # Remove any extra newlines at the start
    content = content.lstrip('\n')
    # Ensure proper spacing between sections
    content = content.replace('\n\n\n', '\n\n')
    
    # The final formatted content without the redundant title and sources
    formatted_content = content
    
    # Add our own source information in a more structured way
    formatted_content += "\n\n## Sources\n\n"
    
    for idx, source in enumerate(report["sources"], 1):
        title = source['title']
        link = source['link']
        score = source['credibility_score']
        
        # Determine credibility badge HTML with color coding based on score
        if score >= 0.7:
            # High credibility - green
            credibility_html = f'<span style="background-color: #00E5A0; color: #0A0C0F; padding: 0.2rem 0.4rem; border-radius: 0.5rem; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-left: 0.5rem;">{score:.2f}</span>'
        elif score >= 0.4:
            # Medium credibility - orange
            credibility_html = f'<span style="background-color: #E54C00; color: #0A0C0F; padding: 0.2rem 0.4rem; border-radius: 0.5rem; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-left: 0.5rem;">{score:.2f}</span>'
        else:
            # Low credibility - red
            credibility_html = f'<span style="background-color: #F24236; color: #0A0C0F; padding: 0.2rem 0.4rem; border-radius: 0.5rem; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-left: 0.5rem;">{score:.2f}</span>'
        
        # Format source with title and separate [Link] at the end - ensure consistent font size
        formatted_content += f"{idx}. {title} [<a href='{link}' style='color: #c5a6ff; text-decoration: none; font-size: 1.1rem;'>Link</a>] {credibility_html}\n"
    
    return formatted_content


def generate_conversational_response(messages: List[Dict]) -> str:
    """Generate a conversational response for follow-up messages."""
    app_logger.info(f"Generating conversational response with {len(messages)} messages")
    
    # Format messages for the model - make sure to filter out any metadata fields
    # We need to create a clean copy with only role and content fields
    formatted_messages = []
    for msg in messages:
        # Only copy over the essential fields for the conversation
        # Skip any message that doesn't have both role and content
        if "role" in msg and "content" in msg:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    app_logger.info(f"Sending {len(formatted_messages)} messages to model")
    
    # Use model_api with a more conversational temperature
    try:
        response = model_api.generate_conversation_response(formatted_messages, temperature=0.7)
        return response
    except Exception as e:
        app_logger.error(f"Error generating conversational response: {str(e)}")
        return "I'm sorry, I encountered an error while processing your follow-up question. Could you try asking it differently?"


def generate_streaming_response(messages: List[Dict]) -> str:
    """Generate a streaming response for follow-up messages."""
    app_logger.info(f"Generating streaming response with {len(messages)} messages")
    
    # Format messages for the model
    formatted_messages = []
    for msg in messages:
        if "role" in msg and "content" in msg:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    try:
        # Reset the streaming response
        st.session_state.streaming_response = ""
        st.session_state.is_streaming = True
        
        # Use model_api with stream=True
        for chunk in model_api.generate_streaming_response(formatted_messages, temperature=0.7):
            if chunk:
                st.session_state.streaming_response += chunk
                # Force a rerun to update the UI with the new chunk
                time.sleep(0.01)  # Small delay to avoid too many reruns
                
        st.session_state.is_streaming = False
        return st.session_state.streaming_response
    except Exception as e:
        app_logger.error(f"Error generating streaming response: {str(e)}")
        st.session_state.is_streaming = False
        return "I'm sorry, I encountered an error while processing your follow-up question. Could you try asking it differently?"


def convert_markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML for display with LaTeX support"""
    # Process LaTeX equations before markdown conversion
    # Replace $$ equation $$ with LaTeX display mode
    text = re.sub(r'\$\$(.*?)\$\$', r'<span class="math-display">\\[\1\\]</span>', text)
    # Replace $ equation $ with LaTeX inline mode
    text = re.sub(r'\$([^\$]+?)\$', r'<span class="math-inline">\\(\1\\)</span>', text)
    
    # Improved subscript and superscript handling
    # Match subscripts with underscore followed by a single character or a group in braces
    text = re.sub(r'_([a-zA-Z0-9])', r'<sub>\1</sub>', text)  # Single character subscript
    text = re.sub(r'_\{([^}]+)\}', r'<sub>\1</sub>', text)    # Multi-character subscript in braces
    
    # Match superscripts with caret followed by a single character or a group in braces
    text = re.sub(r'\^([a-zA-Z0-9])', r'<sup>\1</sup>', text)  # Single character superscript
    text = re.sub(r'\^\{([^}]+)\}', r'<sup>\1</sup>', text)    # Multi-character superscript in braces
    
    # Use Python's markdown library to convert markdown to HTML
    html = markdown.markdown(text, extensions=['extra', 'nl2br', 'sane_lists'])
    
    # Process any HTML style tags that might have been escaped
    html = re.sub(r'&lt;span style=(["\'])(.+?)\1&gt;', r'<span style=\1\2\1>', html)
    html = re.sub(r'&lt;/span&gt;', r'</span>', html)
    html = re.sub(r'&lt;a href=(["\'])(.+?)\1(.+?)&lt;/a&gt;', r'<a href=\1\2\1\3</a>', html)
    html = re.sub(r'&lt;sub&gt;(.+?)&lt;/sub&gt;', r'<sub>\1</sub>', html)
    html = re.sub(r'&lt;sup&gt;(.+?)&lt;/sup&gt;', r'<sup>\1</sup>', html)
    
    # Fix list numbering size to match regular text instead of headings
    html = re.sub(r'<ol>', r'<ol style="font-size: 1.1rem; color: white; margin-bottom: 1rem; padding-left: 1.5rem;">', html)
    html = re.sub(r'<ul>', r'<ul style="font-size: 1.1rem; color: white; margin-bottom: 1rem; padding-left: 1.5rem;">', html)
    html = re.sub(r'<li>', r'<li style="font-size: 1.1rem; color: white; margin-bottom: 0.5rem;">', html)
    
    # Add custom styling for better appearance with larger text size
    html = html.replace('<h1>', '<h1 style="color: white; margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.8rem; font-weight: 700;">')
    html = html.replace('<h2>', '<h2 style="color: white; margin-top: 1.25rem; margin-bottom: 0.75rem; font-size: 1.6rem; font-weight: 700;">')
    html = html.replace('<h3>', '<h3 style="color: white; margin-top: 1rem; margin-bottom: 0.5rem; font-size: 1.4rem; font-weight: 700;">')
    html = html.replace('<h4>', '<h4 style="color: white; margin-top: 0.75rem; margin-bottom: 0.5rem; font-size: 1.2rem; font-weight: 700;">')
    html = html.replace('<p>', '<p style="margin-bottom: 0.75rem; color: white; font-size: 1.1rem; line-height: 1.6;">')
    
    # Improved styling for code blocks
    html = html.replace('<code>', '<code style="background-color: rgba(0,0,0,0.3); padding: 0.2rem 0.4rem; border-radius: 0.25rem; color: #c5a6ff; font-family: \'Geist Mono\', monospace; font-size: 1rem;">')
    html = html.replace('<pre>', '<pre style="background-color: rgba(0,0,0,0.3); padding: 1rem; border-radius: 0.75rem; margin: 1rem 0; overflow-x: auto; border: 1px solid #333333; color: white; font-size: 1rem;">')
    html = html.replace('<blockquote>', '<blockquote style="border-left: 3px solid #b388ff; padding-left: 1rem; margin: 1rem 0; color: #d0d0d0; font-size: 1.1rem;">')
    html = html.replace('<a ', '<a style="color: #c5a6ff; text-decoration: none; font-size: 1.1rem;" ')
    
    # Enhanced styling for subscripts and superscripts
    html = html.replace('<sub>', '<sub style="font-size: 0.75em; position: relative; bottom: -0.25em; color: inherit;">')
    html = html.replace('<sup>', '<sup style="font-size: 0.75em; position: relative; top: -0.5em; color: inherit;">')
    
    # Add MathJax script for LaTeX rendering
    html += """
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    <script type="text/x-mathjax-config">
      MathJax.Hub.Config({
        tex2jax: {
          inlineMath: [['\\\\(','\\\\)']],
          displayMath: [['\\\\[','\\\\]']],
          processEscapes: true
        }
      });
    </script>
    """
    
    return html


def display_message(message: Dict) -> None:
    """Display a chat message using Streamlit's native components."""
    role = message["role"]
    content = message["content"]
    timestamp = datetime.fromisoformat(
        message.get("timestamp", datetime.now().isoformat())
    )
    time_str = timestamp.strftime('%H:%M')
    
    # Convert markdown content to HTML
    html_content = convert_markdown_to_html(content)
    
    # Create a full-width container for the message
    msg_container = st.container()
    
    with msg_container:
        # Create different layouts based on role
        if role == "user":
            # User messages on the right side
            cols = st.columns([3, 7])
            with cols[1]:
                # Display user content in styled HTML container with timestamp inside
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1e1e28, #252532); 
                    border: 1px solid #35354a; 
                    border-radius: 0.75rem; 
                    padding: 1rem; 
                    margin-bottom: 1rem;
                    box-shadow: 0 8px 16px -2px rgba(18, 18, 24, 0.3), 0 4px 8px -1px rgba(18, 18, 24, 0.2);
                    position: relative;
                ">
                    {html_content}
                    <div style="text-align: right; font-size: 0.8rem; color: #888888; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">
                        {time_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Assistant messages on the left side
            cols = st.columns([7, 3])
            with cols[0]:
                is_research = message.get("is_research", False)
                
                # Different styling based on if it's research or a regular response
                if is_research:
                    # Research Results header - no emoji in header
                    st.markdown('<div class="research-header">Research Results</div>', unsafe_allow_html=True)
                else:
                    # Just a regular chat response - no emoji in header
                    st.markdown('<div class="research-header">Response</div>', unsafe_allow_html=True)
                
                # Display assistant content in styled HTML container with improved box styling
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #141820, #202830); 
                    border: 1px solid #202830; 
                    border-radius: 0.75rem; 
                    padding: 1.25rem;
                    margin-bottom: 1rem;
                    box-shadow: 0 8px 16px -2px rgba(7, 15, 24, 0.3), 0 4px 8px -1px rgba(7, 15, 24, 0.2);
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 4px;
                        height: 100%;
                        background: linear-gradient(to bottom, #00E5A0, #E54C00);
                    "></div>
                    <div style="padding-left: 0.5rem;">
                        {html_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"{timestamp.strftime('%H:%M')}")


def main():
    try:
        # Log app start only if a special flag isn't set
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

        # Sidebar for chat management
        with st.sidebar:
            st.title("Deep Research")
            
            # Display a subtle session identifier
            session_id_short = st.session_state.session_id[:8]
            st.markdown(f"""
            <div style="
                font-size: 0.8rem;
                color: #888888;
                margin-bottom: 1rem;
                padding: 0.5rem;
                background-color: rgba(20, 24, 32, 0.5);
                border-radius: 0.5rem;
                text-align: center;
            ">
                Session ID: {session_id_short}...
            </div>
            """, unsafe_allow_html=True)

            # New chat button
            if st.button("New Research Chat", use_container_width=True):
                # Use a session state flag to detect real clicks vs re-runs
                if not st.session_state.get("_new_chat_clicked", False):
                    app_logger.info("User clicked 'New Research Chat' button")
                    st.session_state._new_chat_clicked = True
                    new_chat_id = create_new_chat()
                    switch_chat(new_chat_id)
                    st.rerun()

            st.divider()

            # List existing chats
            st.subheader("Previous Research")
            chat_count = len(st.session_state.chats)
            app_logger.debug(f"Displaying {chat_count} existing chats for session {st.session_state.session_id[:8]}...")

            if chat_count == 0:
                st.caption("No previous research sessions found")
            else:
                # Display chats with last update time
                for chat_id, chat_data in st.session_state.chats.items():
                    # Verify this chat belongs to the current session
                    if chat_data.get("session_id") != st.session_state.session_id:
                        app_logger.warning(f"Skipping chat {chat_id} - belongs to different session")
                        continue
                        
                    title = chat_data.get("title", "New Chat")
                    
                    # Get timestamp and format as relative time
                    chat_time = datetime.fromisoformat(chat_data["timestamp"])
                    time_diff = datetime.now() - chat_time
                    
                    if time_diff.total_seconds() < 3600:  # Less than an hour
                        time_display = f"{int(time_diff.total_seconds() / 60)}m ago"
                    else:
                        time_display = f"{int(time_diff.total_seconds() / 3600)}h ago"
                    
                    # Use columns to place button and timestamp side by side
                    col1, col2 = st.columns([7, 3])
                    with col1:
                        if st.button(title, key=f"chat_{chat_id}", use_container_width=True):
                            app_logger.info(f"User selected chat: {chat_id}")
                            switch_chat(chat_id)
                            st.rerun()
                    with col2:
                        # Add custom styling to align the timestamp vertically
                        st.markdown(f"""
                        <div style="
                            color: #888888; 
                            font-size: 0.8rem; 
                            text-align: right; 
                            padding-top: 0.5rem;
                            padding-right: 0.5rem;
                        ">
                            {time_display}
                        </div>
                        """, unsafe_allow_html=True)

            # Add settings section
            st.divider()
            st.subheader("About")
            st.markdown("""
            **Deep Research Assistant** helps you conduct comprehensive research with AI assistance.
            
            - Ask any research question first
            - Get detailed answers with sources
            - Then continue with follow-up questions
            - Get conversational responses for follow-ups
            
            *Chat history is stored for 24 hours only.*
            """)

        # Main content area
        if not st.session_state.current_chat_id:
            app_logger.debug("No current chat selected")
            # Create initial chat if none exists
            if not st.session_state.chats:
                app_logger.info("No chats exist for current session, creating initial chat")
                new_chat_id = create_new_chat()
                switch_chat(new_chat_id)
            else:
                # Switch to most recent chat for this session
                session_chat_ids = [chat_id for chat_id, chat_data in st.session_state.chats.items() 
                                if chat_data.get("session_id") == st.session_state.session_id]
                
                if session_chat_ids:
                    # Sort by timestamp to get the most recent
                    latest_chat_id = sorted(
                        session_chat_ids,
                        key=lambda cid: datetime.fromisoformat(st.session_state.chats[cid]["timestamp"]),
                        reverse=True
                    )[0]
                    app_logger.info(f"Switching to most recent chat for current session: {latest_chat_id}")
                    switch_chat(latest_chat_id)
                else:
                    # Fallback - create a new chat if no chats for this session
                    app_logger.info("No chats found for current session, creating new chat")
                    new_chat_id = create_new_chat()
                    switch_chat(new_chat_id)
                    
        # Verify the current chat belongs to this session
        if st.session_state.current_chat_id:
            current_chat = st.session_state.chats.get(st.session_state.current_chat_id)
            
            if not current_chat:
                app_logger.warning(f"Current chat ID {st.session_state.current_chat_id} not found in chats")
                # Create a new chat
                new_chat_id = create_new_chat()
                switch_chat(new_chat_id)
                st.rerun()
            elif current_chat.get("session_id") != st.session_state.session_id:
                app_logger.warning(f"Current chat {st.session_state.current_chat_id} belongs to a different session")
                # Create a new chat for this session
                new_chat_id = create_new_chat()
                switch_chat(new_chat_id)
                st.rerun()
                
        current_chat = st.session_state.chats[st.session_state.current_chat_id]
        app_logger.debug(
            f"Current chat ID: {st.session_state.current_chat_id}, message count: {len(current_chat['messages'])}, session: {current_chat.get('session_id', 'unknown')[:8]}..."
        )

        # Initialize chat history in session state - always sync with current chat
        st.session_state.chat_history = current_chat["messages"]

        # Display the title
        st.title("Deep Research Assistant")
        
        # Update header based on if first message is done
        is_first_message_done = current_chat.get("is_first_message_done", False)
        if is_first_message_done:
            st.markdown("Continue the conversation with follow-up questions")
        else:
            st.markdown("Ask a research question to start, then follow up with regular questions")
        
        st.divider()

        # Show welcome message if no messages yet
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; margin: 2rem 0; background: linear-gradient(135deg, #141820, #202830); border-radius: 0.75rem; border: 1px solid #202830; box-shadow: 0 8px 16px -2px rgba(7, 15, 24, 0.4), 0 4px 8px -1px rgba(7, 15, 24, 0.3);">
                <h3 style="font-size: 1.125rem; color: #F2F2F2;">Welcome to Deep Research Assistant!</h3>
                <p style="font-size: 1rem; color: #F2F2F2;">I can help you conduct in-depth research on any topic.</p>
                <p style="font-size: 1rem; color: #F2F2F2;">Your first question will get a comprehensive research response.</p>
                <p style="font-size: 1rem; color: #F2F2F2;">Follow-up questions will get conversational answers.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display chat messages from history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                is_research = message.get("is_research", False)
                
                if message["role"] == "assistant":
                    # Different styling based on if it's research or a regular response
                    if is_research:
                        st.markdown('<div class="research-header">Research Results</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="research-header">Response</div>', unsafe_allow_html=True)
                    
                    # Ensure proper HTML handling for the content
                    content_html = message["content"]
                    
                    # First convert markdown to HTML
                    content_html = markdown.markdown(content_html, extensions=['extra', 'nl2br', 'sane_lists'])
                    
                    # Process any HTML style tags that might have been escaped
                    content_html = re.sub(r'&lt;span style=(["\'])(.+?)\1&gt;', r'<span style=\1\2\1>', content_html)
                    content_html = re.sub(r'&lt;/span&gt;', r'</span>', content_html)
                    
                    # Now add the container with the processed HTML content
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #141820, #202830); 
                        border: 1px solid #202830; 
                        border-radius: 0.75rem; 
                        padding: 1.25rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 8px 16px -2px rgba(7, 15, 24, 0.3), 0 4px 8px -1px rgba(7, 15, 24, 0.2);
                        position: relative;
                        overflow: hidden;
                    ">
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 4px;
                            height: 100%;
                            background: linear-gradient(to bottom, #00E5A0, #E54C00);
                        "></div>
                        <div style="padding-left: 0.75rem; color: #F2F2F2;">
                            {content_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # For user messages, just use standard markdown
                    st.markdown(message["content"])
        
        # Chat input (automatically fixed at the bottom)
        button_label = "Research" if not is_first_message_done else "Send Message"
        placeholder_text = "Ask your research question" if not is_first_message_done else "Ask a follow-up question"
        
        # Use Streamlit's chat_input for the message box
        query = st.chat_input(placeholder=placeholder_text)
        
        # Process user input
        if query:
            app_logger.info(f"Message submitted: {query}")
            
            # Update chat data
            current_chat["timestamp"] = datetime.now().isoformat()  # Update timestamp on new query
            
            # Update chat title if this is the first message
            if not current_chat["messages"]:
                update_chat_title(st.session_state.current_chat_id, query)
                current_chat["query"] = query  # Store the original research query
            
            # Add the user message to chat history
            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            
            # Save the updated messages to persistent storage
            current_chat["messages"] = st.session_state.chat_history
            st.session_state.all_chats[st.session_state.current_chat_id] = current_chat
            save_chats(st.session_state.all_chats)
            
            # Rerun the app to display the new message
            st.rerun()
        
        # Check if we have a new user message that needs a response
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
            # We have a new user message that needs a response
            user_message = st.session_state.chat_history[-1]["content"]
            
            # Check if this is the first message or a follow-up
            if not is_first_message_done:
                # First message - do deep research
                # Check cache first
                app_logger.debug("Checking cache for existing report")
                cached_report = report_cache.get(user_message)
                if cached_report:
                    app_logger.info("Cache hit! Using cached report")
                    formatted_report = format_report(cached_report)
                    
                    # Add to chat history
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": formatted_report + "\n\n*(Results from cache)*",
                            "timestamp": datetime.now().isoformat(),
                            "is_research": True
                        }
                    )
                    
                    # Mark first message as done
                    current_chat["is_first_message_done"] = True
                    
                    # Save updated history to persistent storage
                    current_chat["messages"] = st.session_state.chat_history
                    st.session_state.all_chats[st.session_state.current_chat_id] = current_chat
                    save_chats(st.session_state.all_chats)
                    
                    # Rerun to display response
                    st.rerun()
                else:
                    # Initialize APIs if not already done
                    if "search_api" not in st.session_state:
                        app_logger.info("Initializing SearchAPI")
                        serper_api_key = st.secrets.get("SERPER_API_KEY") or os.getenv("SERPER_API_KEY")
                        st.session_state.search_api = SearchAPI(serper_api_key)

                    # Create a chat message container for the assistant
                    with st.chat_message("assistant"):
                        # Step 1: Searching - Replace old progress bar with modern animation
                        st.markdown('<div class="research-header">Searching for information...</div>', unsafe_allow_html=True)
                        
                        # Create a modern loading animation container
                        search_container = st.container()
                        with search_container:
                            st.markdown("""
                            <div style="display: flex; justify-content: center; margin: 1.5rem 0;">
                                <div style="
                                    display: flex;
                                    align-items: center;
                                    background: linear-gradient(135deg, #141820, #202830);
                                    border-radius: 0.75rem;
                                    padding: 1.25rem;
                                    box-shadow: 0 8px 16px -2px rgba(7, 15, 24, 0.3);
                                    width: 100%;
                                ">
                                    <div style="
                                        display: flex;
                                        margin-right: 1.5rem;
                                        min-width: 50px;
                                        justify-content: center;
                                    ">
                                        <div class="spinner-container" style="
                                            position: relative;
                                            width: 50px;
                                            height: 30px;
                                            margin-right: 1.5rem;
                                            display: flex;
                                            justify-content: center;
                                            min-width: 50px;
                                        ">
                                            <div class="spinner" style="
                                                width: 30px;
                                                height: 30px;
                                                border: 3px solid transparent;
                                                border-top-color: #E54C00;
                                                border-radius: 50%;
                                                animation: spin 1s linear infinite;
                                            ">
                                                <style>
                                                    @keyframes spin {
                                                        0% { transform: rotate(0deg); }
                                                        100% { transform: rotate(360deg); }
                                                    }
                                                    @keyframes pulse {
                                                        0% { transform: scale(0.8); opacity: 0.3; }
                                                        50% { transform: scale(1.2); opacity: 1; }
                                                        100% { transform: scale(0.8); opacity: 0.3; }
                                                    }
                                                </style>
                                            </div>
                                            <div class="pulse" style="
                                                position: absolute;
                                                top: 35%;
                                                left: 35%;
                                                transform: translate(-50%, -50%);
                                                width: 12px;
                                                height: 12px;
                                                background-color: #00E5A0;
                                                border-radius: 50%;
                                                animation: pulse 1.5s ease-in-out infinite;
                                                z-index: 2;
                                            "></div>
                                        </div>
                                        <div style="color: #F2F2F2; font-size: 1rem; flex: 1;">
                                            Searching the web for relevant information...
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        try:
                            # Perform search
                            app_logger.info("Performing search")
                            time.sleep(1)  # Small delay for visual effect
                            search_results = st.session_state.search_api.search(user_message)
                            
                            # Clear the loading animation
                            search_container.empty()

                            if not search_results:
                                app_logger.warning("No search results found")
                                st.error(
                                    "No search results found. Please try a different query."
                                )
                                return

                            app_logger.info(
                                f"Found {len(search_results)} search results"
                            )
                            
                            # Step 2: Analyzing - Replace old progress bar with modern animation
                            st.markdown('<div class="research-header">Analyzing sources and generating report...</div>', unsafe_allow_html=True)
                            
                            # Create a modern analysis animation container
                            analysis_container = st.container()
                            with analysis_container:
                                st.markdown("""
                                <div style="display: flex; justify-content: center; margin: 1.5rem 0;">
                                    <div style="
                                        display: flex;
                                        align-items: center;
                                        background: linear-gradient(135deg, #141820, #202830);
                                        border-radius: 0.75rem;
                                        padding: 1.25rem;
                                        box-shadow: 0 8px 16px -2px rgba(7, 15, 24, 0.3);
                                        width: 100%;
                                    ">
                                        <div class="spinner-container" style="
                                            position: relative;
                                            width: 50px;
                                            height: 30px;
                                            margin-right: 1.5rem;
                                            display: flex;
                                            justify-content: center;
                                            min-width: 50px;
                                        ">
                                            <div class="spinner" style="
                                                width: 30px;
                                                height: 30px;
                                                border: 3px solid transparent;
                                                border-top-color: #E54C00;
                                                border-radius: 50%;
                                                animation: spin 1s linear infinite;
                                            ">
                                                <style>
                                                    @keyframes spin {
                                                        0% { transform: rotate(0deg); }
                                                        100% { transform: rotate(360deg); }
                                                    }
                                                    @keyframes pulse {
                                                        0% { transform: scale(0.8); opacity: 0.3; }
                                                        50% { transform: scale(1.2); opacity: 1; }
                                                        100% { transform: scale(0.8); opacity: 0.3; }
                                                    }
                                                </style>
                                            </div>
                                            <div class="pulse" style="
                                                position: absolute;
                                                top: 35%;
                                                left: 35%;
                                                transform: translate(-50%, -50%);
                                                width: 12px;
                                                height: 12px;
                                                background-color: #00E5A0;
                                                border-radius: 50%;
                                                animation: pulse 1.5s ease-in-out infinite;
                                                z-index: 2;
                                            "></div>
                                        </div>
                                        <div style="color: #F2F2F2; font-size: 1rem; flex: 1;">
                                            Analyzing sources and synthesizing information...
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Generate report
                            app_logger.info("Generating research report")
                            
                            # Log detailed information about the search results
                            app_logger.debug(f"Search results count: {len(search_results)}")
                            for i, result in enumerate(search_results):
                                app_logger.debug(f"Search result {i+1}: {result.title[:50]}... (score: {result.credibility_score:.2f})")
                            
                            # Log the query and model being used
                            app_logger.info(f"Using model: {model_api.model}")
                            app_logger.info(f"Research query: {user_message}")
                            
                            # Attempt to generate the report with detailed error logging
                            try:
                                report = model_api.generate_research_report(
                                    user_message,
                                    [r.to_dict() for r in search_results],
                                )
                                
                                app_logger.info(f"Report generation completed: {'Success' if report else 'Failed'}")
                                
                                if not report:
                                    app_logger.error("Report is None - generation failed")
                                    st.error("Failed to generate report. Please try again.")
                                    return
                                    
                            except Exception as e:
                                error_msg = str(e)
                                stack_trace = traceback.format_exc()
                                app_logger.error(f"Exception during report generation: {error_msg}")
                                app_logger.error(f"Stack trace: {stack_trace}")
                                st.error(f"An error occurred during report generation: {error_msg}")
                                return
                            
                            # Clear the loading animation
                            analysis_container.empty()

                            if report:
                                # Check if report content is empty
                                if not report['content'] or len(report['content'].strip()) == 0:
                                    app_logger.error("Report content is empty")
                                    st.error("Generated report is empty. Please try again.")
                                    return
                                
                                # Log report generation once
                                app_logger.info(
                                    f"Successfully generated report with {len(report['content'])} characters"
                                )
                                app_logger.debug(f"Report content starts with: {report['content'][:100]}...")

                                # Cache the report
                                report_cache.set_report(user_message, report)

                                # Format and display report
                                formatted_report = format_report(report)
                                
                                # Display the report directly
                                st.markdown(formatted_report)
                                
                                # Add report to chat history
                                st.session_state.chat_history.append(
                                    {
                                        "role": "assistant",
                                        "content": formatted_report,
                                        "timestamp": datetime.now().isoformat(),
                                        "is_research": True
                                    }
                                )
                                
                                # Mark first message as done
                                current_chat["is_first_message_done"] = True
                                
                                # Save updated history to persistent storage
                                current_chat["messages"] = st.session_state.chat_history
                                st.session_state.all_chats[st.session_state.current_chat_id] = current_chat
                                save_chats(st.session_state.all_chats)
                                
                                # Rerun to clean up the progress bars
                                st.rerun()
                            else:
                                st.error("Failed to generate report. Please try again.")
                                app_logger.error("Failed to generate report")
                        except Exception as e:
                            error_msg = str(e)
                            stack_trace = traceback.format_exc()
                            app_logger.error(
                                f"Error during research process: {error_msg}",
                                exc_info=True,
                            )
                            st.error(f"An error occurred: {error_msg}")
            else:
                # Follow-up message - generate conversational response
                with st.chat_message("assistant"):
                    st.markdown('<div class="research-header">Thinking about your question...</div>', unsafe_allow_html=True)
                    
                    # Create a modern thinking animation container
                    thinking_container = st.container()
                    with thinking_container:
                        st.markdown("""
                        <div style="display: flex; justify-content: center; margin: 1.5rem 0;">
                            <div style="
                                display: flex;
                                align-items: center;
                                background: linear-gradient(135deg, #141820, #202830);
                                border-radius: 0.75rem;
                                padding: 1.25rem;
                                box-shadow: 0 8px 16px -2px rgba(7, 15, 24, 0.3);
                                width: 100%;
                            ">
                                <div class="brain-container" style="
                                    position: relative;
                                    width: 50px;
                                    height: 40px;
                                    margin-right: 1.5rem;
                                    display: flex;
                                    justify-content: center;
                                    min-width: 50px;
                                ">
                                    <div class="brain-animation" style="
                                        position: relative;
                                        width: 40px;
                                        height: 40px;
                                    ">
                                        <div class="brain-pulse" style="
                                            position: absolute;
                                            top: 0;
                                            left: 0;
                                            width: 30px;
                                            height: 30px;
                                            background-color: rgba(0, 229, 160, 0.2);
                                            border-radius: 50%;
                                            animation: brain-pulse 2s ease-in-out infinite;
                                        ">
                                            <style>
                                                @keyframes brain-pulse {
                                                    0% { transform: scale(0.8); background-color: rgba(0, 229, 160, 0.2); }
                                                    50% { transform: scale(1.2); background-color: rgba(0, 229, 160, 0.8); }
                                                    100% { transform: scale(0.8); background-color: rgba(0, 229, 160, 0.2); }
                                                }
                                                @keyframes wave {
                                                    0% { height: 5px; }
                                                    50% { height: 20px; }
                                                    100% { height: 5px; }
                                                }
                                            </style>
                                        </div>
                                        <div style="
                                            position: absolute;
                                            bottom: 0;
                                            right: 0;
                                            display: flex;
                                            align-items: flex-end;
                                            height: 30px;
                                        ">
                                            <div class="wave" style="width: 3px; margin-right: 3px; background-color: #00E5A0; animation: wave 1s ease-in-out infinite;"></div>
                                            <div class="wave" style="width: 3px; margin-right: 3px; background-color: #00E5A0; animation: wave 1s ease-in-out infinite; animation-delay: 0.2s;"></div>
                                            <div class="wave" style="width: 3px; background-color: #00E5A0; animation: wave 1s ease-in-out infinite; animation-delay: 0.4s;"></div>
                                        </div>
                                    </div>
                                </div>
                                <div style="color: #F2F2F2; font-size: 1rem; flex: 1;">
                                    Processing your question and formulating a response...
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Initialize conversation history
                    conversation_history = []
                    for msg in st.session_state.chat_history:
                        # Make sure we're only sending the essential fields to avoid metadata issues
                        conversation_history.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
                    
                    try:
                        # Initialize streaming response
                        response_placeholder = st.empty()
                        st.session_state.streaming_response = ""
                        st.session_state.is_streaming = True
                        
                        # Generate streaming response
                        for chunk in model_api.generate_streaming_response(conversation_history, temperature=0.7):
                            if chunk:
                                # Clear the thinking animation after first chunk
                                if st.session_state.streaming_response == "":
                                    thinking_container.empty()
                                
                                # Append chunk to the full response
                                st.session_state.streaming_response += chunk
                                
                                # Update the display with the latest response
                                processed_content = markdown.markdown(st.session_state.streaming_response, extensions=['extra', 'nl2br', 'sane_lists'])
                                
                                # Apply additional styling to ensure consistent list and subscript rendering
                                processed_content = re.sub(r'<ol>', r'<ol style="font-size: 1.1rem; color: white; margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                                processed_content = re.sub(r'<ul>', r'<ul style="font-size: 1.1rem; color: white; margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                                processed_content = re.sub(r'<li>', r'<li style="font-size: 1.1rem; color: white; margin-bottom: 0.5rem;">', processed_content)
                                processed_content = re.sub(r'<sub>', r'<sub style="font-size: 0.75em; position: relative; bottom: -0.25em; color: inherit;">', processed_content)
                                processed_content = re.sub(r'<sup>', r'<sup style="font-size: 0.75em; position: relative; top: -0.5em; color: inherit;">', processed_content)
                                
                                response_placeholder.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, #141820, #202830); 
                                    border: 1px solid #202830; 
                                    border-radius: 0.75rem; 
                                    padding: 1.25rem;
                                    margin-bottom: 1rem;
                                    box-shadow: 0 8px 16px -2px rgba(7, 15, 24, 0.3), 0 4px 8px -1px rgba(7, 15, 24, 0.2);
                                    position: relative;
                                    overflow: hidden;
                                ">
                                    <div style="
                                        position: absolute;
                                        top: 0;
                                        left: 0;
                                        width: 4px;
                                        height: 100%;
                                        background: linear-gradient(to bottom, #00E5A0, #E54C00);
                                    "></div>
                                    <div style="padding-left: 0.5rem; color: #F2F2F2;">
                                        {processed_content}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Small delay to control update frequency
                                time.sleep(0.01)

                        st.session_state.is_streaming = False
                        
                        # Add final response to chat history
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": st.session_state.streaming_response,
                                "timestamp": datetime.now().isoformat(),
                                "is_research": False
                            }
                        )
                        
                        # Save updated history to persistent storage
                        current_chat["messages"] = st.session_state.chat_history
                        st.session_state.all_chats[st.session_state.current_chat_id] = current_chat
                        save_chats(st.session_state.all_chats)
                        
                        # Rerun to display the clean response
                        st.rerun()
                    except Exception as e:
                        error_msg = str(e)
                        app_logger.error(
                            f"Error generating conversational response: {error_msg}",
                            exc_info=True,
                        )
                        st.error(f"An error occurred: {error_msg}")
                        st.session_state.is_streaming = False
    except Exception as e:
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        app_logger.critical(
            f"Unhandled exception in main application: {error_msg}", exc_info=True
        )
        st.error(f"An unexpected error occurred: {error_msg}")


if __name__ == "__main__":
    main()
