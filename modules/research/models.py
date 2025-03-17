"""
Data models for the research module.
"""

from typing import Dict, Optional
from datetime import datetime
import validators
import config
from utils.logger import research_logger
from utils.search import extract_domain, get_domain_credibility

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """
    Parse a date string into a standardized ISO format.
    
    Args:
        date_str: A string representing a date
        
    Returns:
        ISO formatted date string or None if parsing fails
    """
    if not date_str:
        return None
        
    try:
        # Try to parse with dateutil
        from dateutil import parser
        date = parser.parse(date_str)
        return date.isoformat()
    except:
        # If parsing fails, return the original string
        return date_str

class SearchResult:
    """Class to represent a search result with metadata"""
    def __init__(self, title, link=None, url=None, snippet="", source="web", credibility_score=0.5, date=None):
        self.title = title
        # Handle both link and url parameters for flexibility
        self.url = url if url is not None else link
        self.link = self.url  # For backward compatibility
        self.snippet = snippet
        self.source = source
        self.credibility_score = credibility_score
        self.date = date
    
    def __str__(self):
        return f"{self.title} ({self.url})"
    
    def get(self, key, default=None):
        """Allow dictionary-like access for compatibility with raw API results"""
        if key == "title":
            return self.title
        elif key in ["url", "link"]:
            return self.url
        elif key == "snippet":
            return self.snippet
        elif key == "source":
            return self.source
        elif key == "credibility_score":
            return self.credibility_score
        elif key == "date":
            return self.date
        return default

    def _calculate_credibility(self) -> float:
        """Calculate the credibility score for this search result."""
        score = 0.0
        domain = self._extract_domain()
        
        # 1. Domain authority - using the utility function
        domain_score = get_domain_credibility(domain)
        score += domain_score * config.CREDIBILITY_WEIGHTS['domain_authority']
        
        # 2. Content freshness - improved with more nuanced date evaluation
        if self.date:
            try:
                date = datetime.fromisoformat(self.date)
                days_old = (datetime.now() - date).days
                
                # Different freshness curves for different types of content
                if domain_score > 0.8:  # Academic/scientific domains
                    # Scientific/academic content ages more slowly
                    freshness_score = max(0, 1 - (days_old / 1825))  # 5 years
                elif domain_score > 0.7:  # News domains
                    # News content ages quickly
                    freshness_score = max(0, 1 - (days_old / 30))  # 1 month
                else:
                    # Default aging
                    freshness_score = max(0, 1 - (days_old / 365))  # 1 year
                
                score += freshness_score * config.CREDIBILITY_WEIGHTS['freshness']
            except ValueError:
                score += 0.5 * config.CREDIBILITY_WEIGHTS['freshness']
        
        # 3. Content quality indicators
        snippet = self.snippet or ""
        
        # Check for citations/references patterns
        citations_indicators = ["cited by", "references", "bibliography", "et al.", "according to", 
                               "[1]", "[2]", "doi:", "doi.org", "pmid:", "isbn:"]
        has_citations = any(indicator in snippet.lower() for indicator in citations_indicators)
        if has_citations:
            score += 0.7 * config.CREDIBILITY_WEIGHTS['citations']
        
        # Check for academic/professional language
        academic_indicators = ["study", "research", "analysis", "evidence", "data", "findings", 
                              "methodology", "conclusion", "results show", "published in"]
        academic_score = sum(1 for indicator in academic_indicators if indicator in snippet.lower()) / len(academic_indicators)
        score += academic_score * config.CREDIBILITY_WEIGHTS['content_quality']
        
        # 4. Author credentials (if available)
        author_indicators = ["professor", "dr.", "phd", "md", "researcher", "scientist", 
                            "expert", "specialist", "author", "journalist", "editor"]
        has_author_credentials = any(indicator in snippet.lower() for indicator in author_indicators)
        if has_author_credentials:
            score += 0.7 * config.CREDIBILITY_WEIGHTS['author_credentials']
        
        # Ensure score is between 0.1 and 1.0
        return max(0.1, min(1.0, score))

    def _extract_domain(self) -> str:
        """Extract domain from the link."""
        return extract_domain(self.link)

    def to_dict(self) -> Dict:
        """Convert the search result to a dictionary."""
        return {
            'title': self.title,
            'link': self.link,
            'snippet': self.snippet,
            'date': self.date,
            'credibility_score': self.credibility_score
        } 