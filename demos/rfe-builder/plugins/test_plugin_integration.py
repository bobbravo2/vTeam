"""Test plugin integration with existing RFE workflow."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from plugins.base.plugin_interface import PluginEvent
from plugins.base.orchestrator import MultiFrameworkOrchestrator
from plugins.base.agent_translator import PersonaTranslator, STANDARD_RFE_PERSONAS
from plugins.openhands.openhands_plugin import OpenHandsPlugin
from plugins.langchain.langchain_plugin import LangChainPlugin
from plugins.crewai.crewai_plugin import CrewAIPlugin


class TestPluginIntegration:
    """Integration tests for plugin system."""
    
    @pytest.fixture
    def mock_agent_manager(self):
        """Mock RFEAgentManager for testing."""
        manager = MagicMock()
        manager.get_agent_personas = AsyncMock(return_value={
            "PRODUCT_MANAGER": {"name": "Product Manager", "persona": "PRODUCT_MANAGER"},
            "STAFF_ENGINEER": {"name": "Staff Engineer", "persona": "STAFF_ENGINEER"},
            "UX_RESEARCHER": {"name": "UX Researcher", "persona": "UX_RESEARCHER"}
        })
        return manager
    
    @pytest.fixture
    def mock_context(self):
        """Mock LlamaIndex workflow context."""
        context = MagicMock()
        return context
    
    async def test_openhands_plugin_execution(self, mock_agent_manager, mock_context):
        """Test OpenHands plugin execution."""
        plugin = OpenHandsPlugin()
        
        events = []
        async for event in plugin.execute_component(
            "full_workflow",
            {"input": "Create a user dashboard feature"},
            mock_agent_manager,
            mock_context
        ):
            events.append(event)
        
        assert len(events) > 0
        assert events[0].framework == "openhands"
        assert events[-1].type == "complete"
        
        # Check for key phases
        phases = [event.data.get("phase") for event in events]
        assert "initialization" in phases
        assert "analysis" in phases
        assert "architecture" in phases
    
    async def test_langchain_plugin_execution(self, mock_agent_manager, mock_context):
        """Test LangChain plugin execution."""
        plugin = LangChainPlugin()
        
        events = []
        async for event in plugin.execute_component(
            "full_workflow", 
            {"input": "Create a user dashboard feature"},
            mock_agent_manager,
            mock_context
        ):
            events.append(event)
        
        assert len(events) > 0
        assert events[0].framework == "langchain"
        assert events[-1].type == "complete"
        
        # Check for agent collaboration
        agent_events = [e for e in events if e.data.get("phase") == "agent_streaming"]
        assert len(agent_events) > 0
    
    async def test_crewai_plugin_execution(self, mock_agent_manager, mock_context):
        """Test CrewAI plugin execution."""
        plugin = CrewAIPlugin()
        
        events = []
        async for event in plugin.execute_component(
            "full_workflow",
            {"input": "Create a user dashboard feature"},
            mock_agent_manager,
            mock_context
        ):
            events.append(event)
        
        assert len(events) > 0
        assert events[0].framework == "crewai"
        assert events[-1].type == "complete"
        
        # Check for hierarchical processing
        hierarchy_events = [e for e in events if "hierarchy" in str(e.data)]
        assert len(hierarchy_events) > 0
    
    async def test_persona_translation_completeness(self):
        """Test that all standard personas have translations in all frameworks."""
        frameworks = ["openhands", "langchain", "crewai"]
        
        for framework in frameworks:
            translator = PersonaTranslator(framework)
            missing = translator.validate_translations(STANDARD_RFE_PERSONAS)
            assert len(missing) == 0, f"Missing translations in {framework}: {missing}"
    
    async def test_orchestrator_parallel_execution(self, mock_agent_manager, mock_context):
        """Test multi-framework orchestrator parallel execution."""
        orchestrator = MultiFrameworkOrchestrator()
        
        # Register plugins
        orchestrator.register_plugin("openhands", OpenHandsPlugin())
        orchestrator.register_plugin("langchain", LangChainPlugin())
        orchestrator.register_plugin("crewai", CrewAIPlugin())
        
        events = []
        async for event in orchestrator.execute_workflow(
            "Create a user dashboard feature",
            ["openhands", "langchain"],
            mock_context,
            mock_agent_manager
        ):
            events.append(event)
        
        # Check that events from both frameworks are present
        frameworks = {event.data.get("framework") for event in events}
        assert "openhands" in frameworks
        assert "langchain" in frameworks
    
    async def test_orchestrator_error_handling(self, mock_agent_manager, mock_context):
        """Test orchestrator continue-on-error behavior."""
        orchestrator = MultiFrameworkOrchestrator()
        
        # Create a plugin that raises an error
        class FailingPlugin(OpenHandsPlugin):
            async def execute_component(self, component, input_data, agent_manager, context):
                yield PluginEvent(
                    framework="failing",
                    type="streaming", 
                    component=component,
                    data={"message": "Starting..."},
                    timestamp="2024-01-01T00:00:00"
                )
                raise Exception("Test error")
        
        orchestrator.register_plugin("failing", FailingPlugin())
        orchestrator.register_plugin("openhands", OpenHandsPlugin())
        
        events = []
        async for event in orchestrator.execute_workflow(
            "Test input",
            ["failing", "openhands"],
            mock_context, 
            mock_agent_manager
        ):
            events.append(event)
        
        # Check that we got events from both frameworks
        frameworks = {event.data.get("framework") for event in events}
        assert "failing" in frameworks
        assert "openhands" in frameworks
        
        # Check that error was handled
        error_events = [e for e in events if e.data.get("error_type")]
        assert len(error_events) > 0
    
    async def test_framework_stop_functionality(self, mock_agent_manager, mock_context):
        """Test individual framework stop functionality."""
        orchestrator = MultiFrameworkOrchestrator()
        orchestrator.register_plugin("openhands", OpenHandsPlugin())
        
        # Start execution
        task = asyncio.create_task(
            list(orchestrator.execute_workflow(
                "Test input",
                ["openhands"],
                mock_context,
                mock_agent_manager
            ))
        )
        
        # Stop framework after brief delay
        await asyncio.sleep(0.1)
        await orchestrator.stop_framework("openhands")
        
        # Check that framework was marked as stopped
        assert orchestrator.is_framework_stopped("openhands")
    
    def test_event_mapping_compatibility(self):
        """Test that plugin events map correctly to UI events."""
        from plugins.base.event_mapper import map_plugin_event_to_ui_event, create_plugin_event
        
        plugin_event = create_plugin_event(
            "openhands", "streaming", "analysis",
            {"message": "Test message", "phase": "test_phase"}
        )
        
        ui_event = map_plugin_event_to_ui_event(plugin_event)
        
        assert ui_event.type == "multi_agent_analysis"
        assert ui_event.data["framework"] == "openhands"
        assert ui_event.data["agent_key"] == "openhands_analysis"
        assert ui_event.data["stream_event"]["message"] == "Test message"


async def manual_integration_test():
    """Manual integration test for development/debugging."""
    print("🧪 Running manual plugin integration test...")
    
    # Mock dependencies
    mock_agent_manager = MagicMock()
    mock_agent_manager.get_agent_personas = AsyncMock(return_value={
        "PRODUCT_MANAGER": {"name": "Product Manager", "persona": "PRODUCT_MANAGER"},
        "STAFF_ENGINEER": {"name": "Staff Engineer", "persona": "STAFF_ENGINEER"}
    })
    mock_context = MagicMock()
    
    # Test orchestrator
    orchestrator = MultiFrameworkOrchestrator()
    orchestrator.register_plugin("openhands", OpenHandsPlugin())
    orchestrator.register_plugin("langchain", LangChainPlugin())
    orchestrator.register_plugin("crewai", CrewAIPlugin())
    
    print(f"✅ Registered frameworks: {orchestrator.get_available_frameworks()}")
    
    # Test execution
    print("🚀 Starting multi-framework execution...")
    event_count = 0
    
    async for event in orchestrator.execute_workflow(
        "Create an AI-powered analytics dashboard",
        ["openhands", "langchain", "crewai"],
        mock_context,
        mock_agent_manager
    ):
        event_count += 1
        framework = event.data.get("framework", "unknown")
        message = event.data.get("message", "No message")
        print(f"  📨 [{framework}] {message}")
        
        if event_count > 50:  # Limit output for testing
            break
    
    print(f"✅ Integration test complete! Processed {event_count} events")
    
    # Test persona translations
    print("🔄 Testing persona translations...")
    for framework in ["openhands", "langchain", "crewai"]:
        translator = PersonaTranslator(framework)
        missing = translator.validate_translations(STANDARD_RFE_PERSONAS[:3])  # Test subset
        if missing:
            print(f"❌ {framework}: Missing translations for {missing}")
        else:
            print(f"✅ {framework}: All persona translations present")
    
    print("🎉 Manual integration test completed successfully!")


if __name__ == "__main__":
    asyncio.run(manual_integration_test())