import streamlit as st
import time
import traceback
import markdown
import re
from datetime import datetime
from utils.logger import app_logger, search_logger
from modules.chat import create_new_chat, update_chat_title, switch_chat, save_chats, display_message, convert_markdown_to_html
from modules.research import search_web, generate_report, format_report, generate_streaming_report, initialize_search_api, generate_search_queries
from utils.cache import report_cache, search_cache
from modules.ui.theme import GRADIENTS, COLORS, SHADOWS, ANIMATIONS

# Add global animation styles
def add_animation_styles():
    """Add global animation styles for spinners and pulses"""
    # We don't need to add these styles here anymore as they're included in the theme.py file
    # The CSS is now generated from the theme configuration
    pass

def clean_report_content(content: str) -> str:
    """
    Clean report content by removing [object Object] artifacts
    
    Args:
        content: The report content string
        
    Returns:
        Cleaned content string
    """
    if not content or "[object Object]" not in content:
        return content
        
    # Remove standalone [object Object]
    cleaned = content.replace("[object Object]", "")
    
    # Remove comma-separated [object Object] patterns
    cleaned = cleaned.replace(",[object Object],", ",")
    cleaned = cleaned.replace(",[object Object]", "")
    cleaned = cleaned.replace("[object Object],", "")
    
    # Remove repeated commas that might be left after cleaning
    while ",," in cleaned:
        cleaned = cleaned.replace(",,", ",")
    
    # Remove leading/trailing commas in lines
    lines = [line.strip(',') for line in cleaned.split('\n')]
    
    return '\n'.join(lines)

def render_main_content(model_api):
    """Render the main content area with chat interface"""
    # Add global animation styles
    add_animation_styles()
    
    # Check if there's a current chat selected
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
        st.markdown(f"""
        <div class="fade-in" style="text-align: center; padding: 2rem; margin: 2rem 0; background: var(--surface-gradient); border-radius: var(--border-radius); border: 1px solid var(--border); box-shadow: var(--container);">
            <h3 style="font-size: 1.2rem; color: var(--text); margin-bottom: 1rem;">Welcome to Deep Research Assistant!</h3>
            <p class="slide-in" style="font-size: 1.05rem; color: var(--text); margin-bottom: 0.75rem;">I can help you conduct in-depth research on any topic.</p>
            <p class="slide-in" style="font-size: 1.05rem; color: var(--text); margin-bottom: 0.75rem; animation-delay: 0.1s;">Your first question will get a comprehensive research response.</p>
            <p class="slide-in" style="font-size: 1.05rem; color: var(--text); animation-delay: 0.2s;">Follow-up questions will get conversational answers.</p>
            <div class="gradient-line" style="margin-top: 1.5rem;"></div>
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
                <div class="message-container" style="
                    background: var(--surface-gradient); 
                    border: 1px solid var(--border); 
                    border-radius: var(--border-radius); 
                    padding: var(--container-padding);
                    margin-bottom: 1rem;
                    box-shadow: var(--container);
                    position: relative;
                    overflow: hidden;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 4px;
                        height: 100%;
                        background: var(--accent-gradient);
                    "></div>
                    <div class="fade-in" style="padding-left: 0.5rem; color: var(--text);">
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
            try:
                cached_report = report_cache.get(user_message, ignore_short_content=False)
            except TypeError as e:
                app_logger.warning(f"Cache error (likely outdated cache instance): {str(e)}")
                # Fallback to the old method signature
                cached_report = report_cache.get(user_message)
                
            if cached_report:
                app_logger.info("Cache hit! Using cached report")
                try:
                    formatted_report = format_report(cached_report)
                    
                    # Check if the formatted report indicates an error
                    if formatted_report.startswith("Error:"):
                        app_logger.error(f"Error formatting cached report: {formatted_report}")
                        # Invalidate the cache entry
                        report_cache.invalidate(user_message)
                        # Continue with normal research flow
                    else:
                        # Add to chat history
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
                        
                        # Rerun to display response
                        st.rerun()
                except Exception as e:
                    app_logger.error(f"Error processing cached report: {str(e)}")
                    # Invalidate the cache entry
                    report_cache.invalidate(user_message)
                    # Continue with normal research flow

            # Initialize APIs if not already done
            if "search_api" not in st.session_state:
                app_logger.info("Initializing SearchAPI")
                # This is now handled in the search_web function
                # Keeping this for backward compatibility
                st.session_state.search_api = initialize_search_api()

            # Create a chat message container for the assistant
            with st.chat_message("assistant"):
                # Step 1: Searching - Replace old progress bar with modern animation
                search_header = st.empty()
                search_header.markdown('<div class="research-header"></div>', unsafe_allow_html=True)
                
                # Create a modern loading animation container
                search_container = st.empty()
                with search_container.container():
                    st.markdown("""
                    <div style="text-align: center; margin: 1rem 0; display: flex; justify-content: center; align-items: center; height: 40px;">
                        <span class="pulsating-wave" style="font-size: 0.95rem;">Generating search queries...</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                try:
                    # Perform search
                    app_logger.info("Performing search")
                    time.sleep(1)  # Small delay for visual effect
                    
                    # Get current date for context
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    
                    # First, generate the search queries
                    search_queries = generate_search_queries(
                        model_api,
                        user_message, 
                        num_queries=3,
                        current_date=current_date
                    )
                    
                    # Clear the first stage completely
                    search_container.empty()
                    
                    # Update the header for the second stage
                    search_header.markdown('<div class="research-header"></div>', unsafe_allow_html=True)
                    
                    # Create a new container for the second stage
                    search_container = st.empty()
                    with search_container.container():
                        st.markdown("""
                        <div style="text-align: center; margin: 1rem 0; display: flex; justify-content: center; align-items: center; height: 40px;">
                            <span class="pulsating-wave" style="font-size: 0.95rem;">Searching the web...</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Now perform the actual searches
                    # Initialize search API
                    search_api = initialize_search_api()
                    if not search_api:
                        app_logger.error("Search API not initialized")
                        st.error("Search API could not be initialized. Please check your API keys.")
                        return
                    
                    # Create a placeholder for showing URLs being processed
                    url_status = search_container.empty()
                    
                    # Create a container for URL processing
                    url_status.markdown("""
                    <div style="text-align: center; margin: 1rem 0; display: flex; justify-content: center; align-items: center; height: 40px;">
                        <span class="pulsating-wave" style="font-size: 0.95rem;">Searching...</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Perform search for each query
                    all_results = []
                    seen_urls = set()
                    
                    for i, search_query in enumerate(search_queries):
                        app_logger.info(f"Searching with query {i+1}/{len(search_queries)}: {search_query}")
                        
                        # Update the URL status
                        url_status.markdown(f"""
                        <div style="text-align: center; margin: 1rem 0; display: flex; justify-content: center; align-items: center; height: 40px;">
                            <span class="pulsating-wave" style="font-size: 0.95rem;">Searching...</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        try:
                            # Perform the search
                            results = search_api.search(search_query, num_results=5)
                            
                            # Deduplicate results based on URL
                            for result in results:
                                url = getattr(result, 'url', None) or getattr(result, 'link', '')
                                if url and url not in seen_urls:
                                    seen_urls.add(url)
                                    all_results.append(result)
                                    
                                    # Show the URL being processed with gradient text
                                    url_status.markdown(f"""
                                    <div style="text-align: center; margin: 1rem 0; display: flex; justify-content: center; align-items: center; height: 40px;">
                                        <span class="pulsating-wave" style="font-size: 0.95rem;">{url[:60]}{"..." if len(url) > 60 else ""}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    time.sleep(0.2)  # Small delay for visual effect
                            
                            app_logger.info(f"Found {len(results)} results for query {i+1}, {len(all_results)} unique results so far")
                            
                        except Exception as e:
                            app_logger.error(f"Error searching for query {i+1}: {str(e)}")
                    
                    # Cache the combined results
                    search_cache.set(user_message, all_results)
                    
                    search_results = all_results
                    
                    # Clear the search container and header completely when done
                    search_container.empty()
                    search_header.empty()

                    if not search_results:
                        app_logger.warning("No search results found")
                        st.error(
                            "No search results found. Please try a different query."
                        )
                        return

                    app_logger.info(
                        f"Found {len(search_results)} search results"
                    )
                    
                    # Step 2: Analyzing - Create a new header and container for the analysis stage
                    analysis_header = st.empty()
                    analysis_header.markdown('<div class="research-header"></div>', unsafe_allow_html=True)
                    
                    # Create a modern analysis animation container
                    analysis_container = st.empty()
                    with analysis_container.container():
                        st.markdown("""
                        <div style="text-align: center; margin: 1rem 0; display: flex; justify-content: center; align-items: center; height: 40px;">
                            <span class="pulsating-wave" style="font-size: 0.95rem;">Analyzing sources...</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Attempt to generate the report with detailed error logging
                    try:
                        # Initialize streaming response
                        report_placeholder = st.empty()
                        st.session_state.streaming_report = ""
                        st.session_state.is_report_streaming = True
                        
                        # Create a report object to store the complete report
                        complete_report = None
                        
                        # Generate streaming report
                        for result in generate_streaming_report(
                            model_api,
                            user_message,
                            [r for r in search_results],
                        ):
                            if "error" in result:
                                app_logger.error(f"Error in streaming report: {result['error']}")
                                st.error(f"An error occurred: {result['error']}")
                                return
                            
                            if "chunk" in result and result["chunk"]:
                                # Clear the analysis animation after first chunk
                                if st.session_state.streaming_report == "":
                                    analysis_container.empty()
                                    analysis_header.empty()
                                
                                # Append chunk to the full response
                                st.session_state.streaming_report += result["chunk"]
                                
                                # Get the complete report object
                                complete_report = result["report"]
                                
                                # Format the current content
                                current_report = {
                                    "query": user_message,
                                    "content": st.session_state.streaming_report,
                                    "sources": complete_report["sources"],
                                    "timestamp": complete_report["timestamp"]
                                }
                                
                                # Format and display the current state of the report
                                # Ignore short content errors during streaming
                                try:
                                    formatted_report = format_report(current_report, ignore_short_content=True, show_sources=False)
                                except TypeError as e:
                                    app_logger.warning(f"Format error (likely outdated function): {str(e)}")
                                    # Fallback to the old method signature
                                    formatted_report = format_report(current_report)
                                
                                # Clean the report content
                                formatted_report = clean_report_content(formatted_report)
                                
                                # Process the markdown to HTML with proper styling
                                processed_content = markdown.markdown(formatted_report, extensions=['extra', 'nl2br', 'sane_lists'])
                                
                                # Apply additional styling to ensure consistent rendering
                                processed_content = re.sub(r'<h1>', r'<h1 style="font-size: 1.9rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                                processed_content = re.sub(r'<h2>', r'<h2 style="font-size: 1.6rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                                processed_content = re.sub(r'<h3>', r'<h3 style="font-size: 1.35rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                                processed_content = re.sub(r'<p>', r'<p style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                                processed_content = re.sub(r'<ol>', r'<ol style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                                processed_content = re.sub(r'<ul>', r'<ul style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                                processed_content = re.sub(r'<li>', r'<li style="font-size: 1.15rem; color: var(--text); margin-bottom: 0.5rem;">', processed_content)
                                processed_content = re.sub(r'<a ', r'<a style="color: var(--primary); text-decoration: none;" ', processed_content)
                                processed_content = re.sub(r'<code>', r'<code style="background-color: rgba(0,0,0,0.2); padding: 0.2rem 0.4rem; border-radius: 0.2rem; font-size: 0.95rem;">', processed_content)
                                processed_content = re.sub(r'<pre>', r'<pre style="background-color: rgba(0,0,0,0.2); padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-bottom: 1rem;">', processed_content)
                                processed_content = re.sub(r'<blockquote>', r'<blockquote style="border-left: 3px solid var(--primary); padding-left: 1rem; margin-left: 0; margin-right: 0; color: var(--text-secondary);">', processed_content)
                                
                                # Update the display with the latest report
                                report_placeholder.markdown(f"""
                                <div class="message-container" style="
                                    background: var(--surface-gradient); 
                                    border: 1px solid var(--border); 
                                    border-radius: var(--border-radius); 
                                    padding: var(--container-padding);
                                    margin-bottom: 1rem;
                                    box-shadow: var(--container);
                                    position: relative;
                                    overflow: hidden;
                                ">
                                    <div style="
                                        position: absolute;
                                        top: 0;
                                        left: 0;
                                        width: 4px;
                                        height: 100%;
                                        background: var(--accent-gradient);
                                    "></div>
                                    <div class="fade-in" style="padding-left: 0.5rem; color: var(--text);">
                                        {processed_content}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Small delay to control update frequency
                                time.sleep(0.01)
                        
                        st.session_state.is_report_streaming = False
                        
                        # Use the complete report for caching and history
                        report = complete_report
                        
                        app_logger.info(f"Report generation completed: {'Success' if report else 'Failed'}")
                        
                        if not report:
                            app_logger.error("Report is None - generation failed")
                            st.error("Failed to generate report. Please try again.")
                            return
                            
                        # Format and display final report with sources
                        formatted_report = format_report(report, show_sources=True)
                        formatted_report = clean_report_content(formatted_report)
                        
                        # Process the markdown to HTML with proper styling
                        processed_content = markdown.markdown(formatted_report, extensions=['extra', 'nl2br', 'sane_lists'])
                        
                        # Apply styling
                        processed_content = re.sub(r'<h1>', r'<h1 style="font-size: 1.9rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                        processed_content = re.sub(r'<h2>', r'<h2 style="font-size: 1.6rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                        processed_content = re.sub(r'<h3>', r'<h3 style="font-size: 1.35rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                        processed_content = re.sub(r'<p>', r'<p style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem;">', processed_content)
                        processed_content = re.sub(r'<ol>', r'<ol style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                        processed_content = re.sub(r'<ul>', r'<ul style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                        processed_content = re.sub(r'<li>', r'<li style="font-size: 1.15rem; color: var(--text); margin-bottom: 0.5rem;">', processed_content)
                        processed_content = re.sub(r'<a ', r'<a style="color: var(--primary); text-decoration: none;" ', processed_content)
                        processed_content = re.sub(r'<code>', r'<code style="background-color: rgba(0,0,0,0.2); padding: 0.2rem 0.4rem; border-radius: 0.2rem; font-size: 0.95rem;">', processed_content)
                        processed_content = re.sub(r'<pre>', r'<pre style="background-color: rgba(0,0,0,0.2); padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-bottom: 1rem;">', processed_content)
                        processed_content = re.sub(r'<blockquote>', r'<blockquote style="border-left: 3px solid var(--primary); padding-left: 1rem; margin-left: 0; margin-right: 0; color: var(--text-secondary);">', processed_content)
                        
                        # Display final report with sources
                        report_placeholder.markdown(f"""
                        <div class="message-container" style="
                            background: var(--surface-gradient); 
                            border: 1px solid var(--border); 
                            border-radius: var(--border-radius); 
                            padding: var(--container-padding);
                            margin-bottom: 1rem;
                            box-shadow: var(--container);
                            position: relative;
                            overflow: hidden;
                        ">
                            <div style="
                                position: absolute;
                                top: 0;
                                left: 0;
                                width: 4px;
                                height: 100%;
                                background: var(--accent-gradient);
                            "></div>
                            <div class="fade-in" style="padding-left: 0.5rem; color: var(--text);">
                                {processed_content}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        error_msg = str(e)
                        stack_trace = traceback.format_exc()
                        app_logger.error(f"Exception during report generation: {error_msg}")
                        app_logger.error(f"Stack trace: {stack_trace}")
                        st.error(f"An error occurred during report generation: {error_msg}")
                        return
                    
                    # We don't need to clear the containers here since they're already cleared during streaming

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

                        # Format and display report - already displayed during streaming
                        formatted_report = format_report(report)
                        
                        # Clean the report content to remove any [object Object] artifacts
                        formatted_report = clean_report_content(formatted_report)
                        
                        # Cache the report
                        report_cache.set_report(user_message, report)
                        
                        # No need to display the report again, it's already displayed during streaming
                        
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
                thinking_header = st.empty()
                thinking_header.markdown('<div class="research-header"></div>', unsafe_allow_html=True)
                
                # Create a modern thinking animation container
                thinking_container = st.empty()
                with thinking_container.container():
                    st.markdown("""
                    <div style="text-align: center; margin: 1rem 0; display: flex; justify-content: center; align-items: center; height: 40px;">
                        <span class="pulsating-wave" style="font-size: 0.95rem;">Processing your question...</span>
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
                                thinking_header.empty()
                            
                            # Append chunk to the full response
                            st.session_state.streaming_response += chunk
                            
                            # Update the display with the latest response
                            processed_content = markdown.markdown(st.session_state.streaming_response, extensions=['extra', 'nl2br', 'sane_lists'])
                            
                            # Apply additional styling to ensure consistent list and subscript rendering
                            processed_content = re.sub(r'<ol>', r'<ol style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                            processed_content = re.sub(r'<ul>', r'<ul style="font-size: 1.15rem; color: var(--text); margin-bottom: 1rem; padding-left: 1.5rem;">', processed_content)
                            processed_content = re.sub(r'<li>', r'<li style="font-size: 1.15rem; color: var(--text); margin-bottom: 0.5rem;">', processed_content)
                            processed_content = re.sub(r'<sub>', r'<sub style="font-size: 0.8em; position: relative; bottom: -0.25em; color: inherit;">', processed_content)
                            processed_content = re.sub(r'<sup>', r'<sup style="font-size: 0.8em; position: relative; top: -0.5em; color: inherit;">', processed_content)
                            
                            response_placeholder.markdown(f"""
                            <div class="message-container" style="
                                background: var(--surface-gradient); 
                                border: 1px solid var(--border); 
                                border-radius: var(--border-radius); 
                                padding: var(--container-padding);
                                margin-bottom: 1rem;
                                box-shadow: var(--container);
                                position: relative;
                                overflow: hidden;
                            ">
                                <div style="
                                    position: absolute;
                                    top: 0;
                                    left: 0;
                                    width: 4px;
                                    height: 100%;
                                    background: var(--accent-gradient);
                                "></div>
                                <div class="fade-in" style="padding-left: 0.5rem; color: var(--text);">
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