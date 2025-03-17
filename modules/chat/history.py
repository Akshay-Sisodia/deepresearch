import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from typing import Dict
from utils.logger import app_logger

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_chats() -> Dict:
    """
    Load chats from persistent storage and filter out ones older than 24 hours
    """
    chats_file = Path("chats.json")
    current_time = datetime.now()
    
    # Initialize with empty dict in case file doesn't exist or there's an error
    all_chats = {}
    
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
            # Continue with empty dict if there's an error
    
    return all_chats


def save_chats(chats: Dict) -> None:
    """Save chats to persistent storage"""
    try:
        # First update the session state
        st.session_state.all_chats = chats
        
        # Then try to save to file
        try:
            with open("chats.json", "w") as f:
                json.dump(chats, f, indent=2)
        except Exception as e:
            app_logger.warning(f"Could not save chats to file (this is normal in cloud environments): {e}")
            # Not raising an exception as we still have the chats in session state
    except Exception as e:
        app_logger.error(f"Error saving chats: {e}")


def get_session_chats(all_chats: Dict, session_id: str) -> Dict:
    """Filter chats to only include those belonging to the current session"""
    session_chats = {}
    for chat_id, chat_data in all_chats.items():
        # Check if this chat belongs to the current session
        if chat_data.get("session_id") == session_id:
            session_chats[chat_id] = chat_data
    
    app_logger.info(f"Filtered {len(session_chats)} chats for session {session_id[:8]}... out of {len(all_chats)} total chats")
    return session_chats


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