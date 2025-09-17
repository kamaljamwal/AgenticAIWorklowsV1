import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from models import AgentResponse, AgentType
from config import settings
import logging

logger = logging.getLogger(__name__)

class APIAgent(BaseAgent):
    """Agent for making API calls to external services"""
    
    def __init__(self):
        super().__init__(AgentType.API)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to API calls"""
        api_keywords = [
            'api', 'endpoint', 'rest', 'http', 'get', 'post', 'put', 'delete',
            'json', 'xml', 'response', 'request', 'service', 'web service',
            'fetch', 'call', 'invoke'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in api_keywords)
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Make API calls based on query"""
        try:
            # Extract API information from query
            api_info = self._parse_api_query(query)
            
            if not api_info.get('url'):
                return self.create_response(
                    success=False,
                    data=[],
                    error="No valid API URL found in query"
                )
            
            # Ensure session is available
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            results = []
            
            # Make API call
            async with self.session.request(
                method=api_info.get('method', 'GET'),
                url=api_info['url'],
                headers=api_info.get('headers', {}),
                params=api_info.get('params', {}),
                json=api_info.get('body') if api_info.get('method', 'GET').upper() in ['POST', 'PUT', 'PATCH'] else None,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/json' in content_type:
                    data = await response.json()
                else:
                    data = await response.text()
                
                result = {
                    'url': api_info['url'],
                    'method': api_info.get('method', 'GET'),
                    'status_code': response.status,
                    'content_type': content_type,
                    'data': data,
                    'headers': dict(response.headers),
                    'success': 200 <= response.status < 300
                }
                
                results.append(result)
            
            return self.create_response(
                success=True,
                data=results,
                metadata={'api_calls_made': 1}
            )
            
        except Exception as e:
            self.logger.error(f"API call failed: {str(e)}")
            return self.create_response(
                success=False,
                data=[],
                error=f"API call failed: {str(e)}"
            )
    
    def _parse_api_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query to extract API call information"""
        api_info = {}
        query_lower = query.lower()
        
        # Extract URL
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, query)
        if urls:
            api_info['url'] = urls[0]
        
        # Extract HTTP method
        if 'post' in query_lower:
            api_info['method'] = 'POST'
        elif 'put' in query_lower:
            api_info['method'] = 'PUT'
        elif 'delete' in query_lower:
            api_info['method'] = 'DELETE'
        elif 'patch' in query_lower:
            api_info['method'] = 'PATCH'
        else:
            api_info['method'] = 'GET'
        
        # Extract headers (basic parsing)
        if 'header' in query_lower or 'authorization' in query_lower:
            api_info['headers'] = {'Content-Type': 'application/json'}
            if 'bearer' in query_lower:
                # This is a placeholder - in real implementation, you'd need to handle auth properly
                api_info['headers']['Authorization'] = 'Bearer YOUR_TOKEN_HERE'
        
        # Extract parameters (basic parsing)
        if 'param' in query_lower or 'query' in query_lower:
            # This is a simplified parameter extraction
            # In a real implementation, you'd want more sophisticated parsing
            api_info['params'] = {}
        
        return api_info
    
    async def make_custom_api_call(self, url: str, method: str = 'GET', 
                                 headers: Optional[Dict[str, str]] = None,
                                 params: Optional[Dict[str, Any]] = None,
                                 body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a custom API call with specified parameters"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers or {},
                params=params or {},
                json=body if method.upper() in ['POST', 'PUT', 'PATCH'] else None,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/json' in content_type:
                    data = await response.json()
                else:
                    data = await response.text()
                
                return {
                    'url': url,
                    'method': method,
                    'status_code': response.status,
                    'content_type': content_type,
                    'data': data,
                    'headers': dict(response.headers),
                    'success': 200 <= response.status < 300
                }
                
        except Exception as e:
            return {
                'url': url,
                'method': method,
                'error': str(e),
                'success': False
            }
    
    async def health_check(self) -> bool:
        """Check API agent health"""
        try:
            # Test with a simple HTTP request
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get('https://httpbin.org/status/200', timeout=aiohttp.ClientTimeout(total=5)) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"API agent health check failed: {str(e)}")
            return False
