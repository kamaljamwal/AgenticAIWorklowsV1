"""
Content processing utilities for extracting and chunking content from various sources
"""

import os
import re
import hashlib
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContentChunk:
    """Represents a chunk of content with metadata"""
    
    def __init__(self, content: str, source: str, source_type: str, metadata: Dict[str, Any] = None):
        self.content = content
        self.source = source
        self.source_type = source_type
        self.metadata = metadata or {}
        self.chunk_id = self._generate_chunk_id()
        self.created_at = datetime.now().isoformat()
    
    def _generate_chunk_id(self) -> str:
        """Generate a unique ID for this chunk"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()[:8]
        source_hash = hashlib.md5(self.source.encode()).hexdigest()[:8]
        return f"{self.source_type}_{source_hash}_{content_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary"""
        return {
            'chunk_id': self.chunk_id,
            'content': self.content,
            'source': self.source,
            'source_type': self.source_type,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'content_length': len(self.content)
        }

class ContentProcessor:
    """Process and chunk content from various sources"""
    
    def __init__(self, chunk_size: int = 1000, overlap_size: int = 200):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
    
    def chunk_text(self, text: str, source: str, source_type: str, metadata: Dict[str, Any] = None) -> List[ContentChunk]:
        """Split text into overlapping chunks"""
        if not text or len(text) < self.chunk_size:
            return [ContentChunk(text, source, source_type, metadata)]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_end = self._find_sentence_boundary(text, start, end)
                if sentence_end > start:
                    end = sentence_end
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    'chunk_start': start,
                    'chunk_end': end,
                    'chunk_index': len(chunks)
                })
                
                chunks.append(ContentChunk(chunk_text, source, source_type, chunk_metadata))
            
            # Move start position with overlap
            start = max(start + self.chunk_size - self.overlap_size, end)
        
        return chunks
    
    def _find_sentence_boundary(self, text: str, start: int, preferred_end: int) -> int:
        """Find a good sentence boundary near the preferred end"""
        # Look for sentence endings within a reasonable range
        search_start = max(start, preferred_end - 100)
        search_end = min(len(text), preferred_end + 100)
        
        # Look for sentence endings
        sentence_endings = ['.', '!', '?', '\n\n']
        best_pos = preferred_end
        
        for ending in sentence_endings:
            pos = text.rfind(ending, search_start, search_end)
            if pos > search_start:
                best_pos = pos + 1
                break
        
        return best_pos
    
    def process_file_content(self, file_path: str, content: str) -> List[ContentChunk]:
        """Process content from a file"""
        metadata = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_extension': os.path.splitext(file_path)[1],
            'file_size': len(content)
        }
        
        return self.chunk_text(content, file_path, 'file', metadata)
    
    def process_url_content(self, url: str, content: str, title: str = None) -> List[ContentChunk]:
        """Process content from a URL"""
        metadata = {
            'url': url,
            'title': title,
            'domain': self._extract_domain(url)
        }
        
        return self.chunk_text(content, url, 'url', metadata)
    
    def process_api_content(self, endpoint: str, content: str, response_metadata: Dict[str, Any] = None) -> List[ContentChunk]:
        """Process content from an API response"""
        metadata = {
            'endpoint': endpoint,
            'response_metadata': response_metadata or {}
        }
        
        # If content is JSON, convert to readable text
        if isinstance(content, dict):
            content = self._dict_to_text(content)
        elif isinstance(content, list):
            content = '\n'.join([self._dict_to_text(item) if isinstance(item, dict) else str(item) for item in content])
        
        return self.chunk_text(str(content), endpoint, 'api', metadata)
    
    def process_video_content(self, video_source: str, transcript: str, video_metadata: Dict[str, Any] = None) -> List[ContentChunk]:
        """Process content from video transcripts"""
        metadata = {
            'video_source': video_source,
            'video_metadata': video_metadata or {}
        }
        
        return self.chunk_text(transcript, video_source, 'video', metadata)
    
    def process_jira_content(self, issue_key: str, content: str, issue_metadata: Dict[str, Any] = None) -> List[ContentChunk]:
        """Process content from JIRA issues"""
        metadata = {
            'issue_key': issue_key,
            'issue_metadata': issue_metadata or {}
        }
        
        return self.chunk_text(content, issue_key, 'jira', metadata)
    
    def process_github_content(self, repo_path: str, content: str, github_metadata: Dict[str, Any] = None) -> List[ContentChunk]:
        """Process content from GitHub"""
        metadata = {
            'repo_path': repo_path,
            'github_metadata': github_metadata or {}
        }
        
        return self.chunk_text(content, repo_path, 'github', metadata)
    
    def process_s3_content(self, s3_key: str, content: str, s3_metadata: Dict[str, Any] = None) -> List[ContentChunk]:
        """Process content from S3 objects"""
        metadata = {
            's3_key': s3_key,
            's3_metadata': s3_metadata or {}
        }
        
        return self.chunk_text(content, s3_key, 's3', metadata)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc
    
    def _dict_to_text(self, data: dict) -> str:
        """Convert dictionary to readable text"""
        lines = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}: {str(value)}")
            else:
                lines.append(f"{key}: {value}")
        return '\n'.join(lines)

class ContentIndex:
    """Simple in-memory content index for question answering"""
    
    def __init__(self):
        self.chunks: List[ContentChunk] = []
        self.index_by_source: Dict[str, List[ContentChunk]] = {}
        self.index_by_type: Dict[str, List[ContentChunk]] = {}
    
    def add_chunks(self, chunks: List[ContentChunk]):
        """Add chunks to the index"""
        for chunk in chunks:
            self.chunks.append(chunk)
            
            # Index by source
            if chunk.source not in self.index_by_source:
                self.index_by_source[chunk.source] = []
            self.index_by_source[chunk.source].append(chunk)
            
            # Index by type
            if chunk.source_type not in self.index_by_type:
                self.index_by_type[chunk.source_type] = []
            self.index_by_type[chunk.source_type].append(chunk)
    
    def search_chunks(self, query: str, source_types: List[str] = None, max_results: int = 10) -> List[ContentChunk]:
        """Search for relevant chunks based on query"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        scored_chunks = []
        
        # Filter by source types if specified
        search_chunks = self.chunks
        if source_types:
            search_chunks = []
            for source_type in source_types:
                search_chunks.extend(self.index_by_type.get(source_type, []))
        
        for chunk in search_chunks:
            score = self._calculate_relevance_score(chunk.content.lower(), query_words)
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and return top results
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, score in scored_chunks[:max_results]]
    
    def _calculate_relevance_score(self, content: str, query_words: set) -> float:
        """Calculate relevance score for content"""
        content_words = set(re.findall(r'\w+', content))
        
        # Exact matches
        exact_matches = len(query_words.intersection(content_words))
        
        # Partial matches (substring)
        partial_matches = 0
        for query_word in query_words:
            if any(query_word in content_word for content_word in content_words):
                partial_matches += 0.5
        
        # Phrase matches
        phrase_matches = 0
        for query_word in query_words:
            if query_word in content:
                phrase_matches += 1
        
        return exact_matches * 2 + partial_matches + phrase_matches * 0.5
    
    def get_chunks_by_source(self, source: str) -> List[ContentChunk]:
        """Get all chunks from a specific source"""
        return self.index_by_source.get(source, [])
    
    def get_chunks_by_type(self, source_type: str) -> List[ContentChunk]:
        """Get all chunks of a specific type"""
        return self.index_by_type.get(source_type, [])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            'total_chunks': len(self.chunks),
            'sources': len(self.index_by_source),
            'source_types': list(self.index_by_type.keys()),
            'chunks_by_type': {k: len(v) for k, v in self.index_by_type.items()}
        }

# Global content index instance
content_index = ContentIndex()
content_processor = ContentProcessor()
