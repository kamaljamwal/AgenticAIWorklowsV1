import asyncio
from typing import List, Dict, Any
from github import Github
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from models import AgentResponse, AgentType
from config import settings
from content_processor import content_processor, content_index
import logging

logger = logging.getLogger(__name__)

class GitHubAgent(BaseAgent):
    """Agent for searching GitHub repositories, issues, and pull requests"""
    
    def __init__(self):
        super().__init__(AgentType.GITHUB)
        self.github_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize GitHub client"""
        try:
            if settings.github_token:
                self.github_client = Github(settings.github_token)
                self.logger.info("GitHub client initialized successfully")
            else:
                self.logger.warning("GitHub token not configured")
        except Exception as e:
            self.logger.error(f"Failed to initialize GitHub client: {str(e)}")
    
    async def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to GitHub"""
        github_keywords = [
            'github', 'repository', 'repo', 'pull request', 'pr', 'issue',
            'commit', 'branch', 'fork', 'star', 'code', 'source',
            'git', 'merge', 'clone', 'push', 'pull'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in github_keywords)
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Search GitHub based on query"""
        if not self.github_client:
            return self.create_response(
                success=False,
                data=[],
                error="GitHub client not initialized. Please check configuration."
            )
        
        try:
            results = []
            search_query = self._extract_search_terms(query)
            
            # Search repositories
            if self._should_search_repos(query):
                repo_results = await self._search_repositories(search_query, max_results // 3)
                results.extend(repo_results)
            
            # Search issues
            if self._should_search_issues(query):
                issue_results = await self._search_issues(search_query, max_results // 3)
                results.extend(issue_results)
            
            # Search pull requests
            if self._should_search_prs(query):
                pr_results = await self._search_pull_requests(search_query, max_results // 3)
                results.extend(pr_results)
            
            # If no specific type mentioned, search all
            if not any([self._should_search_repos(query), self._should_search_issues(query), self._should_search_prs(query)]):
                repo_results = await self._search_repositories(search_query, max_results // 3)
                issue_results = await self._search_issues(search_query, max_results // 3)
                results.extend(repo_results + issue_results)
            
            # Limit results
            results = results[:max_results]
            
            return self.create_response(
                success=True,
                data=results,
                metadata={'search_query': search_query, 'total_found': len(results)}
            )
            
        except Exception as e:
            self.logger.error(f"GitHub search failed: {str(e)}")
            return self.create_response(
                success=False,
                data=[],
                error=f"GitHub search failed: {str(e)}"
            )
    
    async def _search_repositories(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search GitHub repositories"""
        results = []
        try:
            repos = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(self.github_client.search_repositories(query)[:max_results])
            )
            
            for repo in repos:
                repo_data = {
                    'type': 'repository',
                    'name': repo.full_name,
                    'url': repo.html_url,
                    'description': repo.description,
                    'created_at': repo.created_at.isoformat() if repo.created_at else None,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                    'author': repo.owner.login,
                    'language': repo.language,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'open_issues': repo.open_issues_count
                }
                results.append(repo_data)
        except Exception as e:
            self.logger.error(f"Repository search failed: {str(e)}")
        
        return results
    
    async def _search_issues(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search GitHub issues"""
        results = []
        try:
            issues = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(self.github_client.search_issues(f"{query} type:issue")[:max_results])
            )
            
            for issue in issues:
                issue_data = {
                    'type': 'issue',
                    'name': issue.title,
                    'url': issue.html_url,
                    'description': issue.body[:500] + '...' if issue.body and len(issue.body) > 500 else issue.body,
                    'created_at': issue.created_at.isoformat() if issue.created_at else None,
                    'updated_at': issue.updated_at.isoformat() if issue.updated_at else None,
                    'author': issue.user.login,
                    'state': issue.state,
                    'repository': issue.repository.full_name,
                    'labels': [label.name for label in issue.labels]
                }
                results.append(issue_data)
        except Exception as e:
            self.logger.error(f"Issue search failed: {str(e)}")
        
        return results
    
    async def _search_pull_requests(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search GitHub pull requests"""
        results = []
        try:
            prs = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: list(self.github_client.search_issues(f"{query} type:pr")[:max_results])
            )
            
            for pr in prs:
                pr_data = {
                    'type': 'pull_request',
                    'name': pr.title,
                    'url': pr.html_url,
                    'description': pr.body[:500] + '...' if pr.body and len(pr.body) > 500 else pr.body,
                    'created_at': pr.created_at.isoformat() if pr.created_at else None,
                    'updated_at': pr.updated_at.isoformat() if pr.updated_at else None,
                    'author': pr.user.login,
                    'state': pr.state,
                    'repository': pr.repository.full_name,
                    'labels': [label.name for label in pr.labels]
                }
                results.append(pr_data)
        except Exception as e:
            self.logger.error(f"Pull request search failed: {str(e)}")
        
        return results
    
    def _extract_search_terms(self, query: str) -> str:
        """Extract search terms from natural language query"""
        # Remove common words and GitHub-specific terms
        stop_words = ['find', 'search', 'show', 'get', 'github', 'repository', 'repo', 'issue', 'pull', 'request']
        words = query.lower().split()
        search_terms = [word for word in words if word not in stop_words]
        return ' '.join(search_terms)
    
    def _should_search_repos(self, query: str) -> bool:
        """Check if query is asking for repositories"""
        repo_keywords = ['repository', 'repo', 'project', 'code', 'source']
        return any(keyword in query.lower() for keyword in repo_keywords)
    
    def _should_search_issues(self, query: str) -> bool:
        """Check if query is asking for issues"""
        issue_keywords = ['issue', 'bug', 'problem', 'ticket']
        return any(keyword in query.lower() for keyword in issue_keywords)
    
    def _should_search_prs(self, query: str) -> bool:
        """Check if query is asking for pull requests"""
        pr_keywords = ['pull request', 'pr', 'merge', 'contribution']
        return any(keyword in query.lower() for keyword in pr_keywords)
    
    async def health_check(self) -> bool:
        """Check GitHub connection health"""
        if not self.github_client:
            return False
        
        try:
            # Try to get rate limit info
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.github_client.get_rate_limit()
            )
            return True
        except Exception as e:
            self.logger.error(f"GitHub health check failed: {str(e)}")
            return False
