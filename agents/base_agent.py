from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models import AgentResponse, AgentType
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"{__name__}.{agent_type.value}")
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Search for information based on the query"""
        pass
    
    @abstractmethod
    async def is_relevant(self, query: str) -> bool:
        """Determine if this agent is relevant for the given query"""
        pass
    
    def create_response(self, success: bool, data: List[Dict[str, Any]], 
                       error: str = None, metadata: Dict[str, Any] = None) -> AgentResponse:
        """Create a standardized agent response"""
        return AgentResponse(
            agent_type=self.agent_type,
            success=success,
            data=data,
            error=error,
            metadata=metadata
        )
    
    async def health_check(self) -> bool:
        """Check if the agent is healthy and can perform operations"""
        try:
            # Basic health check - can be overridden by specific agents
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
