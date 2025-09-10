"""Validate plugin structure and configuration."""

import os
import yaml
from pathlib import Path


def validate_plugin_structure():
    """Validate plugin directory structure and configurations."""
    
    plugins_dir = Path(__file__).parent
    base_dir = plugins_dir / "base"
    
    print("🔍 Validating plugin structure...")
    
    # Check base infrastructure
    required_base_files = [
        "plugin_interface.py",
        "event_mapper.py", 
        "agent_translator.py",
        "orchestrator.py"
    ]
    
    for file in required_base_files:
        file_path = base_dir / file
        if file_path.exists():
            print(f"✅ Base: {file}")
        else:
            print(f"❌ Missing base file: {file}")
    
    # Check plugin implementations
    frameworks = ["openhands", "langchain", "crewai"]
    
    for framework in frameworks:
        framework_dir = plugins_dir / framework
        print(f"\n📁 Validating {framework} plugin:")
        
        # Check plugin files
        plugin_file = framework_dir / f"{framework}_plugin.py"
        requirements_file = framework_dir / "requirements.txt"
        mapping_file = framework_dir / "persona_mapping.yaml"
        
        if plugin_file.exists():
            print(f"  ✅ Plugin implementation: {plugin_file.name}")
        else:
            print(f"  ❌ Missing plugin file: {plugin_file.name}")
        
        if requirements_file.exists():
            print(f"  ✅ Requirements: {requirements_file.name}")
        else:
            print(f"  ❌ Missing requirements: {requirements_file.name}")
        
        if mapping_file.exists():
            print(f"  ✅ Persona mapping: {mapping_file.name}")
            
            # Validate YAML structure
            try:
                with open(mapping_file, 'r') as f:
                    config = yaml.safe_load(f)
                    
                if 'persona_mappings' in config:
                    personas = list(config['persona_mappings'].keys())
                    print(f"  📋 Mapped personas: {len(personas)}")
                    
                    # Check for key personas
                    key_personas = ["PRODUCT_MANAGER", "STAFF_ENGINEER", "UX_RESEARCHER"]
                    for persona in key_personas:
                        if persona in personas:
                            print(f"    ✅ {persona}")
                        else:
                            print(f"    ❌ Missing: {persona}")
                else:
                    print(f"  ⚠️  No persona_mappings section found")
                    
            except Exception as e:
                print(f"  ❌ YAML error: {e}")
        else:
            print(f"  ❌ Missing mapping file: {mapping_file.name}")
    
    # Check deployment configuration
    deployment_file = plugins_dir.parent / "deployment.yml"
    print(f"\n🚀 Checking deployment configuration:")
    
    if deployment_file.exists():
        print(f"  ✅ Deployment file exists")
        
        try:
            with open(deployment_file, 'r') as f:
                content = f.read()
                
            for framework in frameworks:
                service_name = f"{framework}-plugin"
                if service_name in content:
                    print(f"  ✅ Service configured: {service_name}")
                else:
                    print(f"  ❌ Missing service: {service_name}")
        except Exception as e:
            print(f"  ❌ Deployment file error: {e}")
    else:
        print(f"  ❌ Deployment file not found")
    
    print(f"\n🎯 Plugin structure validation complete!")


def validate_persona_coverage():
    """Validate persona coverage across frameworks."""
    
    plugins_dir = Path(__file__).parent
    
    print("\n👥 Validating persona coverage...")
    
    # Standard personas that should be supported
    standard_personas = [
        "PRODUCT_MANAGER", "STAFF_ENGINEER", "UX_RESEARCHER", "UX_ARCHITECT",
        "UX_FEATURE_LEAD", "UX_TEAM_LEAD", "TEAM_LEAD", "TEAM_MEMBER",
        "DELIVERY_OWNER", "ENGINEERING_MANAGER", "SCRUM_MASTER",
        "TECHNICAL_WRITER", "TECHNICAL_WRITING_MANAGER", 
        "DOCUMENTATION_PROGRAM_MANAGER", "CONTENT_STRATEGIST", "PXE"
    ]
    
    frameworks = ["openhands", "langchain", "crewai"]
    
    for framework in frameworks:
        mapping_file = plugins_dir / framework / "persona_mapping.yaml"
        
        if not mapping_file.exists():
            print(f"❌ {framework}: No mapping file")
            continue
        
        try:
            with open(mapping_file, 'r') as f:
                config = yaml.safe_load(f)
            
            mapped_personas = set(config.get('persona_mappings', {}).keys())
            missing_personas = set(standard_personas) - mapped_personas
            extra_personas = mapped_personas - set(standard_personas)
            
            print(f"\n📊 {framework.upper()} Coverage:")
            print(f"  ✅ Mapped: {len(mapped_personas)}/{len(standard_personas)}")
            
            if missing_personas:
                print(f"  ❌ Missing: {len(missing_personas)}")
                for persona in sorted(missing_personas):
                    print(f"    - {persona}")
            
            if extra_personas:
                print(f"  ℹ️  Extra: {len(extra_personas)}")
                for persona in sorted(extra_personas):
                    print(f"    + {persona}")
                    
        except Exception as e:
            print(f"❌ {framework}: Error reading mapping - {e}")
    
    print(f"\n👥 Persona coverage validation complete!")


if __name__ == "__main__":
    validate_plugin_structure()
    validate_persona_coverage()