import streamlit as st
import uuid
from utils.logger import app_logger
from modules.chat import load_chats, get_session_chats

def get_session_id():
    """Get a unique session ID using Streamlit's session state"""
    if "session_id" not in st.session_state:
        # Generate a new random session ID for this session
        session_id = str(uuid.uuid4())
        st.session_state.session_id = session_id
        app_logger.info(f"Generated new session ID: {session_id[:8]}...")
    return st.session_state.session_id

def initialize_session_state():
    """Initialize all session state variables"""
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