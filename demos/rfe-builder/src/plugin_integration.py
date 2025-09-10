"""Integration module for plugin system with existing RFE workflow."""

import asyncio
from typing import Dict, List, Any, AsyncGenerator, Optional

from llama_index.core.workflow import Context
from llama_index.core.chat_ui.events import UIEvent

from plugins.base.orchestrator import MultiFrameworkOrchestrator
from plugins.openhands.openhands_plugin import OpenHandsPlugin
from plugins.langchain.langchain_plugin import LangChainPlugin
from plugins.crewai.crewai_plugin import CrewAIPlugin


class PluginIntegrationManager:
    """Manages plugin integration with the existing RFE workflow."""
    
    def __init__(self):
        self.orchestrator = MultiFrameworkOrchestrator()
        self.active_frameworks = ["llamaindex"]  # Default to LlamaIndex
        self._register_plugins()
        
    def _register_plugins(self):
        """Register all available plugins with the orchestrator."""
        try:
            self.orchestrator.register_plugin("openhands", OpenHandsPlugin())
        except ImportError:
            print("OpenHands plugin dependencies not installed")
            
        try:
            self.orchestrator.register_plugin("langchain", LangChainPlugin())
        except ImportError:
            print("LangChain plugin dependencies not installed")
            
        try:
            self.orchestrator.register_plugin("crewai", CrewAIPlugin())
        except ImportError:
            print("CrewAI plugin dependencies not installed")
    
    def set_active_frameworks(self, frameworks: List[str]):
        """Set the active frameworks for execution.
        
        Args:
            frameworks: List of framework identifiers to activate
        """
        available = self.orchestrator.get_available_frameworks()
        self.active_frameworks = [f for f in frameworks if f in available or f == "llamaindex"]
    
    def get_available_frameworks(self) -> List[str]:
        """Get list of all available frameworks including LlamaIndex."""
        plugin_frameworks = self.orchestrator.get_available_frameworks()
        return ["llamaindex"] + plugin_frameworks
    
    async def execute_multi_framework_workflow(
        self,
        user_input: str,
        context: Context,
        agent_manager: Any,
        include_llamaindex: bool = True
    ) -> AsyncGenerator[UIEvent, None]:
        """Execute workflow across multiple frameworks.
        
        Args:
            user_input: User input for the workflow
            context: LlamaIndex workflow context
            agent_manager: RFEAgentManager instance
            include_llamaindex: Whether to include LlamaIndex in execution
            
        Yields:
            UIEvent: Events from all frameworks
        """
        # Separate LlamaIndex from plugin frameworks
        plugin_frameworks = [f for f in self.active_frameworks if f != "llamaindex"]
        
        if plugin_frameworks:
            # Execute plugin frameworks
            async for event in self.orchestrator.execute_workflow(
                user_input,
                plugin_frameworks,
                context,
                agent_manager
            ):
                yield event
        
        # Note: LlamaIndex execution happens in the main workflow
        # This integration manager only handles plugin frameworks
    
    async def stop_framework(self, framework: str):
        """Stop execution of a specific framework.
        
        Args:
            framework: Framework identifier to stop
        """
        if framework != "llamaindex":  # Can't stop LlamaIndex through plugin system
            await self.orchestrator.stop_framework(framework)
    
    async def restart_framework(
        self,
        framework: str,
        user_input: str,
        context: Context,
        agent_manager: Any
    ) -> AsyncGenerator[UIEvent, None]:
        """Restart a stopped framework.
        
        Args:
            framework: Framework identifier to restart
            user_input: User input for the workflow
            context: LlamaIndex workflow context
            agent_manager: RFEAgentManager instance
            
        Yields:
            UIEvent: Events from the restarted framework
        """
        if framework == "llamaindex":
            return  # Handle LlamaIndex restart in main workflow
        
        await self.orchestrator.restart_framework(framework)
        
        # Re-execute just this framework
        async for event in self.orchestrator.execute_workflow(
            user_input,
            [framework],
            context,
            agent_manager
        ):
            yield event
    
    async def trigger_openhands_implementation(
        self,
        artifacts: Dict[str, Any],
        context: Context,
        agent_manager: Any
    ) -> AsyncGenerator[UIEvent, None]:
        """Manually trigger OpenHands implementation phase.
        
        Args:
            artifacts: Phase 1 artifacts to process
            context: LlamaIndex workflow context
            agent_manager: RFEAgentManager instance
            
        Yields:
            UIEvent: Events from OpenHands implementation
        """
        if "openhands" not in self.orchestrator.plugins:
            yield UIEvent(
                type="error",
                data={
                    "framework": "openhands",
                    "error": "OpenHands plugin not available"
                }
            )
            return
        
        plugin = self.orchestrator.plugins["openhands"]
        
        # Execute artifact processing component
        async for event in plugin.execute_component(
            "artifact_processing",
            {"artifacts": artifacts},
            agent_manager,
            context
        ):
            ui_event = self._plugin_event_to_ui_event(event)
            yield ui_event
        
        # Then execute implementation planning
        async for event in plugin.execute_component(
            "implementation_planning",
            {"artifacts": artifacts},
            agent_manager,
            context
        ):
            ui_event = self._plugin_event_to_ui_event(event)
            yield ui_event
        
        # Finally execute code generation
        async for event in plugin.execute_component(
            "code_generation",
            {"artifacts": artifacts},
            agent_manager,
            context
        ):
            ui_event = self._plugin_event_to_ui_event(event)
            yield ui_event
    
    def _plugin_event_to_ui_event(self, plugin_event) -> UIEvent:
        """Convert plugin event to UI event.
        
        Args:
            plugin_event: PluginEvent instance
            
        Returns:
            UIEvent compatible with existing UI
        """
        from plugins.base.event_mapper import map_plugin_event_to_ui_event
        return map_plugin_event_to_ui_event(plugin_event)
    
    async def get_framework_status(self) -> Dict[str, str]:
        """Get status of all frameworks.
        
        Returns:
            Dict mapping framework names to their current status
        """
        plugin_status = await self.orchestrator.get_framework_status()
        
        # Add LlamaIndex status (always "ready" or "running")
        all_status = {"llamaindex": "ready"}
        all_status.update(plugin_status)
        
        return all_status


def create_plugin_integration_manager() -> PluginIntegrationManager:
    """Factory function to create plugin integration manager."""
    return PluginIntegrationManager()