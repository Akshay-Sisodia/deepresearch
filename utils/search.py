"""
Search functionality for Deep Research Assistant.

Note: This module is deprecated and has been moved to modules/research.
It is kept for backward compatibility.
"""

import http.client
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse
import config
from datetime import datetime, timedelta
import validators
from utils.logger import search_logger

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """
    Parse various date formats into ISO format.
    Handles relative dates (e.g., "2 days ago") and common formats.
    """
    if not date_str:
        return None
        
    try:
        # Handle relative dates
        if 'ago' in date_str.lower():
            match = re.match(r'(\d+)\s*(day|days|hour|hours|minute|minutes|second|seconds)\s*ago', date_str.lower())
            if match:
                number = int(match.group(1))
                unit = match.group(2)
                now = datetime.now()
                if 'day' in unit:
                    return (now - timedelta(days=number)).isoformat()
                elif 'hour' in unit:
                    return (now - timedelta(hours=number)).isoformat()
                elif 'minute' in unit:
                    return (now - timedelta(minutes=number)).isoformat()
                elif 'second' in unit:
                    return (now - timedelta(seconds=number)).isoformat()
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S%z'
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.isoformat()
            except ValueError:
                continue
                
        # If no format matches, try to extract date-like patterns
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{4}/\d{2}/\d{2}',
            r'\d{2}/\d{2}/\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    parsed_date = datetime.strptime(match.group(0), '%Y-%m-%d')
                    return parsed_date.isoformat()
                except ValueError:
                    continue
        
        return None
        
    except Exception:
        return None

def extract_domain(url):
    """
    Extract domain from URL in a robust way
    
    Args:
        url: The URL to extract domain from
        
    Returns:
        The domain name or empty string if extraction fails
    """
    if not url:
        return ""
        
    try:
        # Handle URLs without protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Remove www. prefix if present
        domain = re.sub(r'^www\.', '', domain)
        
        return domain.lower()
    except:
        # Fallback to simple extraction
        parts = url.split('/')
        if len(parts) > 2:
            domain = parts[2]
            return domain.lower()
        return ""

def get_domain_credibility(domain):
    """
    Get credibility score for a domain
    
    Args:
        domain: The domain to evaluate
        
    Returns:
        A credibility score between 0 and 1
    """
    if not domain:
        return config.DOMAIN_CREDIBILITY['default']
        
    # Get TLD
    tld = domain.split('.')[-1] if '.' in domain else ''
    
    # Check for specific domains first
    reputable_domains = {
        "wikipedia.org": 0.9,
        "nature.com": 0.95, 
        "science.org": 0.95,
        "nih.gov": 0.95,
        "cdc.gov": 0.95,
        "who.int": 0.95,
        "ieee.org": 0.9,
        "acm.org": 0.9,
        "mit.edu": 0.95,
        "harvard.edu": 0.95,
        "stanford.edu": 0.95,
        "arxiv.org": 0.85,
        "jstor.org": 0.85,
        "sciencedirect.com": 0.85,
        "springer.com": 0.85,
        "wiley.com": 0.85,
        "ncbi.nlm.nih.gov": 0.95,
        "pubmed.gov": 0.95
    }
    
    # Credible news sources
    news_domains = {
        "reuters.com": 0.85,
        "apnews.com": 0.85,
        "bbc.com": 0.8,
        "nytimes.com": 0.8,
        "wsj.com": 0.8,
        "economist.com": 0.85,
        "ft.com": 0.8,
        "bloomberg.com": 0.8
    }
    
    # Less reliable domains
    less_reliable_domains = {
        "wordpress.com": -0.2,
        "blogspot.com": -0.2,
        "medium.com": -0.1,
        "substack.com": -0.1,
        "facebook.com": -0.3,
        "twitter.com": -0.2,
        "instagram.com": -0.3,
        "tiktok.com": -0.3,
        "reddit.com": -0.1
    }
    
    # Check for exact domain matches
    for d, score in reputable_domains.items():
        if domain == d or domain.endswith('.' + d):
            return score
            
    for d, score in news_domains.items():
        if domain == d or domain.endswith('.' + d):
            return score
    
    # Apply TLD-based scoring
    base_score = config.DOMAIN_CREDIBILITY.get(tld, config.DOMAIN_CREDIBILITY['default'])
    
    # Apply penalties for less reliable domains
    for d, penalty in less_reliable_domains.items():
        if domain == d or domain.endswith('.' + d):
            return max(0.1, base_score + penalty)
    
    return base_score

class SearchResult:
    def __init__(self, title: str, link: str, snippet: str, date: Optional[str] = None):
        self.title = title
        self.link = link
        self.snippet = snippet
        self.date = parse_date(date)  # Parse date during initialization
        self.credibility_score = self._calculate_credibility()

    def _calculate_credibility(self) -> float:
        """Calculate the credibility score for this search result."""
        score = 0.0
        domain = self._extract_domain()

        # Domain authority
        domain_score = get_domain_credibility(domain)
        score += domain_score * config.CREDIBILITY_WEIGHTS['domain_authority']

        # Content freshness
        if self.date:
            try:
                date = datetime.fromisoformat(self.date)
                days_old = (datetime.now() - date).days
                freshness_score = max(0, 1 - (days_old / 365))
                score += freshness_score * config.CREDIBILITY_WEIGHTS['freshness']
            except ValueError:
                score += 0.5 * config.CREDIBILITY_WEIGHTS['freshness']

        return min(1.0, score)

    def _extract_domain(self) -> str:
        """Extract domain from the link."""
        if validators.url(self.link):
            return self.link.split('/')[2]
        return ""

    def to_dict(self) -> Dict:
        """Convert the search result to a dictionary."""
        return {
            'title': self.title,
            'link': self.link,
            'snippet': self.snippet,
            'date': self.date,
            'credibility_score': self.credibility_score
        }

class SearchAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.host = "google.serper.dev"
        self.headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        search_logger.info("SearchAPI initialized")

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """
        Perform a search using the Serper API.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        search_logger.info(f"Performing search for query: {query}")
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
            
            search_logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            search_logger.error(f"Search API error: {str(e)}")
            return []
        finally:
            if conn:
                conn.close() 