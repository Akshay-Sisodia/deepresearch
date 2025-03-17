import streamlit as st
import time
from typing import List, Dict
from utils.logger import app_logger

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
        from utils.model import model_api
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
        from utils.model import model_api
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