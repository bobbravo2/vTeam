"""Core plugin interface for framework plugins."""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List
from pydantic import BaseModel

from llama_index.core.workflow import Context


class PluginEvent(BaseModel):
    """Standard plugin event format for UI integration."""
    framework: str
    type: str  # 'streaming', 'complete', 'error'
    component: str  # 'analysis', 'synthesis', etc.
    data: Dict[str, Any]
    timestamp: str


class PluginWorkflow(ABC):
    """Base interface for framework plugins."""
    
    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Framework identifier (e.g., 'openhands', 'langchain', 'crewai')."""
        pass
    
    @property 
    @abstractmethod
    def supported_granularities(self) -> List[str]:
        """Component granularities this plugin supports.
        
        Examples: ['full_workflow', 'analysis', 'synthesis', 'artifact_generation']
        """
        pass
    
    @abstractmethod
    async def execute_component(
        self, 
        component: str,
        input_data: Dict[str, Any],
        agent_manager: Any,  # RFEAgentManager type hint would create circular import
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute a workflow component with streaming events.
        
        Args:
            component: Component to execute ('full_workflow', 'analysis', etc.)
            input_data: Input data including user input and context
            agent_manager: RFEAgentManager instance for persona access
            context: LlamaIndex workflow context
            
        Yields:
            PluginEvent: Streaming events compatible with UI
        """
        pass
    
    @abstractmethod
    async def get_agent_mapping(self) -> Dict[str, str]:
        """Get mapping from RFE agent personas to framework-specific agents.
        
        Returns:
            Dict mapping RFE persona keys to framework agent identifiers
        """
        pass


class PluginError(Exception):
    """Base exception for plugin-related errors."""
    
    def __init__(self, framework: str, message: str, component: str = None):
        self.framework = framework
        self.component = component
        super().__init__(f"{framework}: {message}")


class PluginExecutionError(PluginError):
    """Error during plugin execution."""
    pass


class PluginConfigurationError(PluginError):
    """Error in plugin configuration."""
    pass