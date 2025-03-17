import streamlit as st
from datetime import datetime
from utils.logger import app_logger
from modules.chat import create_new_chat, switch_chat

def render_sidebar():
    """Render the sidebar with chat history and controls"""
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