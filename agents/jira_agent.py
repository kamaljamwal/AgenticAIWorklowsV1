import asyncio
from typing import List, Dict, Any
from jira import JIRA
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from models import AgentResponse, AgentType
from config import settings
from content_processor import content_processor, content_index
import logging

logger = logging.getLogger(__name__)

class JiraAgent(BaseAgent):
    """Agent for searching JIRA issues and projects"""
    
    def __init__(self):
        super().__init__(AgentType.JIRA)
        self.jira_client = None
        self.projects = settings.jira_projects or []
        self.content_refresh_interval = settings.content_refresh_hours * 3600  # Convert to seconds
        self.last_refresh = 0
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize JIRA client"""
        try:
            if settings.jira_server and settings.jira_email and settings.jira_api_token:
                self.jira_client = JIRA(
                    server=settings.jira_server,
                    basic_auth=(settings.jira_email, settings.jira_api_token)
                )
                self.logger.info("JIRA client initialized successfully")
            else:
                self.logger.warning("JIRA credentials not configured")
        except Exception as e:
            self.logger.error(f"Failed to initialize JIRA client: {str(e)}")
    
    async def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to JIRA"""
        jira_keywords = [
            'jira', 'issue', 'ticket', 'bug', 'story', 'task', 'epic',
            'sprint', 'project', 'assignee', 'status', 'priority',
            'backlog', 'board', 'workflow'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in jira_keywords)
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Search JIRA content based on query"""
        if not self.jira_client:
            return self.create_response(
                success=False,
                data=[],
                error="JIRA client not initialized. Please check configuration."
            )
        
        try:
            # Refresh content if needed
            await self._refresh_content_if_needed()
            
            # Search indexed content
            jira_chunks = content_index.search_chunks(query, content_type='jira', max_results=max_results)
            
            if not jira_chunks:
                return self.create_response(
                    success=True,
                    data=[],
                    message="No JIRA content found matching your query. Try refreshing content or check if JIRA projects are configured."
                )
            
            # Format results
            results = []
            for chunk in jira_chunks:
                results.append({
                    'content': chunk.content,
                    'source': chunk.source,
                    'metadata': chunk.metadata,
                    'relevance_score': chunk.relevance_score,
                    'chunk_id': chunk.chunk_id
                })
            
            return self.create_response(
                success=True,
                data=results,
                message=f"Found {len(results)} JIRA content matches"
            )
            
        except Exception as e:
            self.logger.error(f"JIRA search failed: {str(e)}")
            return self.create_response(
                success=False,
                data=[],
                error=f"JIRA search failed: {str(e)}"
            )
        
    
    async def _refresh_content_if_needed(self):
        """Refresh JIRA content if needed"""
        import time
        current_time = time.time()
        
        if current_time - self.last_refresh > self.content_refresh_interval:
            await self.refresh_content()
            self.last_refresh = current_time
    
    async def refresh_content(self):
        """Refresh JIRA content from configured projects"""
        if not self.jira_client:
            self.logger.warning("JIRA client not initialized")
            return
        
        try:
            self.logger.info("Refreshing JIRA content...")
            
            for project_key in self.projects:
                await self._process_project(project_key)
            
            self.logger.info(f"JIRA content refresh completed for {len(self.projects)} projects")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh JIRA content: {str(e)}")
    
    async def _process_project(self, project_key: str):
        """Process all issues in a JIRA project"""
        try:
            # Get all issues in the project (limit to recent ones for performance)
            jql = f"project = {project_key} ORDER BY updated DESC"
            
            issues = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.jira_client.search_issues(jql, maxResults=settings.max_items_per_source or 100)
            )
            
            for issue in issues:
                await self._extract_issue_content(issue)
                
            self.logger.debug(f"Processed {len(issues)} issues from project {project_key}")
            
        except Exception as e:
            self.logger.error(f"Failed to process JIRA project {project_key}: {str(e)}")
    
    async def _extract_issue_content(self, issue):
        """Extract content from a JIRA issue"""
        try:
            # Build content from issue fields
            content_parts = []
            content_parts.append(f"Issue: {issue.key}")
            content_parts.append(f"Summary: {issue.fields.summary}")
            
            if hasattr(issue.fields, 'description') and issue.fields.description:
                content_parts.append(f"Description: {issue.fields.description}")
            
            content_parts.append(f"Status: {issue.fields.status.name}")
            content_parts.append(f"Type: {issue.fields.issuetype.name}")
            
            if issue.fields.assignee:
                content_parts.append(f"Assignee: {issue.fields.assignee.displayName}")
            
            if issue.fields.priority:
                content_parts.append(f"Priority: {issue.fields.priority.name}")
            
            # Add comments if available
            if hasattr(issue.fields, 'comment') and issue.fields.comment.comments:
                comments = []
                for comment in issue.fields.comment.comments[-3:]:  # Last 3 comments
                    comments.append(f"{comment.author.displayName}: {comment.body}")
                if comments:
                    content_parts.append(f"Recent Comments: {'; '.join(comments)}")
            
            content = '\n'.join(content_parts)
            
            # Create content chunks
            chunks = content_processor.process_jira_content(
                f"{settings.jira_server}/browse/{issue.key}",
                content,
                {
                    'issue_key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'issue_type': issue.fields.issuetype.name,
                    'project': issue.fields.project.key,
                    'created': str(issue.fields.created),
                    'updated': str(issue.fields.updated),
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                    'priority': issue.fields.priority.name if issue.fields.priority else None
                }
            )
            
            content_index.add_chunks(chunks)
            self.logger.debug(f"Extracted content from issue: {issue.key}")
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from JIRA issue: {str(e)}")
    
    async def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed JIRA content"""
        jira_chunks = content_index.get_chunks_by_type('jira')
        
        projects = {}
        statuses = {}
        issue_types = {}
        
        for chunk in jira_chunks:
            # Count by project
            project = chunk.metadata.get('project', 'unknown')
            if project not in projects:
                projects[project] = 0
            projects[project] += 1
            
            # Count by status
            status = chunk.metadata.get('status', 'unknown')
            if status not in statuses:
                statuses[status] = 0
            statuses[status] += 1
            
            # Count by issue type
            issue_type = chunk.metadata.get('issue_type', 'unknown')
            if issue_type not in issue_types:
                issue_types[issue_type] = 0
            issue_types[issue_type] += 1
        
        return {
            'total_chunks': len(jira_chunks),
            'projects': projects,
            'statuses': statuses,
            'issue_types': issue_types,
            'configured_projects': len(self.projects)
        }
    
    async def health_check(self) -> bool:
        """Check JIRA agent health"""
        try:
            # Check if JIRA client is initialized
            if not self.jira_client:
                self.logger.warning("JIRA client not initialized")
                return False
            
            # Check if projects are configured
            if not self.projects:
                self.logger.warning("No JIRA projects configured")
                return False
            
            # Try to get server info
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.jira_client.server_info()
            )
            
            return True
        except Exception as e:
            self.logger.error(f"JIRA health check failed: {str(e)}")
            return False
