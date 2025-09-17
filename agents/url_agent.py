import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from models import AgentResponse, AgentType
import logging
import re

logger = logging.getLogger(__name__)

class URLAgent(BaseAgent):
    """Agent for fetching and parsing content from URLs"""
    
    def __init__(self):
        super().__init__(AgentType.URL)
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to URL operations"""
        url_keywords = [
            'url', 'website', 'web', 'http', 'https', 'link', 'page',
            'scrape', 'fetch', 'download', 'crawl', 'parse', 'extract',
            'content', 'html', 'site'
        ]
        query_lower = query.lower()
        
        # Also check if query contains actual URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        has_urls = bool(re.search(url_pattern, query))
        
        return has_urls or any(keyword in query_lower for keyword in url_keywords)
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Fetch and parse content from URLs based on query"""
        try:
            # Ensure session is available
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            # Extract URLs from query
            urls = self._extract_urls(query)
            
            if not urls:
                return self.create_response(
                    success=False,
                    data=[],
                    error="No valid URLs found in query"
                )
            
            results = []
            
            # Process each URL
            for url in urls[:max_results]:
                url_content = await self._fetch_url_content(url)
                if url_content:
                    results.append(url_content)
            
            return self.create_response(
                success=True,
                data=results,
                metadata={'urls_processed': len(results), 'total_urls_found': len(urls)}
            )
            
        except Exception as e:
            self.logger.error(f"URL processing failed: {str(e)}")
            return self.create_response(
                success=False,
                data=[],
                error=f"URL processing failed: {str(e)}"
            )
    
    async def _fetch_url_content(self, url: str) -> Dict[str, Any]:
        """Fetch and parse content from a single URL"""
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                content_type = response.headers.get('content-type', '').lower()
                status_code = response.status
                
                if status_code >= 400:
                    return {
                        'url': url,
                        'title': None,
                        'content': f'HTTP Error: {status_code}',
                        'content_type': content_type,
                        'status_code': status_code,
                        'last_accessed': asyncio.get_event_loop().time(),
                        'error': f'HTTP {status_code}'
                    }
                
                # Handle different content types
                if 'text/html' in content_type:
                    content = await self._parse_html_content(response, url)
                elif 'application/json' in content_type:
                    json_data = await response.json()
                    content = {
                        'type': 'json',
                        'data': json_data,
                        'formatted': self._format_json(json_data)
                    }
                elif 'text/' in content_type:
                    text_content = await response.text()
                    content = {
                        'type': 'text',
                        'text': text_content[:5000] + '...' if len(text_content) > 5000 else text_content
                    }
                else:
                    content = {
                        'type': 'binary',
                        'size': len(await response.read()),
                        'message': f'Binary content ({content_type})'
                    }
                
                return {
                    'url': url,
                    'title': content.get('title') if isinstance(content, dict) else None,
                    'content': content,
                    'content_type': content_type,
                    'status_code': status_code,
                    'last_accessed': asyncio.get_event_loop().time()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {str(e)}")
            return {
                'url': url,
                'title': None,
                'content': f'Error: {str(e)}',
                'content_type': 'error',
                'status_code': 0,
                'last_accessed': asyncio.get_event_loop().time(),
                'error': str(e)
            }
    
    async def _parse_html_content(self, response, url: str) -> Dict[str, Any]:
        """Parse HTML content and extract useful information"""
        try:
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = None
            if soup.title:
                title = soup.title.string.strip()
            
            # Extract meta description
            description = None
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '').strip()
            
            # Extract main content (remove script, style, nav, footer, etc.)
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Get text content
            text_content = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length
            if len(text_content) > 5000:
                text_content = text_content[:5000] + '...'
            
            # Extract links
            links = []
            for link in soup.find_all('a', href=True)[:20]:  # Limit to first 20 links
                href = link['href']
                link_text = link.get_text().strip()
                if href and link_text:
                    absolute_url = urljoin(url, href)
                    links.append({
                        'url': absolute_url,
                        'text': link_text
                    })
            
            # Extract images
            images = []
            for img in soup.find_all('img', src=True)[:10]:  # Limit to first 10 images
                src = img['src']
                alt = img.get('alt', '').strip()
                absolute_url = urljoin(url, src)
                images.append({
                    'url': absolute_url,
                    'alt': alt
                })
            
            return {
                'type': 'html',
                'title': title,
                'description': description,
                'text_content': text_content,
                'links': links,
                'images': images,
                'word_count': len(text_content.split())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse HTML from {url}: {str(e)}")
            return {
                'type': 'html',
                'title': None,
                'error': str(e)
            }
    
    def _format_json(self, json_data: Any) -> str:
        """Format JSON data for display"""
        try:
            import json
            return json.dumps(json_data, indent=2)[:2000] + '...' if len(str(json_data)) > 2000 else json.dumps(json_data, indent=2)
        except Exception:
            return str(json_data)[:2000] + '...' if len(str(json_data)) > 2000 else str(json_data)
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            try:
                parsed = urlparse(url)
                if parsed.scheme and parsed.netloc:
                    valid_urls.append(url)
            except Exception:
                continue
        
        return valid_urls
    
    async def fetch_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch content from multiple URLs concurrently"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        
        tasks = [self._fetch_url_content(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                self.logger.error(f"URL fetch failed: {str(result)}")
        
        return valid_results
    
    async def check_url_status(self, url: str) -> Dict[str, Any]:
        """Check if a URL is accessible"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return {
                    'url': url,
                    'status_code': response.status,
                    'accessible': 200 <= response.status < 400,
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': response.headers.get('content-length'),
                    'last_modified': response.headers.get('last-modified'),
                    'success': True
                }
                
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'accessible': False,
                'success': False
            }
    
    async def health_check(self) -> bool:
        """Check URL agent health"""
        try:
            # Test with a simple HTTP request
            if not self.session:
                self.session = aiohttp.ClientSession(headers=self.headers)
            
            async with self.session.get('https://httpbin.org/status/200', timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"URL agent health check failed: {str(e)}")
            return False
