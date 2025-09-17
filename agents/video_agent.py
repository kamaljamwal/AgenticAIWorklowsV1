import asyncio
import os
import re
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from models import AgentResponse, AgentType
from config import settings
from content_processor import content_processor, content_index
import logging

# Optional imports
try:
    import yt_dlp
    HAS_YT_DLP = True
except ImportError:
    HAS_YT_DLP = False
    logging.warning("yt-dlp not available. YouTube functionality will be limited.")

logger = logging.getLogger(__name__)

class VideoAgent(BaseAgent):
    """Agent for extracting content and answering questions from configured video sources"""
    
    def __init__(self):
        super().__init__(AgentType.VIDEO)
        self.video_sources = settings.video_sources
        self.youtube_channels = settings.video_youtube_channels
        self.youtube_playlists = settings.video_youtube_playlists
        self.local_paths = settings.video_local_paths
        self.supported_formats = settings.video_supported_formats
        self.content_cache = {}
        
        # Initialize content from configured sources
        asyncio.create_task(self._initialize_content())
        
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True
        } if HAS_YT_DLP else None
    
    async def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to video content"""
        video_keywords = [
            'video', 'youtube', 'vimeo', 'mp4', 'avi', 'mov', 'mkv',
            'watch', 'stream', 'movie', 'clip', 'tutorial', 'webinar',
            'recording', 'media', 'playlist', 'channel'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in video_keywords)
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Search for content and answer questions based on video sources"""
        try:
            # Search for relevant content chunks from video sources
            relevant_chunks = content_index.search_chunks(query, ['video'], max_results)
            
            results = []
            for chunk in relevant_chunks:
                result = {
                    'source': chunk.source,
                    'content': chunk.content,
                    'metadata': chunk.metadata,
                    'relevance_type': 'content_match',
                    'chunk_id': chunk.chunk_id
                }
                results.append(result)
            
            # If no content found, try to extract from configured sources
            if not results:
                await self._refresh_content()
                relevant_chunks = content_index.search_chunks(query, ['video'], max_results)
                
                for chunk in relevant_chunks:
                    result = {
                        'source': chunk.source,
                        'content': chunk.content,
                        'metadata': chunk.metadata,
                        'relevance_type': 'content_match',
                        'chunk_id': chunk.chunk_id
                    }
                    results.append(result)
            
            # If still no results, provide information about configured sources
            if not results:
                results = await self._get_source_info()
            
            return self.create_response(
                success=True,
                data=results,
                metadata={
                    'query': query, 
                    'total_found': len(results),
                    'configured_sources': len(self.youtube_channels) + len(self.youtube_playlists) + len(self.local_paths)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Video content search failed: {str(e)}")
            return self.create_response(
                success=False,
                data=[],
                error=f"Video content search failed: {str(e)}"
            )
    
    async def _initialize_content(self):
        """Initialize content from configured video sources"""
        try:
            # Process YouTube channels
            for channel_id in self.youtube_channels:
                await self._process_youtube_channel(channel_id)
            
            # Process YouTube playlists
            for playlist_id in self.youtube_playlists:
                await self._process_youtube_playlist(playlist_id)
            
            # Process local video files
            for path in self.local_paths:
                await self._process_local_videos(path)
                
            self.logger.info(f"Initialized content from {len(self.youtube_channels)} channels, {len(self.youtube_playlists)} playlists, and {len(self.local_paths)} local paths")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize video content: {str(e)}")
    
    async def _refresh_content(self):
        """Refresh content from sources"""
        await self._initialize_content()
    
    async def _process_youtube_channel(self, channel_id: str):
        """Process videos from a YouTube channel"""
        if not HAS_YT_DLP:
            self.logger.warning("yt-dlp not available for YouTube processing")
            return
            
        try:
            channel_url = f"https://www.youtube.com/channel/{channel_id}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                channel_info = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ydl.extract_info(channel_url, download=False)
                )
                
                if channel_info and 'entries' in channel_info:
                    for entry in channel_info['entries'][:10]:  # Limit to recent 10 videos
                        if entry:
                            await self._extract_video_content(entry)
                            
        except Exception as e:
            self.logger.error(f"Failed to process YouTube channel {channel_id}: {str(e)}")
    
    async def _process_youtube_playlist(self, playlist_id: str):
        """Process videos from a YouTube playlist"""
        if not HAS_YT_DLP:
            return
            
        try:
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                playlist_info = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ydl.extract_info(playlist_url, download=False)
                )
                
                if playlist_info and 'entries' in playlist_info:
                    for entry in playlist_info['entries']:
                        if entry:
                            await self._extract_video_content(entry)
                            
        except Exception as e:
            self.logger.error(f"Failed to process YouTube playlist {playlist_id}: {str(e)}")
    
    async def _process_local_videos(self, path: str):
        """Process local video files"""
        try:
            video_path = Path(path)
            if not video_path.exists():
                self.logger.warning(f"Video path does not exist: {path}")
                return
            
            for video_file in video_path.rglob('*'):
                if video_file.is_file() and video_file.suffix.lower() in self.supported_formats:
                    await self._process_local_video_file(str(video_file))
                    
        except Exception as e:
            self.logger.error(f"Failed to process local videos in {path}: {str(e)}")
    
    async def _process_local_video_file(self, file_path: str):
        """Process a single local video file"""
        try:
            # For local files, we'll create content based on filename and metadata
            file_name = os.path.basename(file_path)
            
            # Extract content from filename (common patterns)
            content_parts = []
            content_parts.append(f"Video file: {file_name}")
            
            # Try to extract meaningful information from filename
            name_without_ext = os.path.splitext(file_name)[0]
            # Replace common separators with spaces
            readable_name = re.sub(r'[_\-\.]+', ' ', name_without_ext)
            content_parts.append(f"Title: {readable_name}")
            
            # Get file metadata
            stat = os.stat(file_path)
            content_parts.append(f"File size: {stat.st_size} bytes")
            content_parts.append(f"Modified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}")
            
            content = '\n'.join(content_parts)
            
            # Create content chunks
            chunks = content_processor.process_video_content(
                file_path,
                content,
                {
                    'file_path': file_path,
                    'file_name': file_name,
                    'file_size': stat.st_size,
                    'source_type': 'local_video'
                }
            )
            
            content_index.add_chunks(chunks)
            self.logger.debug(f"Processed local video: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to process local video file {file_path}: {str(e)}")
    
    async def _extract_video_content(self, video_entry: Dict[str, Any]):
        """Extract content from a video entry"""
        try:
            video_url = video_entry.get('webpage_url', video_entry.get('url', ''))
            title = video_entry.get('title', 'Unknown Title')
            description = video_entry.get('description', '')
            
            # Build content from available metadata
            content_parts = []
            content_parts.append(f"Title: {title}")
            
            if description:
                content_parts.append(f"Description: {description}")
            
            # Add other metadata
            if video_entry.get('uploader'):
                content_parts.append(f"Channel: {video_entry['uploader']}")
            
            if video_entry.get('duration'):
                content_parts.append(f"Duration: {self._format_duration(video_entry['duration'])}")
            
            if video_entry.get('upload_date'):
                content_parts.append(f"Upload Date: {video_entry['upload_date']}")
            
            if video_entry.get('tags'):
                content_parts.append(f"Tags: {', '.join(video_entry['tags'][:10])}")
            
            content = '\n'.join(content_parts)
            
            # Try to get subtitles/transcript if available
            transcript = await self._get_video_transcript(video_url)
            if transcript:
                content += f"\n\nTranscript:\n{transcript}"
            
            # Create content chunks
            chunks = content_processor.process_video_content(
                video_url,
                content,
                {
                    'title': title,
                    'url': video_url,
                    'platform': 'YouTube',
                    'uploader': video_entry.get('uploader', ''),
                    'duration': video_entry.get('duration'),
                    'upload_date': video_entry.get('upload_date', ''),
                    'view_count': video_entry.get('view_count', 0)
                }
            )
            
            content_index.add_chunks(chunks)
            self.logger.debug(f"Extracted content from video: {title}")
            
        except Exception as e:
            self.logger.error(f"Failed to extract video content: {str(e)}")
    
    async def _get_video_transcript(self, video_url: str) -> str:
        """Get transcript/subtitles for a video"""
        if not HAS_YT_DLP:
            return ""
            
        try:
            transcript_opts = {
                **self.ydl_opts,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'skip_download': True
            }
            
            with yt_dlp.YoutubeDL(transcript_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: ydl.extract_info(video_url, download=False)
                )
                
                # Extract subtitle text if available
                if info and 'subtitles' in info:
                    for lang, subs in info['subtitles'].items():
                        if subs and len(subs) > 0:
                            # This is a simplified approach - in practice you'd need to
                            # download and parse the subtitle files
                            return "[Subtitles available but not extracted in this demo]"
                
                return ""
                
        except Exception as e:
            self.logger.debug(f"Could not get transcript for {video_url}: {str(e)}")
            return ""
    
    async def _get_source_info(self) -> List[Dict[str, Any]]:
        """Get information about configured sources"""
        sources = []
        
        if self.youtube_channels:
            sources.append({
                'type': 'youtube_channels',
                'count': len(self.youtube_channels),
                'description': f"Configured to monitor {len(self.youtube_channels)} YouTube channels",
                'channels': self.youtube_channels[:3]  # Show first 3
            })
        
        if self.youtube_playlists:
            sources.append({
                'type': 'youtube_playlists',
                'count': len(self.youtube_playlists),
                'description': f"Configured to monitor {len(self.youtube_playlists)} YouTube playlists",
                'playlists': self.youtube_playlists[:3]
            })
        
        if self.local_paths:
            sources.append({
                'type': 'local_videos',
                'count': len(self.local_paths),
                'description': f"Configured to scan {len(self.local_paths)} local video directories",
                'paths': self.local_paths
            })
        
        if not sources:
            sources.append({
                'type': 'configuration_needed',
                'description': "No video sources configured. Please update your .env file with video sources.",
                'example_config': {
                    'VIDEO_YOUTUBE_CHANNELS': 'UC_channel_id1,UC_channel_id2',
                    'VIDEO_YOUTUBE_PLAYLISTS': 'PLplaylist_id1,PLplaylist_id2',
                    'VIDEO_LOCAL_PATHS': 'C:/Videos/Training,C:/Videos/Tutorials'
                }
            })
        
        return sources
    
    async def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed video content"""
        video_chunks = content_index.get_chunks_by_type('video')
        
        sources = {}
        for chunk in video_chunks:
            source = chunk.metadata.get('platform', 'unknown')
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        return {
            'total_chunks': len(video_chunks),
            'sources': sources,
            'configured_channels': len(self.youtube_channels),
            'configured_playlists': len(self.youtube_playlists),
            'configured_local_paths': len(self.local_paths)
        }
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract video URLs from text"""
        url_pattern = r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|vimeo\.com/|dailymotion\.com/video/)[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    def _format_duration(self, duration: int) -> str:
        """Format duration from seconds to readable format"""
        if not duration:
            return "Unknown"
        
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def _get_platform_from_url(self, url: str) -> str:
        """Determine platform from URL"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'YouTube'
        elif 'vimeo.com' in url:
            return 'Vimeo'
        elif 'dailymotion.com' in url:
            return 'Dailymotion'
        else:
            return 'Unknown'
    
    async def health_check(self) -> bool:
        """Check video agent health"""
        try:
            # Check if we have any configured sources
            if not (self.youtube_channels or self.youtube_playlists or self.local_paths):
                self.logger.warning("No video sources configured")
                return False
            
            # Check if yt-dlp is available for YouTube sources
            if (self.youtube_channels or self.youtube_playlists) and not HAS_YT_DLP:
                self.logger.warning("yt-dlp not available for YouTube sources")
                return False
            
            # Check if local paths exist
            for path in self.local_paths:
                if not Path(path).exists():
                    self.logger.warning(f"Local video path does not exist: {path}")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Video agent health check failed: {str(e)}")
            return False
