"""Event mapping utilities for plugin UI integration."""

from typing import Dict, Any
from datetime import datetime

from llama_index.core.chat_ui.events import UIEvent
from plugins.base.plugin_interface import PluginEvent


def map_plugin_event_to_ui_event(plugin_event: PluginEvent) -> UIEvent:
    """Convert plugin event to UI event format.
    
    Maps plugin events to existing UI event structure for compatibility
    with current multi_agent_analysis component.
    """
    return UIEvent(
        type="multi_agent_analysis",
        data={
            "framework": plugin_event.framework,
            "agent_key": f"{plugin_event.framework}_{plugin_event.component}",
            "stream_event": plugin_event.data,
            "timestamp": plugin_event.timestamp,
            "component": plugin_event.component,
            "event_type": plugin_event.type
        }
    )


def create_plugin_event(
    framework: str,
    event_type: str,
    component: str,
    data: Dict[str, Any]
) -> PluginEvent:
    """Create a standardized plugin event.
    
    Args:
        framework: Framework identifier ('openhands', 'langchain', 'crewai')
        event_type: Event type ('streaming', 'complete', 'error')
        component: Component identifier ('analysis', 'synthesis', etc.)
        data: Event data payload
        
    Returns:
        PluginEvent ready for UI consumption
    """
    return PluginEvent(
        framework=framework,
        type=event_type,
        component=component,
        data=data,
        timestamp=datetime.now().isoformat()
    )


def create_framework_specific_ui_event(
    framework: str,
    agent_key: str,
    stream_data: Dict[str, Any]
) -> UIEvent:
    """Create framework-specific UI event directly.
    
    For cases where direct UI event creation is preferred over
    plugin event conversion.
    """
    return UIEvent(
        type="multi_agent_analysis",
        data={
            "framework": framework,
            "agent_key": agent_key,
            "stream_event": stream_data,
            "timestamp": datetime.now().isoformat()
        }
    )


# Framework-specific event type mappings
FRAMEWORK_EVENT_TYPES = {
    "llamaindex": {
        "agent_streaming": "streaming",
        "agent_complete": "complete",
        "workflow_error": "error"
    },
    "openhands": {
        "task_streaming": "streaming",
        "task_complete": "complete",
        "execution_error": "error"
    },
    "langchain": {
        "agent_streaming": "streaming",
        "chain_complete": "complete",
        "graph_error": "error"
    },
    "crewai": {
        "crew_streaming": "streaming",
        "crew_complete": "complete",
        "crew_error": "error"
    }
}


def normalize_framework_event_type(framework: str, original_type: str) -> str:
    """Normalize framework-specific event types to standard types.
    
    Args:
        framework: Framework identifier
        original_type: Framework-specific event type
        
    Returns:
        Normalized event type ('streaming', 'complete', 'error')
    """
    mappings = FRAMEWORK_EVENT_TYPES.get(framework, {})
    
    # Try to find mapping, default to original if not found
    for framework_type, normalized_type in mappings.items():
        if original_type == framework_type:
            return normalized_type
    
    # Fallback: try to infer from common patterns
    if "stream" in original_type.lower():
        return "streaming"
    elif "complete" in original_type.lower() or "done" in original_type.lower():
        return "complete"
    elif "error" in original_type.lower() or "fail" in original_type.lower():
        return "error"
    
    return original_type