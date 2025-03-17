"""
Report generation and formatting for the research module.
"""

import json
from typing import Dict, List, Optional, Any, Generator
from datetime import datetime
import streamlit as st
from utils.logger import research_logger, model_logger
from modules.research.models import SearchResult
import time
import re

def generate_report(
    model_api,
    query: str,
    search_results: List[SearchResult],
) -> Optional[Dict[str, Any]]:
    """
    Generate a research report based on search results.

    Args:
        model_api: The model API instance
        query: The research query
        search_results: List of search result objects

    Returns:
        Generated report dictionary or None if failed
    """
    research_logger.info(f"Generating research report for query: {query}")
    research_logger.debug(f"Using {len(search_results)} search results")

    if not search_results:
        research_logger.warning("No search results provided for report generation")
        return None
    
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Prepare the context from search results
    context = []
    for i, result in enumerate(search_results):
        # Get URL from either url or link attribute
        url = getattr(result, 'url', None) or getattr(result, 'link', '')
        context.append(f"Source {i+1}: {result.title}\nURL: {url}\nContent: {result.snippet}\nCredibility: {result.credibility_score:.2f}")
    
    context_text = "\n\n".join(context)
    
    # Create the prompt for the model
    prompt = f"""Today is {current_date}. You are a research assistant tasked with creating a comprehensive report on the following query:
    
Query: {query}

I have gathered the following information from various sources. Please analyze this information and create a detailed report.

{context_text}

Your report should:
1. Provide a thorough answer to the query
2. Synthesize information from multiple sources
3. Cite sources using [Source X] notation
4. Highlight any contradictions or uncertainties
5. Be well-structured with headings and sections
6. Include a brief summary at the beginning
7. Consider the current date ({current_date}) for context if relevant

Please format your response in Markdown.
"""
    
    try:
        # Generate the report content
        report_content = model_api.generate_research_report(prompt)
        
        if not report_content:
            research_logger.error("Failed to generate report content")
            return None
        
        # Ensure report_content is a string
        if not isinstance(report_content, str):
            try:
                import json
                # If it's an array of objects, extract and join their content
                if isinstance(report_content, list):
                    research_logger.warning(f"Report content is a list with {len(report_content)} items")
                    # Try to extract content from each object in the list
                    extracted_content = []
                    for item in report_content:
                        if isinstance(item, dict) and 'content' in item:
                            extracted_content.append(item['content'])
                        elif isinstance(item, dict) and 'text' in item:
                            extracted_content.append(item['text'])
                        elif isinstance(item, str):
                            extracted_content.append(item)
                        else:
                            # If we can't extract specific content, convert the whole object to string
                            extracted_content.append(json.dumps(item))
                    
                    # Join all extracted content
                    report_content = "\n\n".join(extracted_content)
                # If it's a dictionary, check for content field
                elif isinstance(report_content, dict):
                    research_logger.warning(f"Report content is a dictionary with keys: {list(report_content.keys())}")
                    if 'content' in report_content:
                        report_content = report_content['content']
                    elif 'text' in report_content:
                        report_content = report_content['text']
                    else:
                        # Convert the whole dictionary to a string
                        report_content = json.dumps(report_content, indent=2)
                else:
                    # For any other type, convert to string
                    report_content = str(report_content)
                
                research_logger.warning(f"Report content was not a string, converted from: {type(report_content)}")
            except Exception as e:
                research_logger.error(f"Failed to convert report content to string: {str(e)}")
                report_content = str(report_content)  # Fallback to basic string conversion
        
        # Clean up any [object Object] artifacts in the content
        if "[object Object]" in report_content:
            research_logger.warning("Found [object Object] in report content, cleaning up")
            report_content = report_content.replace("[object Object]", "")
            report_content = report_content.replace(",[object Object],", ",")
            report_content = report_content.replace(",[object Object]", "")
            report_content = report_content.replace("[object Object],", "")
            
            # Remove repeated commas that might be left after cleaning
            while ",," in report_content:
                report_content = report_content.replace(",,", ",")
            
            # Remove leading/trailing commas in lines
            lines = report_content.split('\n')
            for i, line in enumerate(lines):
                lines[i] = line.strip(',')
            
            report_content = '\n'.join(lines)
        
        # Process search results to ensure they're properly formatted as dictionaries
        sources = []
        for result in search_results:
            try:
                # Create a clean dictionary for each source
                source = {
                    "title": result.title if hasattr(result, 'title') else "Unknown Source",
                    "url": getattr(result, 'url', None) or getattr(result, 'link', ''),
                    "credibility": result.credibility_score if hasattr(result, 'credibility_score') else 0.5
                }
                sources.append(source)
            except Exception as e:
                research_logger.error(f"Error processing search result: {str(e)}")
                # Add a minimal valid source
                sources.append({
                    "title": "Source",
                    "url": "",
                    "credibility": 0.3
                })
        
        # Create the report object
        report = {
            "query": query,
            "content": report_content,
            "sources": sources,
            "timestamp": st.session_state.get("current_timestamp", "")
        }
        
        research_logger.info(f"Successfully generated report with {len(report_content)} characters")
        return report
    
    except Exception as e:
        research_logger.error(f"Error generating report: {str(e)}")
        return None

def format_report(report: Dict[str, Any], ignore_short_content: bool = False, show_sources: bool = True) -> str:
    """
    Format a report for display
    
    Args:
        report: The report to format
        ignore_short_content: If True, don't validate content length (useful for streaming)
        show_sources: If True, show sources section at the end (set False during streaming)
        
    Returns:
        Formatted report as a string
    """
    # Validate report structure
    if not report:
        research_logger.error("Report is None or empty")
        return "Error: Invalid report data (empty report)"
    
    if "content" not in report:
        research_logger.error("Report missing content field")
        return "Error: Invalid report data (missing content)"
    
    # Get content and ensure it's a string
    content = report["content"]
    if not isinstance(content, str):
        try:
            content = str(content)
            report["content"] = content
            research_logger.warning(f"Report content was not a string, converted from object: {type(report['content'])}")
        except Exception as e:
            research_logger.error(f"Failed to convert report content to string: {str(e)}")
            return "Error: Invalid report content format"
    
    # Check if content is empty or too short
    if not ignore_short_content and (not content or len(content.strip()) < 50):
        research_logger.error(f"Report content too short: {len(content)} chars")
        return "Error: Invalid report data (content too short)"
    
    # Process sources first to create a mapping of source numbers to URLs
    source_urls = {}
    if "sources" in report:
        for i, source in enumerate(report["sources"]):
            if isinstance(source, dict):
                url = source.get('url', '') or source.get('link', '')
                if url:
                    # Source numbers are 1-indexed
                    source_urls[i+1] = url
    
    # Replace source citations with hyperlinks
    def replace_source(match):
        # Get the full match
        full_match = match.group(0)
        
        # Extract all source numbers from the match
        source_numbers = re.findall(r'Source\s+(\d+)', full_match)
        
        if not source_numbers:
            return full_match
        
        # Create hyperlinks for each source number
        linked_sources = []
        for num_str in source_numbers:
            try:
                num = int(num_str)
                if num in source_urls and source_urls[num]:
                    linked_sources.append(f'<a href="{source_urls[num]}" target="_blank" style="color: #00E5A0; text-decoration: none;">[{num}]</a>')
                else:
                    linked_sources.append(f'[{num}]')
            except ValueError:
                linked_sources.append(f'[{num_str}]')
        
        # Join the linked sources with commas
        return ' '.join(linked_sources)
    
    # Apply the replacement
    content = re.sub(r'\[Source\s+(\d+)(?:(?:\s*,\s*|\s+and\s+)Source\s+(\d+))*\]', replace_source, content)
    
    # Only add sources section at the end if show_sources is True
    if show_sources and "sources" in report and report["sources"]:
        # Add a sources section at the end
        sources_md = "\n\n## Sources\n\n"
        
        # Create a mapping of credibility scores to labels and colors
        credibility_map = {
            (0.8, 1.0): ("High", "#28a745"),
            (0.6, 0.8): ("Good", "#5cb85c"),
            (0.4, 0.6): ("Medium", "#ffc107"),
            (0.2, 0.4): ("Low", "#dc3545"),
            (0.0, 0.2): ("Poor", "#d9534f")
        }
        
        # Add each source with its credibility rating
        for i, source in enumerate(report["sources"]):
            if not isinstance(source, dict):
                continue
                
            # Get source details
            title = source.get('title', f"Source {i+1}")
            url = source.get('url', '') or source.get('link', '')
            credibility = source.get('credibility', 0.5)
            
            # Determine credibility label and color
            cred_label = "Medium"
            cred_color = "#ffc107"
            for (min_val, max_val), (label, color) in credibility_map.items():
                if min_val <= credibility <= max_val:
                    cred_label = label
                    cred_color = color
                    break
            
            # Create a credibility pill with color spectrum
            # Calculate color based on credibility score (red to yellow to green)
            if credibility < 0.5:
                # Red (low) to yellow (medium): #dc3545 to #ffc107
                red = int(220 - (credibility * 2 * (220 - 255)))
                green = int(53 + (credibility * 2 * (193 - 53)))
                blue = int(69 + (credibility * 2 * (7 - 69)))
            else:
                # Yellow (medium) to green (high): #ffc107 to #28a745
                red = int(255 - ((credibility - 0.5) * 2 * (255 - 40)))
                green = int(193 + ((credibility - 0.5) * 2 * (167 - 193)))
                blue = int(7 + ((credibility - 0.5) * 2 * (69 - 7)))
            
            # Ensure RGB values are within valid range
            red = max(0, min(255, red))
            green = max(0, min(255, green))
            blue = max(0, min(255, blue))
            
            # Convert to hex color
            hex_color = f"#{red:02x}{green:02x}{blue:02x}"
            
            # Create the pill with dynamic color
            credibility_pill = f'<span style="display: inline-block; padding: 0.2rem 0.4rem; border-radius: 0.5rem; font-size: 0.8rem; font-weight: 600; color: white; background-color: {hex_color}; margin-left: 0.5rem; white-space: nowrap;">{cred_label} ({credibility:.2f})</span>'
            
            # Create an anchor for linking
            source_anchor = f'<a id="source-{i+1}"></a>'
            
            # Add the source with its credibility pill and modern link
            modern_link = f'<a href="{url}" target="_blank" style="color: #00E5A0; text-decoration: none; margin-left: 0.5rem;">Link</a>' if url else ''
            sources_md += f"{source_anchor}{i+1}. {title} {modern_link} {credibility_pill}\n\n"
        
        content += sources_md
    
    return content

def generate_streaming_report(
    model_api,
    query: str,
    search_results: List[SearchResult],
) -> Generator[Dict[str, Any], None, None]:
    """
    Generate a streaming research report based on search results.

    Args:
        model_api: The model API instance
        query: The research query
        search_results: List of search result objects

    Yields:
        Chunks of the report content as they are generated
    """
    research_logger.info(f"Generating streaming research report for query: {query}")
    research_logger.debug(f"Using {len(search_results)} search results")

    # Check if the model API has the streaming method
    if not hasattr(model_api, 'generate_streaming_research_report'):
        research_logger.warning("ModelAPI doesn't have streaming method, falling back to non-streaming")
        # Fallback to non-streaming implementation
        try:
            # Generate the full report
            report = generate_report(model_api, query, search_results)
            if report:
                # Simulate streaming by yielding the content in chunks
                content = report["content"]
                chunk_size = 10  # Characters per chunk
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i+chunk_size]
                    # Update the report content with the current chunk
                    report_so_far = {
                        "query": query,
                        "content": content[:i+chunk_size],
                        "sources": report["sources"],
                        "timestamp": report["timestamp"]
                    }
                    yield {"chunk": chunk, "report": report_so_far}
                    time.sleep(0.01)  # Small delay to simulate streaming
            else:
                yield {"error": "Failed to generate report"}
        except Exception as e:
            research_logger.error(f"Error in fallback streaming report: {str(e)}")
            yield {"error": f"Error generating report: {str(e)}"}
        return

    if not search_results:
        research_logger.warning("No search results provided for report generation")
        yield {"error": "No search results provided"}
        return
    
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Prepare the context from search results
    context = []
    for i, result in enumerate(search_results):
        # Get URL from either url or link attribute
        url = getattr(result, 'url', None) or getattr(result, 'link', '')
        context.append(f"Source {i+1}: {result.title}\nURL: {url}\nContent: {result.snippet}\nCredibility: {result.credibility_score:.2f}")
    
    context_text = "\n\n".join(context)
    
    # Create the prompt for the model
    prompt = f"""Today is {current_date}. You are a research assistant tasked with creating a comprehensive report on the following query:
    
Query: {query}

I have gathered the following information from various sources. Please analyze this information and create a detailed report.

{context_text}

Your report should:
1. Provide a thorough answer to the query
2. Synthesize information from multiple sources
3. Cite sources using [Source X] notation
4. Highlight any contradictions or uncertainties
5. Be well-structured with headings and sections
6. Include a brief summary at the beginning
7. Consider the current date ({current_date}) for context if relevant

Please format your response in Markdown.
"""
    
    try:
        # Process search results to ensure they're properly formatted as dictionaries
        sources = []
        for result in search_results:
            try:
                # Create a clean dictionary for each source
                source = {
                    "title": result.title if hasattr(result, 'title') else "Unknown Source",
                    "url": getattr(result, 'url', None) or getattr(result, 'link', ''),
                    "credibility": result.credibility_score if hasattr(result, 'credibility_score') else 0.5
                }
                sources.append(source)
            except Exception as e:
                research_logger.error(f"Error processing search result: {str(e)}")
                # Add a minimal valid source
                sources.append({
                    "title": "Source",
                    "url": "",
                    "credibility": 0.3
                })
        
        # Create the initial report object with empty content
        report = {
            "query": query,
            "content": "",
            "sources": sources,
            "timestamp": st.session_state.get("current_timestamp", "")
        }
        
        # Generate the report content in streaming mode
        for chunk in model_api.generate_streaming_research_report(prompt, temperature=0.7):
            if chunk:
                # Append chunk to the report content
                report["content"] += chunk
                # Yield the updated report
                yield {"chunk": chunk, "report": report}
        
        research_logger.info(f"Successfully generated streaming report with {len(report['content'])} characters")
        
    except Exception as e:
        research_logger.error(f"Error generating streaming report: {str(e)}")
        yield {"error": f"Error generating report: {str(e)}"} 