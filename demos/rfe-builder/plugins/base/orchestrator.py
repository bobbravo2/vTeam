"""Multi-framework orchestrator for parallel execution and coordination."""

import asyncio
from typing import Dict, List, Any, AsyncGenerator, Optional, Set
from datetime import datetime

from llama_index.core.workflow import Context
from llama_index.core.chat_ui.events import UIEvent

from plugins.base.plugin_interface import PluginWorkflow, PluginEvent, PluginError
from plugins.base.event_mapper import map_plugin_event_to_ui_event, create_plugin_event


class MultiFrameworkOrchestrator:
    """Coordinates parallel execution across selected frameworks."""
    
    def __init__(self):
        self.plugins: Dict[str, PluginWorkflow] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.stopped_frameworks: Set[str] = set()
    
    def register_plugin(self, framework: str, plugin: PluginWorkflow):
        """Register a plugin framework.
        
        Args:
            framework: Framework identifier
            plugin: PluginWorkflow implementation
        """
        self.plugins[framework] = plugin
    
    def get_available_frameworks(self) -> List[str]:
        """Get list of available framework identifiers."""
        return list(self.plugins.keys())
    
    def is_framework_stopped(self, framework: str) -> bool:
        """Check if a framework has been manually stopped."""
        return framework in self.stopped_frameworks
    
    async def stop_framework(self, framework: str):
        """Stop execution of a specific framework.
        
        Args:
            framework: Framework identifier to stop
        """
        self.stopped_frameworks.add(framework)
        
        if framework in self.active_tasks:
            task = self.active_tasks[framework]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del self.active_tasks[framework]
    
    async def restart_framework(self, framework: str):
        """Restart a stopped framework.
        
        Args:
            framework: Framework identifier to restart
        """
        if framework in self.stopped_frameworks:
            self.stopped_frameworks.remove(framework)
    
    async def execute_workflow(
        self, 
        user_input: str,
        selected_frameworks: List[str],
        context: Context,
        agent_manager: Any,
        component: str = "full_workflow"
    ) -> AsyncGenerator[UIEvent, None]:
        """Execute workflow across multiple frameworks in parallel.
        
        Args:
            user_input: User input for the workflow
            selected_frameworks: List of framework identifiers to execute
            context: LlamaIndex workflow context
            agent_manager: RFEAgentManager instance
            component: Component to execute ('full_workflow', 'analysis', etc.)
            
        Yields:
            UIEvent: UI events from all frameworks
        """
        # Clear stopped frameworks for new execution
        self.stopped_frameworks.clear()
        
        # Validate frameworks
        available_frameworks = set(self.plugins.keys())
        invalid_frameworks = set(selected_frameworks) - available_frameworks
        if invalid_frameworks:
            yield self._create_error_event(
                "orchestrator",
                f"Invalid frameworks: {', '.join(invalid_frameworks)}"
            )
            return
        
        # Start all frameworks in parallel
        framework_tasks = []
        for framework in selected_frameworks:
            if framework in self.plugins:
                plugin = self.plugins[framework]
                input_data = {"input": user_input, "user_input": user_input}
                
                task = asyncio.create_task(
                    self._execute_framework_with_error_handling(
                        framework, plugin, component, input_data, agent_manager, context
                    )
                )
                self.active_tasks[framework] = task
                framework_tasks.append((framework, task))
        
        # Stream events from all frameworks with continue-on-error
        async for ui_event in self._stream_from_multiple_tasks(framework_tasks):
            yield ui_event
        
        # Clean up completed tasks
        for framework in list(self.active_tasks.keys()):
            if self.active_tasks[framework].done():
                del self.active_tasks[framework]
    
    async def _execute_framework_with_error_handling(
        self,
        framework: str,
        plugin: PluginWorkflow,
        component: str,
        input_data: Dict[str, Any],
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute framework with error handling and continue-on-error behavior."""
        try:
            async for event in plugin.execute_component(
                component, input_data, agent_manager, context
            ):
                # Check if framework was stopped during execution
                if framework in self.stopped_frameworks:
                    yield create_plugin_event(
                        framework, "stopped", component,
                        {"message": f"{framework} framework stopped by user"}
                    )
                    return
                
                yield event
                
        except asyncio.CancelledError:
            # Framework was stopped
            yield create_plugin_event(
                framework, "stopped", component,
                {"message": f"{framework} framework stopped"}
            )
            
        except PluginError as e:
            # Plugin-specific error
            yield create_plugin_event(
                framework, "error", component,
                {
                    "error": str(e),
                    "error_type": "plugin_error",
                    "component": e.component or component
                }
            )
            
        except Exception as e:
            # Unexpected error
            yield create_plugin_event(
                framework, "error", component,
                {
                    "error": str(e),
                    "error_type": "unexpected_error",
                    "framework": framework
                }
            )
    
    async def _stream_from_multiple_tasks(
        self, 
        framework_tasks: List[tuple[str, asyncio.Task]]
    ) -> AsyncGenerator[UIEvent, None]:
        """Stream events from multiple framework tasks with continue-on-error."""
        
        # Create a queue for collecting events from all frameworks
        event_queue = asyncio.Queue()
        
        # Create tasks that feed the queue
        async def feed_queue(framework: str, task: asyncio.Task):
            try:
                async for event in task:
                    await event_queue.put((framework, event))
            except Exception as e:
                # Task failed, put error event
                error_event = create_plugin_event(
                    framework, "error", "framework_execution",
                    {"error": str(e), "error_type": "task_error"}
                )
                await event_queue.put((framework, error_event))
            finally:
                await event_queue.put((framework, None))  # Signal completion
        
        # Start all feeder tasks
        feeder_tasks = []
        for framework, task in framework_tasks:
            feeder_task = asyncio.create_task(feed_queue(framework, task))
            feeder_tasks.append(feeder_task)
        
        # Stream events until all frameworks complete or are stopped
        completed_frameworks = set()
        total_frameworks = len(framework_tasks)
        
        while len(completed_frameworks) < total_frameworks:
            try:
                # Wait for next event with timeout
                framework, event = await asyncio.wait_for(
                    event_queue.get(), timeout=1.0
                )
                
                if event is None:
                    # Framework completed
                    completed_frameworks.add(framework)
                    continue
                
                # Convert plugin event to UI event and yield
                ui_event = map_plugin_event_to_ui_event(event)
                yield ui_event
                
            except asyncio.TimeoutError:
                # Check if any frameworks were stopped
                for framework, _ in framework_tasks:
                    if framework in self.stopped_frameworks:
                        completed_frameworks.add(framework)
                continue
        
        # Clean up feeder tasks
        for feeder_task in feeder_tasks:
            if not feeder_task.done():
                feeder_task.cancel()
    
    def _create_error_event(self, framework: str, message: str) -> UIEvent:
        """Create an error UI event."""
        error_event = create_plugin_event(
            framework, "error", "orchestrator",
            {"error": message, "timestamp": datetime.now().isoformat()}
        )
        return map_plugin_event_to_ui_event(error_event)
    
    async def get_framework_status(self) -> Dict[str, str]:
        """Get status of all registered frameworks.
        
        Returns:
            Dict mapping framework names to their current status
        """
        status = {}
        for framework in self.plugins.keys():
            if framework in self.stopped_frameworks:
                status[framework] = "stopped"
            elif framework in self.active_tasks:
                task = self.active_tasks[framework]
                if task.done():
                    status[framework] = "completed"
                else:
                    status[framework] = "running"
            else:
                status[framework] = "ready"
        
        return status