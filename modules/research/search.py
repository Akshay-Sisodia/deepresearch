"""
Search functionality for the research module.
"""

import json
import http.client
from typing import List, Optional
import streamlit as st
from utils.logger import research_logger, search_logger, app_logger
from modules.research.models import SearchResult
from utils.cache import search_cache
from datetime import datetime
from dateutil import parser
from utils.search import extract_domain, get_domain_credibility

class SearchAPI:
    """
    API client for performing web searches.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.host = "google.serper.dev"
        self.headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        research_logger.info("SearchAPI initialized")

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Perform a search using the Serper API.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        research_logger.info(f"Performing search for query: {query}")
        conn = None
        try:
            conn = http.client.HTTPSConnection(self.host)
            payload = json.dumps({
                "q": query,
                "num": num_results
            })
            
            conn.request("POST", "/search", payload, self.headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            
            results = []
            for item in data.get('organic', []):
                result = SearchResult(
                    title=item.get('title', ''),
                    link=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    date=item.get('date')
                )
                results.append(result)
            
            research_logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            research_logger.error(f"Search API error: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()

class SearchResult:
    """Class to represent a search result with metadata"""
    def __init__(self, title, url, snippet, source="web", credibility_score=0.5):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source
        self.credibility_score = credibility_score
    
    def __str__(self):
        return f"{self.title} ({self.url})"

@st.cache_resource
def initialize_search_api():
    """Initialize and cache the search API instance"""
    try:
        import os
        import streamlit as st
        
        # First try to get from Streamlit secrets
        api_key = st.secrets.get("SERPER_API_KEY")
        
        # If not found in secrets, try environment variables
        if not api_key:
            api_key = os.getenv("SERPER_API_KEY")
            
        if not api_key:
            research_logger.error("SERPER_API_KEY not found in secrets or environment variables")
            return None
        else:
            research_logger.info("SERPER_API_KEY found, initializing search API")
            
        search_api = SearchAPI(api_key)
        research_logger.info("Initialized SearchAPI")
        return search_api
    except Exception as e:
        research_logger.error(f"Error initializing search API: {str(e)}")
        return None

def generate_search_queries(model_api, original_query: str, num_queries: int = 3, current_date: str = None) -> List[str]:
    """
    Generate multiple search queries based on the original query using the LLM.
    
    Args:
        model_api: The model API instance
        original_query: The original research query
        num_queries: Number of search queries to generate
        current_date: Current date string in YYYY-MM-DD format
        
    Returns:
        List of search query strings
    """
    search_logger.info(f"Generating {num_queries} search queries for: {original_query}")
    
    # Get current date for context if not provided
    if not current_date:
        current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create the prompt for the model
    prompt = f"""Today is {current_date}. I need to research the following question:

"{original_query}"

Generate {num_queries} different search queries that would help gather diverse and relevant information about this topic.

Requirements for the search queries:
1. Each query should be a clear, concise search term (not a complete sentence or question)
2. Focus on keywords and specific terms that search engines respond well to
3. Cover different aspects of the original question
4. Include any necessary context or time-relevant information
5. DO NOT include any articles (a, an, the) unless absolutely necessary
6. DO NOT use punctuation like question marks, periods, or quotation marks
7. Keep each query between 3-7 words for optimal search results

Format your response as a JSON array of strings, each containing one search query.
Example: ["machine learning applications healthcare", "AI medical diagnosis current research", "deep learning radiology examples"]
"""
    
    try:
        # Generate the search queries
        response = model_api.generate_search_queries(prompt)
        
        # Parse the response as JSON
        if isinstance(response, str):
            # Try to extract JSON array from the response if it contains other text
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            queries = json.loads(response)
        elif isinstance(response, list):
            queries = response
        else:
            search_logger.error(f"Unexpected response type: {type(response)}")
            # Fallback to original query
            return [original_query]
        
        # Ensure we have the right format
        if not isinstance(queries, list):
            search_logger.error("Response is not a list")
            return [original_query]
        
        # Filter out any non-string items
        queries = [q for q in queries if isinstance(q, str)]
        
        # Ensure we have at least one query
        if not queries:
            search_logger.error("No valid queries generated")
            return [original_query]
        
        search_logger.info(f"Generated {len(queries)} search queries")
        for i, q in enumerate(queries):
            search_logger.debug(f"Query {i+1}: {q}")
        
        return queries
    
    except Exception as e:
        search_logger.error(f"Error generating search queries: {str(e)}")
        # Fallback to original query
        return [original_query]

def search_web(model_api, query: str, num_queries: int = 3, results_per_query: int = 5) -> List[SearchResult]:
    """
    Search the web using multiple queries generated from the original query.
    
    Args:
        model_api: The model API instance
        query: The original research query
        num_queries: Number of search queries to generate
        results_per_query: Number of results to return per query
        
    Returns:
        List of deduplicated SearchResult objects
    """
    search_logger.info(f"Performing multi-query search for: {query}")
    
    # Check cache first for the original query
    cached_results = search_cache.get(query)
    if cached_results:
        search_logger.info(f"Cache hit for query: {query}")
        return cached_results
    
    # Get current date for context
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Generate multiple search queries with current date
    search_queries = generate_search_queries(model_api, query, num_queries, current_date)
    
    # Initialize search API if not already done
    search_api = initialize_search_api()
    if not search_api:
        search_logger.error("Search API not initialized")
        return []
    
    all_results = []
    seen_urls = set()
    
    # Perform search for each query
    for i, search_query in enumerate(search_queries):
        search_logger.info(f"Searching with query {i+1}/{len(search_queries)}: {search_query}")
        
        try:
            # Perform the search
            results = search_api.search(search_query, num_results=results_per_query)
            
            # Deduplicate results based on URL
            for result in results:
                url = getattr(result, 'url', None) or getattr(result, 'link', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)
            
            search_logger.info(f"Found {len(results)} results for query {i+1}, {len(all_results)} unique results so far")
            
        except Exception as e:
            search_logger.error(f"Error searching for query {i+1}: {str(e)}")
    
    # Cache the combined results
    search_cache.set(query, all_results)
    
    search_logger.info(f"Multi-query search completed with {len(all_results)} unique results")
    return all_results

def calculate_credibility_score(result: dict) -> float:
    """
    Calculate a credibility score for a search result
    
    This uses a comprehensive heuristic approach that evaluates multiple factors
    
    Args:
        result: The raw search result
        
    Returns:
        A credibility score between 0 and 1
    """
    # Start with a base score
    score = 0.5
    
    # Get the URL and domain
    url = result.get("link", "")
    domain = extract_domain(url)
    
    # 1. Domain authority evaluation
    domain_score = get_domain_credibility(domain)
    score = domain_score
    
    # 2. Content quality indicators
    snippet = result.get("snippet", "")
    
    # Check for citations/references patterns
    citations_indicators = ["cited by", "references", "bibliography", "et al.", "according to", 
                           "[1]", "[2]", "doi:", "doi.org", "pmid:", "isbn:"]
    has_citations = any(indicator in snippet.lower() for indicator in citations_indicators)
    if has_citations:
        score += 0.15
    
    # Check for academic/professional language
    academic_indicators = ["study", "research", "analysis", "evidence", "data", "findings", 
                          "methodology", "conclusion", "results show", "published in"]
    academic_score = sum(1 for indicator in academic_indicators if indicator in snippet.lower()) / len(academic_indicators)
    score += academic_score * 0.15
    
    # 3. Author credentials (if available)
    author_indicators = ["professor", "dr.", "phd", "md", "researcher", "scientist", 
                        "expert", "specialist", "author", "journalist", "editor"]
    has_author_credentials = any(indicator in snippet.lower() for indicator in author_indicators)
    if has_author_credentials:
        score += 0.1
    
    # 4. Content length and depth
    if len(snippet) > 300:
        score += 0.1
    elif len(snippet) > 200:
        score += 0.05
    
    # 5. Date evaluation (if available)
    date_str = result.get("date", "")
    if date_str:
        try:
            # Try to parse the date - format may vary
            date = parser.parse(date_str)
            days_old = (datetime.now() - date).days
            
            # Different freshness curves for different types of content
            if domain_score > 0.8:  # Academic/scientific domains
                # Scientific/academic content ages more slowly
                freshness_score = max(0, 0.1 * (1 - (days_old / 1825)))  # 5 years
            elif domain_score > 0.7:  # News domains
                # News content ages quickly
                freshness_score = max(0, 0.1 * (1 - (days_old / 30)))  # 1 month
            else:
                # Default aging
                freshness_score = max(0, 0.1 * (1 - (days_old / 365)))  # 1 year
                
            score += freshness_score
        except:
            # If date parsing fails, don't adjust score
            pass
    
    # Ensure score is between 0.1 and 0.9
    return max(0.1, min(0.9, score)) 