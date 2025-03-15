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
        st.error("OpenRouter API key is missing. Please add it to your secrets.toml file or as an environment variable.")
        return None
    try:
        instance = ModelAPI(api_key)
        model_logger.info(f"ModelAPI initialized with model: {instance.model} (singleton)")
        return instance
    except Exception as e:
        model_logger.error(f"Error initializing ModelAPI: {str(e)}")
        st.error(f"Failed to initialize the AI model. Please check your API key and try again.")
        return None


class ModelAPI:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        self.api_key = api_key
        self.api_base = "https://openrouter.ai/api/v1"
        try:
            self.client = OpenAI(base_url=self.api_base, api_key=self.api_key)
            self.model = config.MODEL_NAME
            self.extra_headers = {
                "HTTP-Referer": "https://github.com/deep-research",
                "X-Title": "Deep Research Assistant",
            }
            self.max_retries = 3
            self.retry_delay = 2
            model_logger.info("ModelAPI initialized")
        except Exception as e:
            model_logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def generate_response(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate a response using the OpenRouter API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated response text or None if failed
        """
        model_logger.info(f"Generating response with temperature: {temperature}")
        model_logger.debug(f"Message count: {len(messages)}")

        try:
            model_logger.debug(f"Request messages: {messages}")
            
            # Log API request details
            model_logger.info(f"Making API request to: {self.api_base}/chat/completions")
            model_logger.info(f"Using model: {self.model}")
            model_logger.debug(f"Extra headers: {self.extra_headers}")
            
            # Implement retry logic
            retries = 0
            max_retries = self.max_retries
            
            while retries <= max_retries:
                try:
                    model_logger.info(f"API request attempt {retries + 1}/{max_retries + 1}")
                    
                    completion = self.client.chat.completions.create(
                        extra_headers=self.extra_headers,
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                    )
                    
                    # Log raw API response for debugging
                    model_logger.debug(f"Raw API response: {completion}")
                    
                    if not completion.choices:
                        model_logger.warning("No choices in response")
                        return None

                    response_text = completion.choices[0].message.content
                    response_length = len(response_text) if response_text else 0
                    model_logger.info(f"Generated response with {response_length} characters")
                    
                    if response_length == 0:
                        model_logger.warning("Response text is empty")
                        
                    return response_text
                    
                except Exception as e:
                    retries += 1
                    model_logger.warning(f"API request failed (attempt {retries}/{max_retries + 1}): {str(e)}")
                    
                    if retries <= max_retries:
                        sleep_time = self.retry_delay * retries
                        model_logger.info(f"Retrying in {sleep_time} seconds...")
                        time.sleep(sleep_time)
                    else:
                        model_logger.error(f"All {max_retries + 1} attempts failed")
                        raise
            
            return None

        except Exception as e:
            model_logger.error(f"Model API error: {str(e)}", exc_info=True)
            return None

    def generate_research_report(
        self,
        query: str,
        search_results: List[Dict],
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a research report based on search results.

        Args:
            query: The research query
            search_results: List of search result dictionaries

        Returns:
            Generated report dictionary or None if failed
        """
        model_logger.info(f"Generating research report for query: {query}")
        model_logger.debug(f"Using {len(search_results)} search results")

        try:
            # Get current date for system prompt
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Prepare system message
            system_message = {
                "role": "system",
                "content": f"""You are a research assistant that generates detailed, factual reports. Today's date is {current_date}.
                Your responses should:
                1. Be well-structured with clear sections using proper markdown headers (##, ###)
                2. Include proper citations for all information using markdown formatting
                3. Evaluate source credibility and highlight it in the text
                4. Cross-reference facts across multiple sources
                5. Maintain academic tone and objectivity
                6. Use proper spacing between sections (single blank line)
                7. Format lists using markdown bullet points (-)
                8. Use bold text (**) for emphasis on key terms
                9. Include a clear conclusion section
                10. Format sources section with proper markdown headers and spacing""",
            }

            # Prepare search results context
            context = "Based on the following sources:\n\n"
            for idx, result in enumerate(search_results, 1):
                context += f"{idx}. {result['title']}\n"
                context += f"   URL: {result['link']}\n"
                context += f"   Credibility Score: {result['credibility_score']:.2f}\n"
                context += f"   Summary: {result['snippet']}\n\n"

            # Prepare user message
            user_message = {
                "role": "user",
                "content": f"Research Query: {query}\n\nContext:\n{context}",
            }

            # Combine messages
            messages = [system_message]
            if "chat_history" in st.session_state and st.session_state.chat_history:
                chat_history = st.session_state.chat_history
                model_logger.debug(
                    f"Including {len(chat_history)} chat history messages"
                )
                messages.extend(chat_history)
            messages.append(user_message)

            model_logger.debug(
                f"Total message count for report generation: {len(messages)}"
            )
            
            # Log the actual messages being sent to the API
            model_logger.debug(f"Messages being sent to API: {json.dumps(messages, indent=2)}")

            # Generate report
            model_logger.info("Making API call to generate report content")
            response = self.generate_response(messages, temperature=0.3)
            
            # Log response details
            if response:
                response_length = len(response)
                model_logger.info(f"Received response with {response_length} characters")
                if response_length == 0:
                    model_logger.warning("Response is empty (0 characters)")
                    model_logger.debug("Empty response received from API")
                else:
                    model_logger.debug(f"First 100 chars of response: {response[:100]}...")
            else:
                model_logger.warning("Response is None")
                
            if not response:
                model_logger.warning("Failed to generate report content")
                return None

            # Structure the report
            report = {
                "query": query,
                "content": response,
                "sources": search_results,
                "timestamp": datetime.now().isoformat(),
            }

            model_logger.info(
                f"Successfully generated report with {len(response)} characters"
            )
            return report

        except Exception as e:
            model_logger.error(f"Report generation error: {str(e)}", exc_info=True)
            return None

    def generate_conversation_response(self, messages: List[Dict], temperature: float = 0.7) -> str:
        """
        Generate a conversational response for follow-up questions using the conversation history.
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Controls randomness in response generation
            
        Returns:
            Conversational response string
        """
        logger = logging.getLogger("model")
        
        try:
            logger.info(f"Generating conversational response with {len(messages)} messages")
            logger.info(f"Generating response with temperature: {temperature}")
            
            # Get the most recent question from the user
            latest_user_message = None
            for message in reversed(messages):
                if message["role"] == "user":
                    latest_user_message = message["content"]
                    break
            
            if not latest_user_message:
                logger.warning("No user message found in conversation history")
                return "I'm sorry, I couldn't find your question. Could you please ask again?"
            
            # Get current date for system prompt
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Create system message with current date
            system_message = f"""You are a knowledgeable and helpful AI assistant engaging in a follow-up conversation. Today's date is {current_date}.
            The user previously asked a deep research question, and now you're having a conversation about the topic.
            Provide helpful, accurate, and conversational responses to their follow-up questions.
            Base your answers on the previous conversation context but be concise and direct.
            Always maintain a conversational tone rather than a formal research tone.
            If you don't know something based on the conversation history, admit that you don't know."""
            
            # Format messages for the API
            formatted_messages = [{"role": "system", "content": system_message}]
            
            # Process conversation history to properly format for API
            # We need to strip out metadata and keep only role/content pairs
            for message in messages:
                # Clean the message to only include required fields and create a clean copy
                formatted_message = {
                    "role": message["role"],
                    "content": message["content"]
                }
                formatted_messages.append(formatted_message)
            
            logger.info(f"Sending {len(formatted_messages)} messages to model API")
            
            # Make API call with complete conversation history
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=1000,
            )
            
            # Extract the message content
            if response.choices and response.choices[0].message.content:
                result = response.choices[0].message.content.strip()
                logger.info(f"Generated response with {len(result)} characters")
                return result
            else:
                logger.warning("No response content received from API")
                return "I'm sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating conversational response: {str(e)}", exc_info=True)
            return f"I encountered an error while processing your question. Please try again or rephrase your question."

    def generate_streaming_response(self, messages: List[Dict], temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Generate a streaming response using the OpenAI client.
        
        Args:
            messages: List of message dictionaries with role and content
            temperature: Controls randomness in response generation
            
        Returns:
            Generator yielding text chunks as they're received
        """
        model_logger.info(f"Generating streaming response with {len(messages)} messages")
        
        try:
            # Get current date for system prompt
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Create system message with current date
            system_message = f"""You are a knowledgeable and helpful AI assistant engaging in a follow-up conversation. Today's date is {current_date}.
            The user previously asked a deep research question, and now you're having a conversation about the topic.
            Provide helpful, accurate, and conversational responses to their follow-up questions.
            Base your answers on the previous conversation context but be concise and direct.
            Always maintain a conversational tone rather than a formal research tone.
            If you don't know something based on the conversation history, admit that you don't know."""
            
            # Format messages for the API
            formatted_messages = [{"role": "system", "content": system_message}]
            
            # Process conversation history to properly format for API
            for message in messages:
                # Clean the message to only include required fields and create a clean copy
                formatted_message = {
                    "role": message["role"],
                    "content": message["content"]
                }
                formatted_messages.append(formatted_message)
            
            model_logger.info(f"Sending {len(formatted_messages)} messages to model API for streaming")
            
            # Make streaming API call using OpenAI client
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=1000,
                stream=True,
            )
            
            # Process streaming response
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        yield content
                        
        except Exception as e:
            model_logger.error(f"Error generating streaming response: {str(e)}", exc_info=True)
            yield f"I encountered an error while processing your question: {str(e)}"


# Get API key from either Streamlit secrets or environment variables
import streamlit as st
import os

# Create the model API instance with fallback to environment variables
api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
model_api = create_model_api(api_key)

# Add a check to ensure model_api is properly initialized
if model_api is None:
    model_logger.warning("model_api is None - API key may be missing or invalid")
