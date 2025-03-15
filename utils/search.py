import http.client
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import validators
import config
from utils.logger import search_logger
import re

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
        
        search_logger.warning(f"Could not parse date: {date_str}")
        return None
        
    except Exception as e:
        search_logger.error(f"Error parsing date '{date_str}': {str(e)}")
        return None

class SearchResult:
    def __init__(self, title: str, link: str, snippet: str, date: Optional[str] = None):
        self.title = title
        self.link = link
        self.snippet = snippet
        self.date = parse_date(date)  # Parse date during initialization
        self.credibility_score = self._calculate_credibility()
        search_logger.debug(f"Created SearchResult: {title} with credibility score: {self.credibility_score}")

    def _calculate_credibility(self) -> float:
        """Calculate the credibility score for this search result."""
        score = 0.0
        domain = self._extract_domain()
        search_logger.debug(f"Calculating credibility for domain: {domain}")

        # Domain authority
        domain_score = config.DOMAIN_CREDIBILITY.get(
            domain.split('.')[-1].lower() if domain and '.' in domain else '',
            config.DOMAIN_CREDIBILITY['default']
        )
        score += domain_score * config.CREDIBILITY_WEIGHTS['domain_authority']

        # Content freshness
        if self.date:
            try:
                date = datetime.fromisoformat(self.date)
                days_old = (datetime.now() - date).days
                freshness_score = max(0, 1 - (days_old / 365))
                score += freshness_score * config.CREDIBILITY_WEIGHTS['freshness']
                search_logger.debug(f"Content age: {days_old} days, freshness score: {freshness_score}")
            except ValueError:
                search_logger.warning(f"Could not parse date: {self.date}")
                score += 0.5 * config.CREDIBILITY_WEIGHTS['freshness']

        return min(1.0, score)

    def _extract_domain(self) -> str:
        """Extract domain from the link."""
        if validators.url(self.link):
            return self.link.split('/')[2]
        search_logger.warning(f"Invalid URL: {self.link}")
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
        try:
            conn = http.client.HTTPSConnection(self.host)
            payload = json.dumps({
                "q": query,
                "num": num_results
            })
            
            search_logger.debug(f"Search payload: {payload}")
            conn.request("POST", "/search", payload, self.headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            
            search_logger.debug(f"Search response status: {response.status}")
            
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
            search_logger.error(f"Search API error: {str(e)}", exc_info=True)
            return []
        finally:
            conn.close() 