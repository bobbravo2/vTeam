"""Static persona translation system for cross-framework compatibility."""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any, List
from plugins.base.plugin_interface import PluginConfigurationError


class PersonaTranslator:
    """Handles translation between RFE agent personas and framework-specific agents."""
    
    def __init__(self, framework: str):
        self.framework = framework
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.load_persona_mappings()
    
    def load_persona_mappings(self):
        """Load persona mapping YAML file for the framework."""
        mapping_file = Path(__file__).parent.parent / self.framework / "persona_mapping.yaml"
        
        if not mapping_file.exists():
            raise PluginConfigurationError(
                self.framework,
                f"Persona mapping file not found: {mapping_file}"
            )
        
        try:
            with open(mapping_file, 'r') as f:
                config = yaml.safe_load(f)
                self.translations = config.get('persona_mappings', {})
        except Exception as e:
            raise PluginConfigurationError(
                self.framework,
                f"Error loading persona mappings: {e}"
            )
    
    def translate_persona(self, rfe_persona: str) -> Dict[str, Any]:
        """Translate RFE persona to framework-specific configuration.
        
        Args:
            rfe_persona: RFE agent persona key (e.g., 'PRODUCT_MANAGER')
            
        Returns:
            Framework-specific agent configuration
            
        Raises:
            PluginConfigurationError: If persona mapping not found
        """
        if rfe_persona not in self.translations:
            raise PluginConfigurationError(
                self.framework,
                f"No translation found for persona: {rfe_persona}"
            )
        
        return self.translations[rfe_persona]
    
    def get_framework_agent_id(self, rfe_persona: str) -> str:
        """Get framework-specific agent identifier.
        
        Args:
            rfe_persona: RFE agent persona key
            
        Returns:
            Framework-specific agent identifier
        """
        config = self.translate_persona(rfe_persona)
        return config.get('agent_id', rfe_persona.lower())
    
    def get_framework_role(self, rfe_persona: str) -> str:
        """Get framework-specific role/type for the persona.
        
        Args:
            rfe_persona: RFE agent persona key
            
        Returns:
            Framework-specific role identifier
        """
        config = self.translate_persona(rfe_persona)
        return config.get('framework_role', 'generic_agent')
    
    def get_capabilities(self, rfe_persona: str) -> List[str]:
        """Get framework-specific capabilities for the persona.
        
        Args:
            rfe_persona: RFE agent persona key
            
        Returns:
            List of framework-specific capabilities
        """
        config = self.translate_persona(rfe_persona)
        return config.get('capabilities', [])
    
    def get_tools(self, rfe_persona: str) -> List[str]:
        """Get framework-specific tools for the persona.
        
        Args:
            rfe_persona: RFE agent persona key
            
        Returns:
            List of framework-specific tools
        """
        config = self.translate_persona(rfe_persona)
        return config.get('tools', [])
    
    def get_all_translations(self) -> Dict[str, Dict[str, Any]]:
        """Get all persona translations for this framework."""
        return self.translations.copy()
    
    def validate_translations(self, required_personas: List[str]) -> List[str]:
        """Validate that all required personas have translations.
        
        Args:
            required_personas: List of RFE personas that must be translated
            
        Returns:
            List of missing persona translations
        """
        missing = []
        for persona in required_personas:
            if persona not in self.translations:
                missing.append(persona)
        return missing


def create_persona_translator(framework: str) -> PersonaTranslator:
    """Factory function to create a PersonaTranslator for a framework.
    
    Args:
        framework: Framework identifier ('openhands', 'langchain', 'crewai')
        
    Returns:
        PersonaTranslator instance
    """
    return PersonaTranslator(framework)


# Standard RFE personas that should be supported by all frameworks
STANDARD_RFE_PERSONAS = [
    "PRODUCT_MANAGER",
    "STAFF_ENGINEER",
    "UX_RESEARCHER",
    "UX_ARCHITECT",
    "UX_FEATURE_LEAD",
    "UX_TEAM_LEAD",
    "TEAM_LEAD",
    "TEAM_MEMBER",
    "DELIVERY_OWNER",
    "ENGINEERING_MANAGER",
    "SCRUM_MASTER",
    "TECHNICAL_WRITER",
    "TECHNICAL_WRITING_MANAGER",
    "DOCUMENTATION_PROGRAM_MANAGER",
    "CONTENT_STRATEGIST",
    "PXE"
]