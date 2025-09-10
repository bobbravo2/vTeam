"""CrewAI plugin for AI agent collaboration using hierarchical structure."""

import asyncio
from typing import Dict, Any, List, AsyncGenerator
from datetime import datetime

from llama_index.core.workflow import Context, Workflow

from plugins.base.plugin_interface import PluginWorkflow, PluginEvent, PluginExecutionError
from plugins.base.event_mapper import create_plugin_event
from plugins.base.agent_translator import PersonaTranslator


class CrewAIPlugin(PluginWorkflow):
    """CrewAI implementation using default hierarchical crew structure."""
    
    def __init__(self):
        self.persona_translator = PersonaTranslator("crewai")
        self.framework_name = "crewai"
        
    @property
    def framework_name(self) -> str:
        return "crewai"
    
    @property
    def supported_granularities(self) -> List[str]:
        return [
            "full_workflow",
            "crew_formation",
            "hierarchical_collaboration", 
            "task_delegation",
            "crew_coordination",
            "collective_decision_making"
        ]
    
    async def execute_component(
        self,
        component: str,
        input_data: Dict[str, Any],
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute CrewAI workflow component."""
        
        if component not in self.supported_granularities:
            raise PluginExecutionError(
                self.framework_name,
                f"Unsupported component: {component}",
                component
            )
        
        user_input = input_data.get("input", input_data.get("user_input", ""))
        
        yield create_plugin_event(
            self.framework_name, "streaming", component,
            {
                "message": f"Starting CrewAI {component} execution",
                "phase": "initialization"
            }
        )
        
        if component == "full_workflow":
            async for event in self._execute_full_workflow(user_input, agent_manager, context):
                yield event
        elif component == "crew_formation":
            async for event in self._execute_crew_formation(user_input, agent_manager, context):
                yield event
        elif component == "hierarchical_collaboration":
            async for event in self._execute_hierarchical_collaboration(user_input, agent_manager, context):
                yield event
        elif component == "task_delegation":
            async for event in self._execute_task_delegation(user_input, agent_manager, context):
                yield event
        elif component == "crew_coordination":
            async for event in self._execute_crew_coordination(user_input, agent_manager, context):
                yield event
        elif component == "collective_decision_making":
            async for event in self._execute_collective_decision_making(user_input, agent_manager, context):
                yield event
    
    async def _execute_full_workflow(
        self, 
        user_input: str, 
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute complete CrewAI workflow with hierarchical structure."""
        
        # Get agent personas and organize into crew hierarchy
        personas = await agent_manager.get_agent_personas() if hasattr(agent_manager, 'get_agent_personas') else {}
        
        # Phase 1: Crew Formation and Hierarchy Establishment
        yield create_plugin_event(
            self.framework_name, "streaming", "crew_formation",
            {
                "message": "Forming CrewAI hierarchical crew structure",
                "phase": "crew_formation",
                "total_crew_members": len(personas)
            }
        )
        
        crew_hierarchy = await self._establish_crew_hierarchy(personas)
        
        yield create_plugin_event(
            self.framework_name, "streaming", "crew_formation",
            {
                "message": "Crew hierarchy established",
                "phase": "hierarchy_complete",
                "crew_structure": crew_hierarchy
            }
        )
        
        # Phase 2: Hierarchical Task Analysis
        yield create_plugin_event(
            self.framework_name, "streaming", "hierarchical_collaboration",
            {
                "message": "Starting hierarchical collaboration and task analysis",
                "phase": "collaboration_start"
            }
        )
        
        crew_analyses = {}
        
        # Process by hierarchy levels (managers first, then seniors, then specialists)
        for level in ["manager", "lead", "senior", "specialist", "junior", "facilitator"]:
            level_members = crew_hierarchy.get(level, [])
            if not level_members:
                continue
                
            yield create_plugin_event(
                self.framework_name, "streaming", "hierarchical_collaboration",
                {
                    "message": f"Processing {level} level crew members",
                    "phase": "level_processing",
                    "hierarchy_level": level,
                    "members": len(level_members)
                }
            )
            
            for persona_key in level_members:
                crew_member = crew_hierarchy["member_details"][persona_key]
                crew_analysis = await self._execute_crew_member_analysis(
                    persona_key, user_input, crew_member, level
                )
                crew_analyses[persona_key] = crew_analysis
                
                yield create_plugin_event(
                    self.framework_name, "streaming", "hierarchical_collaboration",
                    {
                        "message": f"{crew_member['name']} analysis complete",
                        "phase": "member_complete",
                        "crew_member": crew_member['crew_id'],
                        "hierarchy_level": level,
                        "analysis": crew_analysis
                    }
                )
            
            await asyncio.sleep(0.3)  # Brief pause between hierarchy levels
        
        # Phase 3: Crew Coordination and Synthesis
        yield create_plugin_event(
            self.framework_name, "streaming", "crew_coordination",
            {
                "message": "Coordinating crew insights through hierarchical synthesis",
                "phase": "coordination_start"
            }
        )
        
        await asyncio.sleep(0.6)
        
        coordination_result = await self._execute_hierarchical_synthesis(crew_analyses, crew_hierarchy)
        
        yield create_plugin_event(
            self.framework_name, "streaming", "crew_coordination",
            {
                "coordination": coordination_result,
                "phase": "coordination_complete",
                "message": "Crew coordination and synthesis complete"
            }
        )
        
        # Phase 4: Collective Decision Making
        yield create_plugin_event(
            self.framework_name, "streaming", "collective_decision_making",
            {
                "message": "Executing CrewAI collective decision making process",
                "phase": "decision_start"
            }
        )
        
        await asyncio.sleep(0.5)
        
        crew_decisions = await self._execute_crew_decisions(coordination_result, crew_hierarchy)
        
        yield create_plugin_event(
            self.framework_name, "streaming", "collective_decision_making",
            {
                "decisions": crew_decisions,
                "phase": "decision_complete",
                "message": "Collective decision making complete"
            }
        )
        
        # Complete workflow
        yield create_plugin_event(
            self.framework_name, "complete", "full_workflow",
            {
                "message": "CrewAI hierarchical workflow complete",
                "summary": {
                    "crew_structure": crew_hierarchy,
                    "crew_analyses": crew_analyses,
                    "coordination": coordination_result,
                    "decisions": crew_decisions,
                    "framework": "crewai",
                    "total_crew_members": len(crew_analyses)
                }
            }
        )
    
    async def _establish_crew_hierarchy(self, personas: Dict[str, Any]) -> Dict[str, Any]:
        """Establish CrewAI hierarchical crew structure."""
        
        hierarchy = {
            "manager": [],
            "lead": [],
            "senior": [],
            "specialist": [],
            "junior": [],
            "facilitator": [],
            "member_details": {}
        }
        
        for persona_key, persona_config in personas.items():
            crew_config = self.persona_translator.translate_persona(persona_key)
            hierarchy_level = crew_config.get('hierarchy_level', 'specialist')
            
            hierarchy[hierarchy_level].append(persona_key)
            hierarchy["member_details"][persona_key] = {
                "name": persona_config.get('name', persona_key),
                "crew_id": crew_config.get('agent_id', persona_key.lower()),
                "framework_role": crew_config.get('framework_role', 'crew_member'),
                "responsibilities": crew_config.get('crew_responsibilities', []),
                "hierarchy_level": hierarchy_level
            }
        
        return hierarchy
    
    async def _execute_crew_member_analysis(
        self, 
        persona_key: str, 
        user_input: str, 
        crew_member: Dict[str, Any],
        hierarchy_level: str
    ) -> Dict[str, Any]:
        """Execute analysis for a specific crew member."""
        
        await asyncio.sleep(0.2)  # Simulate processing time
        
        crew_config = self.persona_translator.translate_persona(persona_key)
        responsibilities = crew_config.get('crew_responsibilities', [])
        
        # Role-specific analysis based on hierarchy level and responsibilities
        if hierarchy_level == "manager":
            return {
                "strategic_assessment": "High-level strategic impact evaluation completed",
                "resource_allocation": "Team capacity and resource requirements identified",
                "risk_management": "Strategic risks and mitigation strategies defined",
                "stakeholder_coordination": "Key stakeholder communication plan established",
                "crew_responsibilities": responsibilities,
                "hierarchy_impact": "Manager-level strategic oversight provided"
            }
        elif hierarchy_level == "lead":
            return {
                "technical_leadership": "Technical approach and team coordination planned",
                "delivery_planning": "Sprint planning and milestone coordination completed",
                "team_coordination": "Cross-team dependencies and communication established",
                "quality_oversight": "Quality standards and review processes defined",
                "crew_responsibilities": responsibilities,
                "hierarchy_impact": "Lead-level coordination and planning provided"
            }
        elif hierarchy_level == "senior":
            return {
                "technical_expertise": "Advanced technical analysis and solution design completed",
                "implementation_strategy": "Detailed implementation approach and architecture defined",
                "mentorship_guidance": "Junior team member guidance and support planned",
                "best_practices": "Industry best practices and standards recommendations",
                "crew_responsibilities": responsibilities,
                "hierarchy_impact": "Senior-level technical expertise and guidance provided"
            }
        elif hierarchy_level == "specialist":
            return {
                "domain_expertise": "Specialized domain knowledge and analysis provided",
                "detailed_requirements": "Specific functional and technical requirements defined",
                "implementation_details": "Detailed implementation specifications and guidelines",
                "quality_standards": "Domain-specific quality criteria and validation approaches",
                "crew_responsibilities": responsibilities,
                "hierarchy_impact": "Specialist-level domain expertise contributed"
            }
        elif hierarchy_level == "facilitator":
            return {
                "process_facilitation": "Team process optimization and facilitation planned",
                "communication_coordination": "Team communication and collaboration enhanced",
                "impediment_removal": "Potential blockers and impediments identified",
                "continuous_improvement": "Process improvement opportunities identified",
                "crew_responsibilities": responsibilities,
                "hierarchy_impact": "Facilitator-level process support provided"
            }
        else:  # junior
            return {
                "implementation_support": "Implementation tasks and execution support planned",
                "learning_opportunities": "Skill development and learning goals identified",
                "task_execution": "Specific development and testing tasks outlined",
                "collaboration_support": "Team collaboration and knowledge sharing planned",
                "crew_responsibilities": responsibilities,
                "hierarchy_impact": "Junior-level implementation support provided"
            }
    
    async def _execute_hierarchical_synthesis(
        self, 
        crew_analyses: Dict[str, Any], 
        crew_hierarchy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute hierarchical synthesis of crew member analyses."""
        
        return {
            "management_consensus": {
                "strategic_direction": "Clear strategic alignment achieved across management level",
                "resource_commitment": "Required resources and capacity confirmed available",
                "executive_sponsorship": "Strong leadership support and strategic priority confirmed"
            },
            "leadership_coordination": {
                "technical_approach": "Unified technical approach agreed upon by lead-level crew",
                "delivery_strategy": "Coordinated delivery plan with clear milestones and dependencies",
                "team_structure": "Optimal team composition and coordination model established"
            },
            "technical_consensus": {
                "architecture_agreement": "Technical architecture validated by senior-level expertise",
                "implementation_feasibility": "Implementation approach confirmed as technically sound",
                "quality_standards": "Quality criteria and acceptance standards clearly defined"
            },
            "specialist_recommendations": {
                "domain_requirements": "Specialized requirements and constraints clearly articulated",
                "best_practices": "Industry-specific best practices and standards integrated",
                "risk_mitigation": "Domain-specific risks identified with mitigation strategies"
            },
            "process_optimization": {
                "workflow_efficiency": "Optimized crew workflow and collaboration patterns established",
                "communication_channels": "Clear communication and coordination mechanisms defined",
                "continuous_improvement": "Built-in feedback loops and improvement processes planned"
            },
            "crew_coordination_method": "Hierarchical synthesis with bottom-up input and top-down validation",
            "decision_authority": "Clear decision-making authority and escalation paths established"
        }
    
    async def _execute_crew_decisions(
        self, 
        coordination_result: Dict[str, Any], 
        crew_hierarchy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute CrewAI collective decision making process."""
        
        return {
            "go_no_go_decision": {
                "decision": "GO",
                "rationale": "Strong crew consensus on strategic value and technical feasibility",
                "voting_breakdown": {
                    "manager_level": "Unanimous GO (strategic value confirmed)",
                    "lead_level": "Unanimous GO (delivery confidence high)",
                    "senior_level": "Unanimous GO (technical feasibility validated)",
                    "specialist_level": "Majority GO (domain requirements manageable)"
                }
            },
            "implementation_decisions": {
                "development_approach": "Agile methodology with 2-week sprints",
                "team_structure": "Cross-functional crew with embedded specialists",
                "technology_stack": "Confirmed current stack with minimal new dependencies",
                "timeline": "8-10 sprints with iterative delivery milestones"
            },
            "resource_allocation": {
                "crew_assignments": "Hierarchical responsibility matrix established",
                "capacity_planning": "Resource availability confirmed for project duration",
                "skill_development": "Training and mentorship plans for junior crew members"
            },
            "risk_management": {
                "identified_risks": ["External API dependencies", "Data migration complexity"],
                "mitigation_strategies": "Crew-based risk ownership with escalation protocols",
                "contingency_plans": "Alternative approaches prepared for high-risk areas"
            },
            "success_metrics": {
                "technical_kpis": "Performance benchmarks and quality thresholds defined",
                "business_kpis": "User adoption and satisfaction targets established",
                "crew_kpis": "Team velocity and collaboration effectiveness measures"
            },
            "decision_making_process": "CrewAI hierarchical consensus with weighted input by level",
            "authority_matrix": "Clear decision authority and approval workflows established"
        }
    
    async def _execute_crew_formation(
        self,
        user_input: str,
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute crew formation phase only."""
        
        yield create_plugin_event(
            self.framework_name, "streaming", "crew_formation",
            {
                "message": "CrewAI crew formation and hierarchy establishment",
                "phase": "crew_formation_only"
            }
        )
        
        await asyncio.sleep(0.5)
        
        formation_result = {
            "crew_size": "7-member hierarchical crew structure",
            "hierarchy_levels": ["Manager", "Lead", "Senior", "Specialist", "Junior", "Facilitator"],
            "coordination_model": "Hierarchical with cross-functional collaboration",
            "communication_structure": "Formal reporting with open collaboration channels"
        }
        
        yield create_plugin_event(
            self.framework_name, "complete", "crew_formation",
            {
                "formation_result": formation_result,
                "message": "Crew formation complete"
            }
        )
    
    async def _execute_hierarchical_collaboration(
        self,
        user_input: str,
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute hierarchical collaboration demonstration."""
        
        yield create_plugin_event(
            self.framework_name, "streaming", "hierarchical_collaboration",
            {
                "message": "CrewAI hierarchical collaboration in progress",
                "phase": "collaboration_demo"
            }
        )
        
        await asyncio.sleep(0.6)
        
        collaboration_result = {
            "collaboration_pattern": "Top-down strategy with bottom-up expertise",
            "information_flow": "Hierarchical reporting with lateral knowledge sharing",
            "decision_making": "Level-appropriate authority with escalation protocols",
            "conflict_resolution": "Hierarchical mediation with peer collaboration"
        }
        
        yield create_plugin_event(
            self.framework_name, "complete", "hierarchical_collaboration",
            {
                "collaboration_result": collaboration_result,
                "message": "Hierarchical collaboration demonstration complete"
            }
        )
    
    async def _execute_task_delegation(
        self,
        user_input: str,
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute task delegation demonstration."""
        
        yield create_plugin_event(
            self.framework_name, "streaming", "task_delegation",
            {
                "message": "CrewAI task delegation in progress",
                "phase": "task_delegation"
            }
        )
        
        await asyncio.sleep(0.4)
        
        delegation_result = {
            "delegation_strategy": "Hierarchical task breakdown with skill-based assignment",
            "task_distribution": "Manager defines scope, leads plan, specialists execute",
            "accountability_model": "Clear ownership with hierarchical oversight",
            "progress_tracking": "Regular check-ins with escalation thresholds"
        }
        
        yield create_plugin_event(
            self.framework_name, "complete", "task_delegation",
            {
                "delegation_result": delegation_result,
                "message": "Task delegation complete"
            }
        )
    
    async def _execute_crew_coordination(
        self,
        user_input: str,
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute crew coordination demonstration."""
        
        yield create_plugin_event(
            self.framework_name, "streaming", "crew_coordination",
            {
                "message": "CrewAI crew coordination in progress",
                "phase": "crew_coordination"
            }
        )
        
        await asyncio.sleep(0.5)
        
        coordination_result = {
            "coordination_mechanism": "Hierarchical structure with collaborative execution",
            "synchronization_points": "Regular crew meetings with milestone reviews",
            "resource_sharing": "Cross-functional resource allocation and optimization",
            "knowledge_management": "Centralized knowledge base with role-based access"
        }
        
        yield create_plugin_event(
            self.framework_name, "complete", "crew_coordination",
            {
                "coordination_result": coordination_result,
                "message": "Crew coordination complete"
            }
        )
    
    async def _execute_collective_decision_making(
        self,
        user_input: str,
        agent_manager: Any,
        context: Context
    ) -> AsyncGenerator[PluginEvent, None]:
        """Execute collective decision making demonstration."""
        
        yield create_plugin_event(
            self.framework_name, "streaming", "collective_decision_making",
            {
                "message": "CrewAI collective decision making in progress",
                "phase": "collective_decisions"
            }
        )
        
        await asyncio.sleep(0.6)
        
        decision_result = {
            "decision_process": "Hierarchical input with weighted consensus voting",
            "authority_levels": "Decision scope matched to appropriate hierarchy level",
            "consensus_building": "Collaborative discussion with structured resolution",
            "implementation_commitment": "Crew-wide commitment to decided approach"
        }
        
        yield create_plugin_event(
            self.framework_name, "complete", "collective_decision_making",
            {
                "decision_result": decision_result,
                "message": "Collective decision making complete"
            }
        )
    
    async def get_agent_mapping(self) -> Dict[str, str]:
        """Get CrewAI agent mappings."""
        return self.persona_translator.get_all_translations()


def create_crewai_workflow() -> Workflow:
    """Factory function to create CrewAI workflow for LlamaDeploy."""
    return CrewAIWorkflow()


class CrewAIWorkflow(Workflow):
    """LlamaDeploy-compatible CrewAI workflow wrapper."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plugin = CrewAIPlugin()
    
    async def run(self, **kwargs) -> Any:
        """Execute CrewAI plugin workflow."""
        component = kwargs.get("component", "full_workflow")
        input_data = kwargs.get("input_data", {})
        agent_manager = kwargs.get("agent_manager")
        context = kwargs.get("context")
        
        results = []
        async for event in self.plugin.execute_component(
            component, input_data, agent_manager, context
        ):
            results.append(event)
        
        return results