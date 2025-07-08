import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import quote_plus, urljoin
import logging
from typing import List, Dict, Optional
import re
import config
import nltk

class GoogleScraper:
    """
    Professional Google SERP scraper for SEO analysis
    Handles rate limiting, user agent rotation, and content extraction
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = config.USER_AGENTS
        self.current_ua_index = 0
        self.request_delay = config.REQUEST_DELAY
        self.timeout = config.REQUEST_TIMEOUT
        self.max_retries = config.MAX_RETRIES
        self.retry_delay = config.RETRY_DELAY
        self.last_request_time = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Setup session headers
        self.setup_session()
        
        # Initialize rate limiting
        self.request_times = []
        self.rate_limit_window = 60  # 1 minute window
        self.max_requests_per_window = 10  # Maximum requests per minute
        
    def wait_for_rate_limit(self):
        """Implement rate limiting with sliding window"""
        current_time = time.time()
        
        # Remove old requests from window
        self.request_times = [t for t in self.request_times 
                            if current_time - t < self.rate_limit_window]
        
        # If we've hit the rate limit, wait
        if len(self.request_times) >= self.max_requests_per_window:
            wait_time = self.request_times[0] + self.rate_limit_window - current_time
            if wait_time > 0:
                self.logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
        
        # Add current request to window
        self.request_times.append(current_time)
        
    def make_request(self, url: str, method: str = 'get', **kwargs) -> requests.Response:
        """
        Make HTTP request with exponential backoff retry logic
        
        Args:
            url: URL to request
            method: HTTP method (get, post, etc.)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException after all retries fail
        """
        retry_count = 0
        last_exception = None
        
        while retry_count <= self.max_retries:
            try:
                # Implement rate limiting
                self.wait_for_rate_limit()
                
                # Add random delay between requests
                self.add_request_delay()
                
                # Rotate user agent
                self.rotate_user_agent()
                
                # Make request
                response = getattr(self.session, method.lower())(url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                
                return response
                
            except requests.RequestException as e:
                retry_count += 1
                last_exception = e
                
                if retry_count <= self.max_retries:
                    # Calculate exponential backoff delay
                    delay = min(300, self.retry_delay * (2 ** (retry_count - 1))) # Max 5 minutes
                    # Add random jitter
                    delay += random.uniform(0, min(1, delay * 0.1))
                    
                    self.logger.warning(
                        f"Request failed (attempt {retry_count}/{self.max_retries}): {str(e)}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )
                    
                    time.sleep(delay)
                    continue
                    
        # If we get here, all retries failed
        raise last_exception
        
    def setup_session(self):
        """Configure session with appropriate headers"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        self.session.headers['User-Agent'] = self.user_agents[self.current_ua_index]
        
    def add_request_delay(self):
        """Add random delay between requests"""
        delay = self.request_delay + random.uniform(0, 2)
        time.sleep(delay)
        
    def scrape_google_results(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Scrape Google search results for given query
        
        Args:
            query: Search query string
            num_results: Number of results to retrieve (default: 10)
            
        Returns:
            List of dictionaries containing search result data
        """
        results = []
        
        try:
            # Prepare search URL
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
            
            self.logger.info(f"Scraping Google results for: {query}")
            
            # Make request with retry logic
            response = self.make_request(search_url)
            
            # Parse results
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find search result containers
            result_containers = soup.find_all('div', class_='g')
            
            for i, container in enumerate(result_containers[:num_results]):
                result_data = self.extract_result_data(container, i + 1)
                if result_data:
                    results.append(result_data)
                    
            self.logger.info(f"Successfully scraped {len(results)} results")
            
        except requests.RequestException as e:
            self.logger.error(f"Request error while scraping Google: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error while scraping Google: {str(e)}")
            
        return results
        
    def extract_result_data(self, container, position: int) -> Optional[Dict]:
        """
        Extract data from individual search result container
        
        Args:
            container: BeautifulSoup element containing search result
            position: Position in search results (1-based)
            
        Returns:
            Dictionary with extracted result data or None
        """
        try:
            # Extract title
            title_element = container.find('h3')
            title = title_element.get_text() if title_element else "No title"
            
            # Extract URL
            link_element = container.find('a')
            url = link_element.get('href') if link_element else None
            
            # Clean up URL (remove Google redirect)
            if url:
                url = self.clean_google_url(url)
                
            # Extract description/snippet
            description_element = container.find('span', {'data-ved': True})
            if not description_element:
                # Try alternative selectors
                description_element = container.find('div', class_=['VwiC3b', 'yXK7lf'])
            
            description = description_element.get_text() if description_element else "No description"
            
            # Extract domain
            domain = self.extract_domain_from_url(url) if url else "Unknown domain"
            
            result_data = {
                'position': position,
                'title': title.strip(),
                'url': url,
                'description': description.strip(),
                'domain': domain
            }
            
            return result_data
            
        except Exception as e:
            self.logger.warning(f"Error extracting result data: {str(e)}")
            return None
            
    def clean_google_url(self, url: str) -> str:
        """
        Clean Google redirect URLs to get actual URLs
        
        Args:
            url: Raw URL from Google search result
            
        Returns:
            Cleaned URL
        """
        if url.startswith('/url?'):
            # Extract actual URL from Google redirect
            import urllib.parse
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            if 'q' in parsed:
                return parsed['q'][0]
        
        return url
        
    def extract_domain_from_url(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: Full URL
            
        Returns:
            Domain name
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return "Unknown domain"
            
    def extract_content_from_url(self, url: str) -> Optional[str]:
        """
        Extract visible text content from webpage
        
        Args:
            url: URL to scrape content from
            
        Returns:
            Extracted text content or None
        """
        try:
            self.logger.info(f"Extracting content from: {url}")
            
            # Make request with retry logic
            response = self.make_request(url)
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            text = self.clean_extracted_text(text)
            
            return text
            
        except requests.RequestException as e:
            self.logger.warning(f"Request error extracting content from {url}: {str(e)}")
        except Exception as e:
            self.logger.warning(f"Error extracting content from {url}: {str(e)}")
            
        return None
        
    def clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep letters, numbers, and basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', ' ', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
        
    def scrape_with_serpapi(self, query: str, api_key: str, num_results: int = 10) -> List[Dict]:
        """
        Alternative scraping method using SerpAPI (for premium users)
        
        Args:
            query: Search query
            api_key: SerpAPI key
            num_results: Number of results
            
        Returns:
            List of search results
        """
        try:
            import serpapi
            
            search = serpapi.GoogleSearch({
                "q": query,
                "api_key": api_key,
                "num": num_results
            })
            
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            
            formatted_results = []
            for i, result in enumerate(organic_results):
                formatted_result = {
                    'position': i + 1,
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'description': result.get('snippet', ''),
                    'domain': self.extract_domain_from_url(result.get('link', ''))
                }
                formatted_results.append(formatted_result)
                
            return formatted_results
            
        except ImportError:
            self.logger.error("SerpAPI not installed. Install with: pip install google-search-results")
        except Exception as e:
            self.logger.error(f"SerpAPI error: {str(e)}")
            
        return []
        
    def get_page_metadata(self, url: str) -> Dict:
        """
        Extract metadata from webpage (title, description, keywords)
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'h1_tags': [],
            'h2_tags': [],
            'h3_tags': []
        }
        
        try:
            # Make request with retry logic
            response = self.make_request(url)
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
                
            # Extract meta description
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '').strip()
                
            # Extract meta keywords
            meta_keywords = soup.find('meta', {'name': 'keywords'})
            if meta_keywords:
                metadata['keywords'] = meta_keywords.get('content', '').strip()
                
            # Extract heading tags
            for level in ['h1', 'h2', 'h3']:
                tags = soup.find_all(level)
                metadata[f'{level}_tags'] = [tag.get_text().strip() for tag in tags]
                
        except Exception as e:
            self.logger.warning(f"Error extracting metadata from {url}: {str(e)}")
            
        return metadata
        
    def batch_scrape_urls(self, urls: List[str], batch_size: int = 5) -> Dict[str, str]:
        """
        Batch scrape content from multiple URLs with memory management
        
        Args:
            urls: List of URLs to scrape
            batch_size: Number of URLs to process in each batch
            
        Returns:
            Dictionary mapping URLs to extracted content
        """
        results = {}
        
        # Process URLs in batches
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(urls) + batch_size - 1)//batch_size}")
            
            for url in batch:
                try:
                    content = self.extract_content_from_url(url)
                    if content:
                        results[url] = content
                except Exception as e:
                    self.logger.error(f"Error processing URL {url}: {str(e)}")
                    continue
                
            # Add extra delay between batches
            if i + batch_size < len(urls):
                delay = random.uniform(2, 5)
                self.logger.info(f"Batch complete. Waiting {delay:.1f} seconds before next batch...")
                time.sleep(delay)
                
        return results
        
    def search_local_results(self, query: str, location: str, num_results: int = 10) -> List[Dict]:
        """
        Search for local business results
        
        Args:
            query: Search query
            location: Location for local search
            num_results: Number of results
            
        Returns:
            List of local search results
        """
        # Combine query with location
        local_query = f"{query} near {location}"
        
        # Use regular search with location modifier
        return self.scrape_google_results(local_query, num_results)
        
    def get_featured_snippet(self, query: str) -> Optional[Dict]:
        """
        Extract featured snippet if present in search results
        
        Args:
            query: Search query
            
        Returns:
            Featured snippet data or None
        """
        try:
            encoded_query = quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            self.rotate_user_agent()
            self.add_request_delay()
            
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for featured snippet containers
            snippet_selectors = [
                'div[data-attrid="wa:/description"]',
                'div.kp-blk',
                'div.xpdopen'
            ]
            
            for selector in snippet_selectors:
                snippet = soup.select_one(selector)
                if snippet:
                    return {
                        'text': snippet.get_text().strip(),
                        'source': 'Featured Snippet'
                    }
                    
        except Exception as e:
            self.logger.warning(f"Error extracting featured snippet: {str(e)}")
            
        return None