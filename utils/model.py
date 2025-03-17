from openai import OpenAI
from typing import List, Dict, Any, Optional, Generator
import config
from datetime import datetime
from utils.logger import model_logger
import streamlit as st
import os
import json
import logging
import time
import requests

# Use Streamlit's caching to ensure we only create one instance of ModelAPI
@st.cache_resource
def create_model_api(api_key: str):
    """Create a singleton instance of ModelAPI using Streamlit's caching"""
    if not api_key:
        model_logger.error("No API key provided to create_model_api")
        return None
    try:
        instance = ModelAPI(api_key)
        model_logger.info(f"ModelAPI initialized with model: {instance.model}")
        return instance
    except Exception as e:
        model_logger.error(f"Error initializing ModelAPI: {str(e)}")
        return None


class ModelAPI:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.api_base = "https://openrouter.ai/api/v1"
        self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)
        self.model = config.MODEL_NAME
        self.extra_headers = {
            "HTTP-Referer": "https://github.com/deep-research",
            "X-Title": "Deep Research Assistant",
        }
        self.max_retries = 3
        self.retry_delay = 2
        model_logger.info("ModelAPI initialized")

    def _handle_api_error(self, e: Exception, context: str) -> None:
        """Handle API errors with consistent logging"""
        error_msg = str(e)
        model_logger.error(f"API error during {context}: {error_msg}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            model_logger.error(f"Response details: {e.response.text}")
        return error_msg

    def generate_response(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate a response from the model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Temperature parameter for generation
            
        Returns:
            Generated text or None if an error occurred
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    headers=self.extra_headers,
                )
                
                if not response.choices:
                    model_logger.error("Empty response from API")
                    return None
                    
                return response.choices[0].message.content
                
            except Exception as e:
                error_msg = self._handle_api_error(e, "text generation")
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    model_logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    model_logger.error(f"Failed after {self.max_retries} attempts")
                    return f"Error: {error_msg}"
        
        return None

    def generate_conversation_response(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Generate a response for a conversation.
        
        Args:
            messages: List of message dictionaries
            temperature: Temperature parameter for generation
            
        Returns:
            Generated response text
        """
        # Validate messages format
        if not messages or not isinstance(messages, list):
            model_logger.error("Invalid messages format")
            return "Error: Invalid message format"
            
        # Ensure each message has role and content
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                model_logger.error(f"Invalid message format: {msg}")
                return "Error: Invalid message format"
        
        try:
            response = self.generate_response(messages, temperature)
            if response is None:
                return "I'm sorry, I couldn't generate a response. Please try again."
            return response
        except Exception as e:
            error_msg = self._handle_api_error(e, "conversation")
            return f"I'm sorry, an error occurred: {error_msg}"

    def generate_streaming_response(self, messages: List[Dict], temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Generate a streaming response from the model.
        
        Args:
            messages: List of message dictionaries
            temperature: Temperature parameter for generation
            
        Yields:
            Chunks of generated text
        """
        # Validate messages
        if not messages or not isinstance(messages, list):
            yield "Error: Invalid message format"
            return
            
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                yield "Error: Invalid message format"
                return
        
        for attempt in range(self.max_retries):
            try:
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    stream=True,
                    headers=self.extra_headers,
                )
                
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                
                return
                
            except Exception as e:
                error_msg = self._handle_api_error(e, "streaming")
                
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (attempt + 1)
                    model_logger.info(f"Retrying streaming in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    yield f"\nError: {error_msg}"
                    return

    def generate_research_report(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate a research report.
        
        Args:
            prompt: The research prompt
            temperature: Temperature parameter for generation
            
        Returns:
            Generated report text
        """
        messages = [
            {"role": "system", "content": "You are a research assistant. Generate a comprehensive report based on the query."},
            {"role": "user", "content": prompt}
        ]
        
        return self.generate_response(messages, temperature)

    def generate_streaming_research_report(self, prompt: str, temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Generate a streaming research report.
        
        Args:
            prompt: The research prompt
            temperature: Temperature parameter for generation
            
        Yields:
            Chunks of the generated report
        """
        messages = [
            {"role": "system", "content": "You are a research assistant. Generate a comprehensive report based on the query."},
            {"role": "user", "content": prompt}
        ]
        
        yield from self.generate_streaming_response(messages, temperature)

    def generate_search_queries(self, prompt: str, temperature: float = 0.7) -> Optional[List[str]]:
        """
        Generate search queries based on a research question.
        
        Args:
            prompt: The research question
            temperature: Temperature parameter for generation
            
        Returns:
            List of search queries
        """
        system_prompt = """
        You are a search query generator. Your task is to generate effective search queries for a given research question.
        Return a JSON array of strings, with each string being a search query.
        Generate 3-5 diverse queries that cover different aspects of the research question.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate search queries for researching: {prompt}"}
        ]
        
        try:
            response = self.generate_response(messages, temperature)
            if not response:
                return None
                
            # Extract JSON array from response
            try:
                # Find JSON array in the response
                import re
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    queries = json.loads(json_match.group(0))
                    return queries if isinstance(queries, list) else None
                else:
                    model_logger.error("No JSON array found in response")
                    return None
            except json.JSONDecodeError:
                model_logger.error(f"Failed to parse JSON from response: {response}")
                return None
                
        except Exception as e:
            self._handle_api_error(e, "search query generation")
            return None

# Create the model API instance
try:
    # First try to get from Streamlit secrets
    api_key = st.secrets.get("OPENROUTER_API_KEY")
    
    # If not found in secrets, try environment variables
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
        
    if not api_key:
        model_logger.error("OPENROUTER_API_KEY not found in secrets or environment variables")
    else:
        model_logger.info("OPENROUTER_API_KEY found, initializing model API")
        
    model_api = create_model_api(api_key)
    
    # Add a check to ensure model_api is properly initialized
    if model_api is None:
        model_logger.warning("model_api is None - API key may be missing or invalid")
except Exception as e:
    model_logger.error(f"Error initializing model_api: {str(e)}")
    model_api = None
