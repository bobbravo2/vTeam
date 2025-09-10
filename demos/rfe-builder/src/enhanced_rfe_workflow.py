"""Enhanced RFE workflow with multi-framework plugin support."""

import asyncio
from typing import Any, Dict, List, Optional
from enum import Enum

from llama_index.core import Settings
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.core.chat_ui.events import UIEvent
from pydantic import BaseModel
from dotenv import load_dotenv

from src.settings import init_settings
from src.agents import RFEAgentManager, get_agent_personas
from src.rfe_builder_workflow import (
    RFEBuilderWorkflow,
    GenerateArtifactsEvent,
    RFEPhase,
    RFEBuilderUIEventData
)
from src.plugin_integration import PluginIntegrationManager


class FrameworkSelectionEvent(Event):
    """Event for framework selection."""
    selected_frameworks: List[str]
    user_input: str


class MultiFrameworkExecutionEvent(Event):
    """Event for multi-framework execution."""
    user_input: str
    frameworks: List[str]
    include_llamaindex: bool = True


class OpenHandsTriggerEvent(Event):
    """Event for manual OpenHands implementation trigger."""
    artifacts: Dict[str, Any]


class EnhancedRFEWorkflow(RFEBuilderWorkflow):
    """Enhanced RFE workflow with multi-framework plugin support."""
    
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.plugin_manager = PluginIntegrationManager()
        self.selected_frameworks = ["llamaindex"]  # Default
        self.multi_framework_mode = False
        
    @step
    async def handle_framework_selection(
        self, ctx: Context, ev: FrameworkSelectionEvent
    ) -> MultiFrameworkExecutionEvent:
        """Handle framework selection from UI."""
        
        self.selected_frameworks = ev.selected_frameworks
        self.multi_framework_mode = len(self.selected_frameworks) > 1
        
        # Update plugin manager
        self.plugin_manager.set_active_frameworks(self.selected_frameworks)
        
        # Send UI event for framework selection
        await ctx.emit(UIEvent(
            type="framework_selection",
            data={
                "selected_frameworks": self.selected_frameworks,
                "multi_framework_mode": self.multi_framework_mode,
                "message": f"Selected frameworks: {', '.join(self.selected_frameworks)}"
            }
        ))
        
        return MultiFrameworkExecutionEvent(
            user_input=ev.user_input,
            frameworks=self.selected_frameworks,
            include_llamaindex="llamaindex" in self.selected_frameworks
        )
    
    @step
    async def execute_multi_framework(
        self, ctx: Context, ev: MultiFrameworkExecutionEvent
    ) -> GenerateArtifactsEvent:
        """Execute workflow across multiple frameworks."""
        
        # Plugin frameworks (non-LlamaIndex)
        plugin_frameworks = [f for f in ev.frameworks if f != "llamaindex"]
        
        if plugin_frameworks:
            # Start plugin framework execution in parallel
            plugin_task = asyncio.create_task(
                self._execute_plugin_frameworks(ctx, ev.user_input, plugin_frameworks)
            )
            
            # Track task for coordination
            ctx.set("plugin_task", plugin_task)
        
        # If LlamaIndex is selected, continue with normal workflow
        if ev.include_llamaindex:
            # This will trigger the existing RFE builder workflow
            return GenerateArtifactsEvent(
                final_rfe=ev.user_input,
                context={"multi_framework": True}
            )
        else:
            # Wait for plugin frameworks only
            if plugin_frameworks:
                await plugin_task
            
            # Send completion event
            await ctx.emit(UIEvent(
                type="multi_framework_complete",
                data={
                    "message": "Plugin framework execution complete",
                    "frameworks": plugin_frameworks
                }
            ))
            
            return StopEvent()
    
    async def _execute_plugin_frameworks(
        self, 
        ctx: Context,
        user_input: str,
        frameworks: List[str]
    ):
        """Execute plugin frameworks and emit UI events."""
        
        try:
            async for event in self.plugin_manager.execute_multi_framework_workflow(
                user_input,
                ctx,
                self.agent_manager,
                include_llamaindex=False
            ):
                # Forward plugin events to UI
                await ctx.emit(event)
                
        except Exception as e:
            await ctx.emit(UIEvent(
                type="plugin_error",
                data={
                    "error": str(e),
                    "frameworks": frameworks,
                    "message": f"Error executing plugin frameworks: {e}"
                }
            ))
    
    @step
    async def handle_framework_control(
        self, ctx: Context, ev: Event
    ) -> Optional[Event]:
        """Handle framework control commands (stop/restart)."""
        
        event_type = ev.get("type")
        framework = ev.get("framework")
        
        if event_type == "stop_framework":
            await self.plugin_manager.stop_framework(framework)
            await ctx.emit(UIEvent(
                type="framework_stopped",
                data={
                    "framework": framework,
                    "message": f"Stopped {framework} framework"
                }
            ))
            
        elif event_type == "restart_framework":
            user_input = ev.get("user_input", "")
            
            # Restart the framework
            async for event in self.plugin_manager.restart_framework(
                framework,
                user_input,
                ctx,
                self.agent_manager
            ):
                await ctx.emit(event)
        
        return None
    
    @step  
    async def handle_openhands_trigger(
        self, ctx: Context, ev: OpenHandsTriggerEvent
    ) -> StopEvent:
        """Handle manual OpenHands implementation trigger."""
        
        await ctx.emit(UIEvent(
            type="openhands_implementation_start",
            data={
                "message": "Starting OpenHands implementation phase",
                "artifacts_count": len(ev.artifacts)
            }
        ))
        
        # Execute OpenHands implementation
        async for event in self.plugin_manager.trigger_openhands_implementation(
            ev.artifacts,
            ctx,
            self.agent_manager
        ):
            await ctx.emit(event)
        
        await ctx.emit(UIEvent(
            type="openhands_implementation_complete",
            data={
                "message": "OpenHands implementation phase complete",
                "artifacts": ev.artifacts
            }
        ))
        
        return StopEvent()
    
    async def get_framework_status(self) -> Dict[str, str]:
        """Get current status of all frameworks."""
        return await self.plugin_manager.get_framework_status()
    
    def get_available_frameworks(self) -> List[str]:
        """Get list of available frameworks."""
        return self.plugin_manager.get_available_frameworks()


def create_enhanced_rfe_workflow() -> Workflow:
    """Factory function to create enhanced RFE workflow with plugin support."""
    load_dotenv()
    init_settings()
    return EnhancedRFEWorkflow(timeout=300.0)