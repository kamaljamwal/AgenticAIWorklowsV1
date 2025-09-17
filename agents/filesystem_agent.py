import os
import asyncio
import aiofiles
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from models import AgentResponse, AgentType
import logging

logger = logging.getLogger(__name__)

class FileSystemAgent(BaseAgent):
    """Agent for searching and accessing local filesystem"""
    
    def __init__(self, base_paths: List[str] = None):
        super().__init__(AgentType.FILESYSTEM)
        self.base_paths = base_paths or [os.getcwd()]
        self.allowed_extensions = {
            '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
            '.csv', '.log', '.conf', '.config', '.ini', '.env', '.dockerfile', '.sql'
        }
    
    async def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to filesystem operations"""
        fs_keywords = [
            'file', 'folder', 'directory', 'path', 'local', 'disk', 'filesystem',
            'document', 'text', 'log', 'config', 'script', 'code', 'read file',
            'find file', 'search file', 'list files'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in fs_keywords)
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Search filesystem based on query"""
        try:
            search_terms = self._extract_search_terms(query)
            results = []
            
            for base_path in self.base_paths:
                if not os.path.exists(base_path):
                    continue
                
                # Search for files and directories
                found_items = await self._search_in_directory(base_path, search_terms, max_results - len(results))
                results.extend(found_items)
                
                if len(results) >= max_results:
                    break
            
            return self.create_response(
                success=True,
                data=results[:max_results],
                metadata={'search_terms': search_terms, 'base_paths': self.base_paths}
            )
            
        except Exception as e:
            self.logger.error(f"Filesystem search failed: {str(e)}")
            return self.create_response(
                success=False,
                data=[],
                error=f"Filesystem search failed: {str(e)}"
            )
    
    async def _search_in_directory(self, directory: str, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search for files and directories matching search terms"""
        results = []
        
        try:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
                
                # Search in directory names
                for dir_name in dirs:
                    if self._matches_search_terms(dir_name, search_terms):
                        dir_path = os.path.join(root, dir_name)
                        dir_info = await self._get_directory_info(dir_path)
                        results.append(dir_info)
                        
                        if len(results) >= max_results:
                            return results
                
                # Search in file names and content
                for file_name in files:
                    if self._matches_search_terms(file_name, search_terms):
                        file_path = os.path.join(root, file_name)
                        file_info = await self._get_file_info(file_path, search_terms)
                        results.append(file_info)
                        
                        if len(results) >= max_results:
                            return results
                
        except Exception as e:
            self.logger.error(f"Error searching directory {directory}: {str(e)}")
        
        return results
    
    async def _get_file_info(self, file_path: str, search_terms: List[str]) -> Dict[str, Any]:
        """Get file information and content preview"""
        try:
            stat = os.stat(file_path)
            file_info = {
                'path': file_path,
                'name': os.path.basename(file_path),
                'type': 'file',
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': Path(file_path).suffix.lower()
            }
            
            # Add content preview for text files
            if Path(file_path).suffix.lower() in self.allowed_extensions and stat.st_size < 1024 * 1024:  # 1MB limit
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = await f.read(1000)  # First 1000 characters
                        file_info['content_preview'] = content
                        
                        # Check if content matches search terms
                        if any(term.lower() in content.lower() for term in search_terms):
                            file_info['content_match'] = True
                except Exception:
                    file_info['content_preview'] = "Could not read file content"
            
            return file_info
            
        except Exception as e:
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'type': 'file',
                'error': str(e)
            }
    
    async def _get_directory_info(self, dir_path: str) -> Dict[str, Any]:
        """Get directory information"""
        try:
            stat = os.stat(dir_path)
            file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            dir_count = len([d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))])
            
            return {
                'path': dir_path,
                'name': os.path.basename(dir_path),
                'type': 'directory',
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'file_count': file_count,
                'directory_count': dir_count
            }
            
        except Exception as e:
            return {
                'path': dir_path,
                'name': os.path.basename(dir_path),
                'type': 'directory',
                'error': str(e)
            }
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query"""
        # Remove common words
        stop_words = {'find', 'search', 'show', 'get', 'file', 'files', 'folder', 'directory', 'in', 'the', 'a', 'an'}
        words = query.lower().split()
        search_terms = [word for word in words if word not in stop_words and len(word) > 2]
        return search_terms
    
    def _matches_search_terms(self, text: str, search_terms: List[str]) -> bool:
        """Check if text matches any of the search terms"""
        text_lower = text.lower()
        return any(term.lower() in text_lower for term in search_terms)
    
    async def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read complete file content"""
        try:
            if not os.path.exists(file_path):
                return {'error': 'File not found', 'success': False}
            
            stat = os.stat(file_path)
            if stat.st_size > 10 * 1024 * 1024:  # 10MB limit
                return {'error': 'File too large to read', 'success': False}
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read()
            
            return {
                'path': file_path,
                'content': content,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    async def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """List directory contents"""
        try:
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                return {'error': 'Directory not found', 'success': False}
            
            items = []
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isfile(item_path):
                    items.append(await self._get_file_info(item_path, []))
                elif os.path.isdir(item_path):
                    items.append(await self._get_directory_info(item_path))
            
            return {
                'path': dir_path,
                'items': items,
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    async def health_check(self) -> bool:
        """Check filesystem agent health"""
        try:
            # Check if base paths are accessible
            for path in self.base_paths:
                if not os.path.exists(path) or not os.access(path, os.R_OK):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Filesystem health check failed: {str(e)}")
            return False
