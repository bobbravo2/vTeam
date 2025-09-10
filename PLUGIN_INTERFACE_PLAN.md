# Plugin Interface Architecture Plan

**Date**: September 9, 2025  
**Purpose**: Design plugin interface for agentic frameworks (OpenHands, LangChain, CrewAI) to be added to vTeam project  
**Current System**: LlamaIndex workflows with LlamaDeploy orchestration

## Requirements Summary

### Framework Integration Goals
- **OpenHands**: Code generation and task execution capabilities for implementation phase ([GitHub](https://github.com/All-Hands-AI/OpenHands))
- **LangChain**: LangGraph workflows mirroring existing 7-agent council process
- **CrewAI**: AI agent collaboration using default hierarchy structure
- **Purpose**: Framework bakeoff to determine best fit for RFE clarity and user experience

### Key Architectural Decisions ✅ FINALIZED
- **All 3 Frameworks**: Implement OpenHands, LangChain, and CrewAI simultaneously
- **Complete Isolation**: Separate virtual environments for each plugin framework
- **Error Handling**: Continue-on-error approach with individual STOP buttons per framework
- **State Management**: Plugins have read-only access to `RFEAgentManager`
- **OpenHands Integration**: Manual trigger button for implementation phase (automation later)
- **LangChain Tools**: Mirror Claude's default toolkit capabilities
- **CrewAI Structure**: Use CrewAI's default hierarchical organization
- **UI Layout**: Side-by-side comparison view for framework outputs
- **Deployment**: Separate LlamaDeploy services with complete dependency isolation
- **Event System**: Refactor existing UI events to support multi-framework streaming
- **Persona Mapping**: Static YAML translation with planned dynamic complexity support

## Core Architecture Principles

- **Loosely Coupled**: Plugins implement minimal interface contracts
- **Service-Based**: Each plugin framework runs as separate LlamaDeploy service
- **Stateless**: Plugins don't maintain session state
- **Compatible Events**: Plugins emit events compatible with existing UI
- **Parallel Execution**: Multiple frameworks run simultaneously without data sharing

## Plugin Interface Design

```python
# Core Plugin Interface
class PluginWorkflow(ABC):
    """Base interface for framework plugins"""
    
    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Framework identifier (e.g., 'openhands', 'langchain', 'crewai')"""
    
    @property 
    @abstractmethod
    def supported_granularities(self) -> List[str]:
        """Component granularities this plugin supports"""
        # e.g., ['full_workflow', 'analysis', 'synthesis', 'artifact_generation']
    
    @abstractmethod
    async def execute_component(
        self, 
        component: str,
        input_data: Dict[str, Any],
        agent_manager: RFEAgentManager,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute a workflow component with streaming events"""
```

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (TypeScript)                        │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │ Framework       │  │ Multi-Framework  │  │ Plugin-Specific │ │
│  │ Selector UI     │  │ Progress Tracker │  │ UI Components   │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │   LlamaDeploy API     │
                    │     (Port 8000)       │
                    └───────────┬───────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    │                           │                           │
┌───▼────┐              ┌──────▼──────┐              ┌─────▼─────┐
│LlamaIdx│              │  OpenHands  │              │ LangChain │
│Service │              │   Plugin    │              │  Plugin   │
│        │              │   Service   │              │  Service  │
└───┬────┘              └──────┬──────┘              └─────┬─────┘
    │                          │                          │
    └──────────────────────────┼──────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Shared Services   │
                    │ • RFEAgentManager   │
                    │ • RAG Indices       │
                    │ • Event Bus         │
                    └─────────────────────┘
```

## Plugin Service Structure

Each framework plugin runs as a separate LlamaDeploy service:

```yaml
# deployment.yml extension
services:
  # Existing services...
  
  openhands-plugin:
    name: OpenHands Plugin
    description: OpenHands code generation and task execution
    source:
      type: local
      name: plugins/openhands
    path: openhands_plugin:create_openhands_workflow
    python-dependencies:
      - openhands-ai>=0.56.0
      - llama-index-core>=0.12.0
    
  langchain-plugin:
    name: LangChain Plugin  
    description: LangGraph workflows, agents, tools, chains
    source:
      type: local
      name: plugins/langchain
    path: langchain_plugin:create_langchain_workflow
    python-dependencies:
      - langchain>=0.1.0
      - langgraph>=0.1.0
      - llama-index-core>=0.12.0
```

## Event System Integration

Plugins emit compatible events for UI integration:

```python
class PluginEvent(BaseModel):
    """Standard plugin event format"""
    framework: str
    type: str  # 'streaming', 'complete', 'error'
    component: str  # 'analysis', 'synthesis', etc.
    data: Dict[str, Any]
    timestamp: str

# Plugin events map to existing UI events
def map_plugin_event_to_ui_event(plugin_event: PluginEvent) -> UIEvent:
    return UIEvent(
        type="multi_agent_analysis",  # or framework-specific type
        data={
            "framework": plugin_event.framework,
            "agent_key": f"{plugin_event.framework}_{plugin_event.component}",
            "stream_event": plugin_event.data
        }
    )
```

## Multi-Framework Orchestration

```python
class MultiFrameworkOrchestrator:
    """Coordinates parallel execution across selected frameworks"""
    
    async def execute_workflow(
        self, 
        user_input: str,
        selected_frameworks: List[str],
        context: Context
    ) -> AsyncGenerator[UIEvent, None]:
        
        # Start all frameworks in parallel
        framework_tasks = []
        for framework in selected_frameworks:
            plugin = self.get_plugin(framework)
            task = asyncio.create_task(
                plugin.execute_component("full_workflow", {"input": user_input}, self.agent_manager, context)
            )
            framework_tasks.append((framework, task))
        
        # Stream events from all frameworks
        async for framework, event in self._stream_from_multiple_tasks(framework_tasks):
            ui_event = map_plugin_event_to_ui_event(event)
            ui_event.data["framework"] = framework
            yield ui_event
```

## UI Integration Points

### Framework Selector Component
```jsx
// New component for framework selection
function FrameworkSelector({ onFrameworksChange, defaultFrameworks = ["llamaindex"] }) {
  const [selectedFrameworks, setSelectedFrameworks] = useState(defaultFrameworks);
  
  const frameworks = [
    { id: "llamaindex", name: "LlamaIndex", description: "Current workflow system" },
    { id: "openhands", name: "OpenHands", description: "Code generation & task execution" },
    { id: "langchain", name: "LangChain", description: "Workflows, agents, tools, chains" }
  ];
  
  return (
    <div className="framework-selector">
      {frameworks.map(framework => (
        <FrameworkOption 
          key={framework.id}
          framework={framework}
          selected={selectedFrameworks.includes(framework.id)}
          onChange={(selected) => {/* update selection */}}
        />
      ))}
    </div>
  );
}
```

### Multi-Framework Progress Tracker with Individual Controls
```jsx
function MultiFrameworkProgress({ events, onStopFramework, onTriggerOpenHands }) {
  // Group events by framework
  const frameworkEvents = groupBy(events, 'framework');
  
  return (
    <div className="multi-framework-progress side-by-side">
      {Object.entries(frameworkEvents).map(([framework, events]) => (
        <FrameworkProgressPanel 
          key={framework}
          framework={framework}
          events={events}
          onStop={() => onStopFramework(framework)}
          showStopButton={framework !== 'llamaindex'} // Always allow stopping plugin frameworks
          component={getFrameworkSpecificComponent(framework)}
        />
      ))}
      
      {/* OpenHands Implementation Trigger */}
      <ImplementationTrigger 
        onTrigger={onTriggerOpenHands}
        enabled={isPhase1Complete(events)}
        artifacts={getPhase1Artifacts(events)}
      />
    </div>
  );
}

function ImplementationTrigger({ onTrigger, enabled, artifacts }) {
  return (
    <div className="implementation-trigger">
      <h4>Implementation Phase</h4>
      <button 
        onClick={onTrigger}
        disabled={!enabled}
        className="btn-implementation"
      >
        🔧 Start OpenHands Implementation
      </button>
      {enabled && (
        <p>Ready to generate implementation plans from your RFE artifacts</p>
      )}
    </div>
  );
}
```

## Plugin Directory Structure

```
plugins/
├── base/
│   ├── __init__.py
│   ├── plugin_interface.py      # PluginWorkflow base class
│   ├── event_mapper.py          # Event mapping utilities
│   └── agent_translator.py      # Static persona translation
├── openhands/
│   ├── __init__.py
│   ├── openhands_plugin.py      # OpenHands workflow implementation
│   ├── persona_mapping.yaml     # Static persona translations
│   └── requirements.txt
├── langchain/
│   ├── __init__.py
│   ├── langchain_plugin.py      # LangChain workflow implementation
│   ├── persona_mapping.yaml
│   └── requirements.txt
└── crewai/                      # Future implementation
    ├── __init__.py
    ├── crewai_plugin.py
    └── persona_mapping.yaml
```

## Static Persona Translation

```yaml
# plugins/openhands/persona_mapping.yaml
persona_mappings:
  UX_RESEARCHER:
    openhands_role: "user_researcher"
    description: "Analyze user needs and research requirements"
    capabilities: ["user_analysis", "requirements_gathering"]
  
  STAFF_ENGINEER:
    openhands_role: "senior_developer"  
    description: "Technical architecture and implementation"
    capabilities: ["code_generation", "system_design"]

# plugins/langchain/persona_mapping.yaml  
persona_mappings:
  UX_RESEARCHER:
    langchain_agent_type: "research_agent"
    tools: ["web_search", "document_analysis"]
    
  STAFF_ENGINEER:
    langchain_agent_type: "coding_agent"
    tools: ["code_generator", "architecture_planner"]
```

## Updated Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- **Base plugin interface** (`plugins/base/plugin_interface.py`)
- **Enhanced event system** with multi-framework support (backward compatible)
- **Multi-framework orchestrator** with individual stop/start controls
- **Framework selector UI** with side-by-side layout
- **LlamaDeploy integration** extending existing `deployment.yml`

### Phase 2: All Framework Plugins (Week 2-4)
**OpenHands Plugin:**
- Post-RFE implementation workflows (triggered manually)
- Code generation for approved Phase 1 artifacts
- Implementation planning and scaffolding

**LangChain Plugin:**
- LangGraph workflow mirroring 7-agent council process
- Claude-equivalent toolset integration
- Agent mapping: UX_RESEARCHER → research_agent, etc.

**CrewAI Plugin:**
- Default hierarchical crew structure
- 7-agent council collaboration patterns
- CrewAI-native coordination mechanisms

### Phase 3: UI Enhancement & Controls (Week 4-5)
- **Individual framework STOP buttons**
- **Side-by-side comparison display**
- **OpenHands implementation trigger button**
- **Framework-specific error handling and display**
- **Enhanced progress tracking per framework**

### Phase 4: Static Persona Translation (Week 5-6)
- **YAML mapping files** for all three frameworks
- **Translation validation** ensuring complete persona coverage
- **Framework-specific capability mapping**
- **Error handling for missing translations**

## Backlog Items

### High Priority
1. **Review OpenHands additional capabilities** beyond code generation/task execution
2. **Static persona translation system** for cross-framework compatibility
3. **Agent format converter middleware** between framework formats

### Medium Priority  
4. **Framework selection per-agent and per-conversation** (beyond per-workflow)
5. **Plugin health checks and monitoring**
6. **Comparison report generation** for framework bakeoff

### Future Enhancements
7. **Benchmarking and comparison tools**
8. **A/B testing capabilities**

## Technical Considerations

### Why LlamaDeploy?
- Already your current orchestration layer
- Provides service isolation and health monitoring
- Handles deployment and scaling concerns
- Maintains consistent API patterns

### Dependency Management
- **Complete Isolation**: Separate virtual environments for each plugin framework
- **No Inheritance**: Plugins declare all dependencies independently in requirements.txt
- **Container-based Deployment**: LlamaDeploy handles dependency conflicts via isolation
- **Framework-specific Dependencies**: Each plugin manages its own Python environment

### Error Handling
- **Continue-on-Error**: Framework failures don't stop other frameworks
- **Individual STOP Buttons**: Users can stop each framework independently via UI
- **Framework-specific Error Reporting**: Errors shown per-framework in side-by-side view
- **Manual Recovery**: Users can restart individual frameworks without affecting others

### Performance Considerations
- Parallel execution prevents blocking
- Stateless plugins enable horizontal scaling
- Event streaming maintains responsiveness
- Plugin granularity allows selective execution

## Final Implementation Decisions ✅

Based on clarification session, all architectural decisions are finalized:

1. **Complete framework isolation** with separate virtual environments
2. **Continue-on-error approach** with individual STOP buttons per framework  
3. **Manual OpenHands triggering** via dedicated button (automation planned for later)
4. **LangChain tools mirror Claude's defaults** (document analysis, web search, code generation, etc.)
5. **CrewAI uses default hierarchy** structure for agent collaboration
6. **Side-by-side comparison UI** for framework output comparison
7. **Enhanced event system** supporting multi-framework streaming while maintaining backward compatibility

**Success Metrics Focus**: RFE clarity and user experience optimization

---

**Next Steps**: Ready to begin Phase 1 implementation - core infrastructure development starting with base plugin interface and enhanced event system.
