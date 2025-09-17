import asyncio
import time
from typing import List, Dict, Any, Optional
from agents.jira_agent import JiraAgent
from agents.github_agent import GitHubAgent
from agents.api_agent import APIAgent
from agents.filesystem_agent import FileSystemAgent
from agents.video_agent import VideoAgent
from agents.s3_agent import S3Agent
from agents.url_agent import URLAgent
from models import QueryRequest, WorkflowResponse, AgentResponse, AgentType
from config import settings
from llm_client import get_llm_client
import logging

logger = logging.getLogger(__name__)

class AgenticOrchestrator:
    """Main orchestrator that manages all agents and workflows"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        try:
            self.agents[AgentType.JIRA] = JiraAgent()
            self.agents[AgentType.GITHUB] = GitHubAgent()
            self.agents[AgentType.API] = APIAgent()
            self.agents[AgentType.FILESYSTEM] = FileSystemAgent()
            self.agents[AgentType.VIDEO] = VideoAgent()
            self.agents[AgentType.S3] = S3Agent()
            self.agents[AgentType.URL] = URLAgent()
            
            logger.info(f"Initialized {len(self.agents)} agents")
        except Exception as e:
            logger.error(f"Failed to initialize agents: {str(e)}")
    
    async def process_query(self, request: QueryRequest) -> WorkflowResponse:
        """Process a natural language query using appropriate agents"""
        start_time = time.time()
        
        try:
            # Determine which agents are relevant for this query
            relevant_agents = await self._determine_relevant_agents(request.prompt, request.specific_sources)
            
            if not relevant_agents:
                return WorkflowResponse(
                    query=request.prompt,
                    agents_used=[],
                    results=[],
                    summary="No relevant agents found for this query.",
                    total_results=0,
                    execution_time=time.time() - start_time
                )
            
            # Execute searches with relevant agents in parallel
            agent_tasks = []
            for agent_type in relevant_agents:
                agent = self.agents[agent_type]
                task = asyncio.create_task(
                    agent.search(request.prompt, request.max_results),
                    name=f"{agent_type.value}_search"
                )
                agent_tasks.append((agent_type, task))
            
            # Wait for all agent searches to complete
            results = []
            for agent_type, task in agent_tasks:
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    logger.error(f"Agent {agent_type.value} failed: {str(e)}")
                    # Create error response for failed agent
                    error_response = AgentResponse(
                        agent_type=agent_type,
                        success=False,
                        data=[],
                        error=str(e)
                    )
                    results.append(error_response)
            
            # Generate summary using AI if available
            summary = await self._generate_summary(request.prompt, results)
            
            # Calculate total results
            total_results = sum(len(result.data) for result in results if result.success)
            
            return WorkflowResponse(
                query=request.prompt,
                agents_used=relevant_agents,
                results=results,
                summary=summary,
                total_results=total_results,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return WorkflowResponse(
                query=request.prompt,
                agents_used=[],
                results=[],
                summary=f"Query processing failed: {str(e)}",
                total_results=0,
                execution_time=time.time() - start_time
            )
    
    async def _determine_relevant_agents(self, query: str, specific_sources: Optional[List[AgentType]] = None) -> List[AgentType]:
        """Determine which agents are relevant for the given query"""
        if specific_sources:
            # If specific sources are requested, use only those
            return [agent_type for agent_type in specific_sources if agent_type in self.agents]
        
        relevant_agents = []
        
        # Check each agent's relevance
        for agent_type, agent in self.agents.items():
            try:
                if await agent.is_relevant(query):
                    relevant_agents.append(agent_type)
            except Exception as e:
                logger.error(f"Failed to check relevance for {agent_type.value}: {str(e)}")
        
        # If no agents are relevant, use AI to determine relevance (if available)
        if not relevant_agents and self.openai_client:
            relevant_agents = await self._ai_determine_relevance(query)
        
        # Fallback: if still no relevant agents, use all available agents
        if not relevant_agents:
            relevant_agents = list(self.agents.keys())
            logger.warning(f"No relevant agents found, using all available agents for query: {query}")
        
        return relevant_agents
    
    async def _ai_determine_relevance(self, query: str) -> List[AgentType]:
        """Use AI to determine which agents are relevant for the query"""
        try:
            prompt = f"""
            Given the following query, determine which data sources would be most relevant to search.
            
            Query: "{query}"
            
            Available data sources:
            - JIRA: For project management, issues, tickets, bugs, stories, tasks
            - GITHUB: For code repositories, pull requests, issues, commits
            - API: For making HTTP requests to external services
            - FILESYSTEM: For local files and directories
            - VIDEO: For video content, YouTube, Vimeo, etc.
            - S3: For AWS S3 bucket objects and files
            - URL: For web pages and online content
            
            Respond with a comma-separated list of relevant sources (e.g., "JIRA,GITHUB,API").
            If unsure, include multiple sources.
            """
            
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            ai_response = response.strip()
            
            # Parse AI response
            suggested_agents = []
            for agent_name in ai_response.split(','):
                agent_name = agent_name.strip().upper()
                try:
                    agent_type = AgentType(agent_name.lower())
                    if agent_type in self.agents:
                        suggested_agents.append(agent_type)
                except ValueError:
                    continue
            
            return suggested_agents
            
        except Exception as e:
            logger.error(f"AI relevance determination failed: {str(e)}")
            return []
    
    async def _generate_summary(self, query: str, results: List[AgentResponse]) -> str:
        """Generate a summary of the search results"""
        if not self.llm_client:
            return self._generate_basic_summary(results)
        
        try:
            # Prepare results summary for AI
            results_summary = []
            for result in results:
                if result.success and result.data:
                    results_summary.append({
                        'agent': result.agent_type.value,
                        'count': len(result.data),
                        'sample_data': result.data[:2] if result.data else []  # First 2 items as sample
                    })
                elif not result.success:
                    results_summary.append({
                        'agent': result.agent_type.value,
                        'error': result.error
                    })
            
            prompt = f"""
            Summarize the following search results for the query: "{query}"
            
            Results: {results_summary}
            
            Provide a concise summary that:
            1. Mentions which sources were searched
            2. Highlights key findings
            3. Notes any errors or limitations
            4. Suggests next steps if relevant
            
            Keep the summary under 200 words.
            """
            
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.3
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {str(e)}")
            return self._generate_basic_summary(results)
    
    def _generate_basic_summary(self, results: List[AgentResponse]) -> str:
        """Generate a basic summary without AI"""
        successful_agents = [r.agent_type.value for r in results if r.success]
        failed_agents = [r.agent_type.value for r in results if not r.success]
        total_results = sum(len(r.data) for r in results if r.success)
        
        summary_parts = []
        
        if successful_agents:
            summary_parts.append(f"Successfully searched: {', '.join(successful_agents)}")
        
        if failed_agents:
            summary_parts.append(f"Failed to search: {', '.join(failed_agents)}")
        
        summary_parts.append(f"Total results found: {total_results}")
        
        return ". ".join(summary_parts) + "."
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all agents"""
        health_status = {}
        
        for agent_type, agent in self.agents.items():
            try:
                is_healthy = await agent.health_check()
                health_status[agent_type.value] = {
                    'healthy': is_healthy,
                    'status': 'OK' if is_healthy else 'ERROR'
                }
            except Exception as e:
                health_status[agent_type.value] = {
                    'healthy': False,
                    'status': 'ERROR',
                    'error': str(e)
                }
        
        overall_health = all(status['healthy'] for status in health_status.values())
        
        return {
            'overall_healthy': overall_health,
            'agents': health_status,
            'openai_configured': self.openai_client is not None
        }
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get information about agent capabilities"""
        capabilities = {}
        
        for agent_type, agent in self.agents.items():
            capabilities[agent_type.value] = {
                'description': self._get_agent_description(agent_type),
                'keywords': self._get_agent_keywords(agent_type)
            }
        
        return capabilities
    
    def _get_agent_description(self, agent_type: AgentType) -> str:
        """Get description for an agent type"""
        descriptions = {
            AgentType.JIRA: "Search JIRA issues, projects, and tickets",
            AgentType.GITHUB: "Search GitHub repositories, issues, and pull requests",
            AgentType.API: "Make HTTP requests to external APIs",
            AgentType.FILESYSTEM: "Search local files and directories",
            AgentType.VIDEO: "Search and extract information from video content",
            AgentType.S3: "Search AWS S3 bucket objects and files",
            AgentType.URL: "Fetch and parse content from web URLs"
        }
        return descriptions.get(agent_type, "Unknown agent")
    
    def _get_agent_keywords(self, agent_type: AgentType) -> List[str]:
        """Get keywords that trigger an agent"""
        keywords = {
            AgentType.JIRA: ['jira', 'issue', 'ticket', 'bug', 'story', 'task'],
            AgentType.GITHUB: ['github', 'repository', 'pull request', 'commit', 'code'],
            AgentType.API: ['api', 'http', 'rest', 'endpoint', 'service'],
            AgentType.FILESYSTEM: ['file', 'folder', 'directory', 'local', 'disk'],
            AgentType.VIDEO: ['video', 'youtube', 'vimeo', 'movie', 'clip'],
            AgentType.S3: ['s3', 'bucket', 'aws', 'cloud storage'],
            AgentType.URL: ['url', 'website', 'web page', 'link', 'scrape']
        }
        return keywords.get(agent_type, [])
