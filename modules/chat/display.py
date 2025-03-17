import streamlit as st
import markdown
import re
from datetime import datetime
from typing import Dict

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