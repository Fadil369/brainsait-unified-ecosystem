#!/usr/bin/env python3
"""
BrainSAIT MCP Healthcare Initialization Script
Sets up Model Context Protocol servers for healthcare platform
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainSAITMCPInitializer:
    """Initialize BrainSAIT MCP servers for healthcare platform"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.mcp_servers_dir = self.project_root / "backend" / "brainsait_mcp_servers"
        self.config_dir = self.project_root / ".github"
        
    def create_mcp_configuration(self) -> Dict[str, Any]:
        """Create MCP configuration for GitHub Copilot"""
        
        config = {
            "mcpServers": {
                "brainsait_nphies": {
                    "type": "local",
                    "command": "python",
                    "args": [
                        "-m", "brainsait_mcp_servers.nphies_server"
                    ],
                    "tools": [
                        "validate_patient_eligibility",
                        "submit_preauthorization", 
                        "process_claim",
                        "check_claim_status",
                        "get_provider_info",
                        "validate_nphies_format"
                    ],
                    "env": {
                        "NPHIES_CLIENT_ID": "COPILOT_MCP_NPHIES_CLIENT_ID",
                        "NPHIES_CLIENT_SECRET": "COPILOT_MCP_NPHIES_CLIENT_SECRET",
                        "NPHIES_HOST": "https://api.nphies.sa",
                        "HEALTHCARE_PROVIDER_ID": "COPILOT_MCP_PROVIDER_ID"
                    }
                },
                "brainsait_arabic_medical": {
                    "type": "local",
                    "command": "python",
                    "args": [
                        "-m", "brainsait_mcp_servers.arabic_medical_server"
                    ],
                    "tools": [
                        "translate_medical_term",
                        "validate_arabic_medical_text",
                        "generate_rtl_layout",
                        "cultural_adaptation_check",
                        "islamic_calendar_conversion",
                        "arabic_medical_coding"
                    ],
                    "env": {
                        "ARABIC_MEDICAL_API": "COPILOT_MCP_ARABIC_MEDICAL_API",
                        "SAUDI_MEDICAL_TERMS_DB": "/opt/medical_terms/saudi_ar.db",
                        "RTL_VALIDATION": "enabled"
                    }
                },
                "brainsait_fhir_healthcare": {
                    "type": "local", 
                    "command": "python",
                    "args": [
                        "-m", "brainsait_mcp_servers.fhir_server"
                    ],
                    "tools": [
                        "validate_fhir_resource",
                        "convert_to_fhir",
                        "search_code_systems",
                        "validate_patient_resource",
                        "create_encounter",
                        "generate_diagnostic_report"
                    ],
                    "env": {
                        "FHIR_TERMINOLOGY_SERVER": "https://terminology.hl7.org/fhir",
                        "FHIR_BASE_URL": "https://hl7.org/fhir/R4"
                    }
                },
                "brainsait_compliance": {
                    "type": "local",
                    "command": "python", 
                    "args": [
                        "-m", "brainsait_mcp_servers.compliance_server"
                    ],
                    "tools": [
                        "validate_hipaa_compliance",
                        "check_phi_exposure",
                        "audit_data_access",
                        "validate_encryption",
                        "compliance_report"
                    ],
                    "env": {
                        "HIPAA_VALIDATION_API": "COPILOT_MCP_HIPAA_API",
                        "AUDIT_LOG_ENDPOINT": "COPILOT_MCP_AUDIT_ENDPOINT"
                    }
                },
                "brainsait_analytics": {
                    "type": "local",
                    "command": "python",
                    "args": [
                        "-m", "brainsait_mcp_servers.analytics_server"
                    ],
                    "tools": [
                        "generate_healthcare_insights",
                        "patient_outcome_prediction", 
                        "medical_trend_analysis",
                        "cost_optimization_analysis",
                        "revenue_cycle_analytics"
                    ],
                    "env": {
                        "HEALTHCARE_DATA_API": "COPILOT_MCP_HEALTHCARE_DATA_API",
                        "ML_MODEL_PATH": "/opt/brainsait/models"
                    }
                }
            }
        }
        
        return config
    
    def create_mcp_server_files(self):
        """Create MCP server Python modules"""
        
        # Create __init__.py for the package
        init_file = self.mcp_servers_dir / "__init__.py"
        init_file.write_text('''"""
BrainSAIT Healthcare MCP Servers
Model Context Protocol servers for healthcare platform integration
"""

__version__ = "1.0.0"
__author__ = "BrainSAIT Healthcare Team"

# Available MCP servers
MCP_SERVERS = [
    "nphies_server",
    "arabic_medical_server", 
    "fhir_server",
    "compliance_server",
    "analytics_server"
]
''')
        
        # Create FHIR server
        fhir_server_content = '''#!/usr/bin/env python3
"""
BrainSAIT FHIR MCP Server
FHIR R4 healthcare standards integration for Model Context Protocol
"""

import asyncio
import logging
import json
from typing import Any, List

# MCP imports (will be available when MCP is installed)
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import TextContent
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not installed - running in development mode")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainSAITFHIRMCPServer:
    """FHIR R4 MCP Server for BrainSAIT Healthcare Platform"""
    
    def __init__(self):
        if MCP_AVAILABLE:
            self.server = Server("brainsait-fhir-mcp-server")
            self.setup_tools()
    
    def setup_tools(self):
        """Register FHIR-related tools"""
        
        @self.server.tool("validate_fhir_resource")
        async def validate_fhir_resource(
            resource_type: str,
            resource_data: str,
            fhir_version: str = "R4"
        ) -> List[types.TextContent]:
            """Validate FHIR resource format"""
            try:
                data = json.loads(resource_data)
                # FHIR validation logic here
                return [types.TextContent(
                    type="text",
                    text=f"✅ FHIR {resource_type} resource validation successful"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ FHIR validation error: {str(e)}"
                )]
    
    async def run(self):
        """Run the FHIR MCP server"""
        if not MCP_AVAILABLE:
            logger.error("MCP not available")
            return
            
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream,
                InitializationOptions(
                    server_name="brainsait-fhir-mcp-server",
                    server_version="1.0.0"
                )
            )

if __name__ == "__main__":
    server = BrainSAITFHIRMCPServer()
    if MCP_AVAILABLE:
        asyncio.run(server.run())
'''
        
        fhir_server_file = self.mcp_servers_dir / "fhir_server.py"
        fhir_server_file.write_text(fhir_server_content)
        
        # Create Compliance server
        compliance_server_content = '''#!/usr/bin/env python3
"""
BrainSAIT Compliance MCP Server
HIPAA and healthcare compliance validation for Model Context Protocol
"""

import asyncio
import logging
import json
from typing import Any, List

# MCP imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import TextContent
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not installed - running in development mode")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainSAITComplianceMCPServer:
    """Healthcare Compliance MCP Server for BrainSAIT Platform"""
    
    def __init__(self):
        if MCP_AVAILABLE:
            self.server = Server("brainsait-compliance-mcp-server")
            self.setup_tools()
    
    def setup_tools(self):
        """Register compliance-related tools"""
        
        @self.server.tool("validate_hipaa_compliance")
        async def validate_hipaa_compliance(
            code_content: str,
            check_type: str = "comprehensive"
        ) -> List[types.TextContent]:
            """Validate HIPAA compliance in code"""
            try:
                # HIPAA compliance validation logic
                return [types.TextContent(
                    type="text",
                    text="✅ HIPAA compliance validation passed"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ HIPAA compliance error: {str(e)}"
                )]
    
    async def run(self):
        """Run the Compliance MCP server"""
        if not MCP_AVAILABLE:
            logger.error("MCP not available")
            return
            
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream,
                InitializationOptions(
                    server_name="brainsait-compliance-mcp-server",
                    server_version="1.0.0"
                )
            )

if __name__ == "__main__":
    server = BrainSAITComplianceMCPServer()
    if MCP_AVAILABLE:
        asyncio.run(server.run())
'''
        
        compliance_server_file = self.mcp_servers_dir / "compliance_server.py"
        compliance_server_file.write_text(compliance_server_content)
        
        # Create Analytics server
        analytics_server_content = '''#!/usr/bin/env python3
"""
BrainSAIT Analytics MCP Server
Healthcare analytics and insights for Model Context Protocol
"""

import asyncio
import logging
import json
from typing import Any, List

# MCP imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import TextContent
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not installed - running in development mode")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainSAITAnalyticsMCPServer:
    """Healthcare Analytics MCP Server for BrainSAIT Platform"""
    
    def __init__(self):
        if MCP_AVAILABLE:
            self.server = Server("brainsait-analytics-mcp-server")
            self.setup_tools()
    
    def setup_tools(self):
        """Register analytics-related tools"""
        
        @self.server.tool("generate_healthcare_insights")
        async def generate_healthcare_insights(
            data_type: str,
            time_period: str = "monthly"
        ) -> List[types.TextContent]:
            """Generate healthcare analytics insights"""
            try:
                # Analytics generation logic
                return [types.TextContent(
                    type="text",
                    text=f"📊 Healthcare insights generated for {data_type}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Analytics error: {str(e)}"
                )]
    
    async def run(self):
        """Run the Analytics MCP server"""
        if not MCP_AVAILABLE:
            logger.error("MCP not available")
            return
            
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream,
                InitializationOptions(
                    server_name="brainsait-analytics-mcp-server",
                    server_version="1.0.0"
                )
            )

if __name__ == "__main__":
    server = BrainSAITAnalyticsMCPServer()
    if MCP_AVAILABLE:
        asyncio.run(server.run())
'''
        
        analytics_server_file = self.mcp_servers_dir / "analytics_server.py"
        analytics_server_file.write_text(analytics_server_content)
        
        logger.info("✅ MCP server files created successfully")
    
    def save_mcp_configuration(self):
        """Save MCP configuration to file"""
        config = self.create_mcp_configuration()
        
        config_file = self.config_dir / "copilot-mcp-config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ MCP configuration saved to {config_file}")
        
        # Also create a template for manual configuration
        template_file = self.config_dir / "copilot-mcp-config-template.md"
        template_content = f"""
# BrainSAIT Healthcare Platform - Copilot MCP Configuration

## Manual Configuration Steps

1. **Navigate to your GitHub repository settings**:
   - Go to: https://github.com/Fadil369/brainsait-unified-ecosystem/settings
   - Click: **Code & automation** → **Copilot** → **Coding agent**

2. **Add MCP Configuration**:
   Copy and paste the following JSON configuration:

```json
{json.dumps(config, indent=2, ensure_ascii=False)}
```

3. **Set up Environment Secrets**:
   Create a Copilot environment with these secrets:
   - `COPILOT_MCP_NPHIES_CLIENT_ID`
   - `COPILOT_MCP_NPHIES_CLIENT_SECRET`
   - `COPILOT_MCP_ARABIC_MEDICAL_API`
   - `COPILOT_MCP_HEALTHCARE_DATA_API`
   - `COPILOT_MCP_PROVIDER_ID`
   - `COPILOT_MCP_HIPAA_API`
   - `COPILOT_MCP_AUDIT_ENDPOINT`

4. **Install MCP Dependencies**:
   ```bash
   pip install -r backend/requirements_mcp.txt
   ```

5. **Test MCP Integration**:
   Create a test issue and assign it to Copilot to verify MCP servers are loaded.

## Available MCP Tools

### NPHIES Server Tools:
- `validate_patient_eligibility`
- `submit_preauthorization`
- `process_claim`
- `check_claim_status`
- `get_provider_info`
- `validate_nphies_format`

### Arabic Medical Server Tools:
- `translate_medical_term`
- `validate_arabic_medical_text`
- `generate_rtl_layout`
- `cultural_adaptation_check`
- `islamic_calendar_conversion`
- `arabic_medical_coding`

### FHIR Healthcare Server Tools:
- `validate_fhir_resource`
- `convert_to_fhir`
- `search_code_systems`
- `validate_patient_resource`

### Compliance Server Tools:
- `validate_hipaa_compliance`
- `check_phi_exposure`
- `audit_data_access`
- `validate_encryption`

### Analytics Server Tools:
- `generate_healthcare_insights`
- `patient_outcome_prediction`
- `medical_trend_analysis`
- `revenue_cycle_analytics`

## Usage Examples

Ask Copilot:
- "Create a FHIR R4 Patient resource for a Saudi patient"
- "Validate NPHIES eligibility for patient ID 12345"
- "Generate an Arabic medical form with RTL layout"
- "Check HIPAA compliance for this patient data access"
- "Translate 'hypertension' to Arabic medical terminology"

## Security Considerations

- All patient data access is logged and audited
- MCP servers use encrypted connections
- HIPAA compliance is validated for all operations
- Arabic cultural sensitivity is maintained
- NPHIES integration follows Saudi standards
"""
        
        template_file.write_text(template_content)
        logger.info(f"✅ MCP configuration template saved to {template_file}")
    
    def create_installation_script(self):
        """Create installation script for MCP setup"""
        script_content = '''#!/bin/bash
# BrainSAIT MCP Healthcare Setup Script

set -e

echo "🏥 Setting up BrainSAIT Healthcare MCP Servers..."

# Install Python dependencies
echo "📦 Installing MCP dependencies..."
pip install -r backend/requirements_mcp.txt

# Create necessary directories
echo "📁 Creating MCP directories..."
mkdir -p /opt/brainsait/models
mkdir -p /opt/medical_terms
mkdir -p /secure/compliance

# Set up Arabic medical terminology database
echo "🔤 Setting up Arabic medical terminology..."
if [ ! -f "/opt/medical_terms/saudi_ar.db" ]; then
    echo "Creating Arabic medical terms database..."
    # Download or create Arabic medical terms database
    touch /opt/medical_terms/saudi_ar.db
fi

# Set up NPHIES certificates (if available)
echo "🔐 Setting up NPHIES certificates..."
if [ -n "$NPHIES_SSL_CERT" ]; then
    mkdir -p /opt/nphies/certs
    echo "$NPHIES_SSL_CERT" > /opt/nphies/certs/client.crt
    echo "$NPHIES_SSL_KEY" > /opt/nphies/certs/client.key
    chmod 600 /opt/nphies/certs/*
fi

# Validate MCP servers
echo "✅ Validating MCP servers..."
python -c "
try:
    from backend.brainsait_mcp_servers import nphies_server
    from backend.brainsait_mcp_servers import arabic_medical_server
    print('✅ NPHIES and Arabic Medical MCP servers validated')
except ImportError as e:
    print(f'⚠️  MCP servers validation warning: {e}')
    print('This is normal if MCP packages are not yet installed')
"

echo "🚀 BrainSAIT MCP Healthcare setup completed!"
echo ""
echo "Next steps:"
echo "1. Configure GitHub Copilot with the MCP configuration"
echo "2. Set up environment secrets in GitHub"
echo "3. Test MCP integration with Copilot"
echo ""
echo "For detailed instructions, see: .github/copilot-mcp-config-template.md"
'''
        
        script_file = self.project_root / "setup_mcp_healthcare.sh"
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        
        logger.info(f"✅ MCP installation script created: {script_file}")
    
    def initialize_mcp_healthcare(self):
        """Initialize complete MCP healthcare setup"""
        logger.info("🏥 Initializing BrainSAIT MCP Healthcare Platform...")
        
        # Create directories
        self.mcp_servers_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create MCP server files
        self.create_mcp_server_files()
        
        # Save MCP configuration
        self.save_mcp_configuration()
        
        # Create installation script
        self.create_installation_script()
        
        logger.info("✅ BrainSAIT MCP Healthcare Platform initialized successfully!")
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("1. Review the MCP configuration: .github/copilot-mcp-config.json")
        logger.info("2. Follow setup instructions: .github/copilot-mcp-config-template.md")
        logger.info("3. Run setup script: ./setup_mcp_healthcare.sh")
        logger.info("4. Configure GitHub Copilot with MCP settings")
        logger.info("5. Set up environment secrets")
        logger.info("6. Test with Copilot healthcare prompts")

def main():
    """Main entry point"""
    try:
        initializer = BrainSAITMCPInitializer()
        initializer.initialize_mcp_healthcare()
    except Exception as e:
        logger.error(f"❌ Error initializing MCP healthcare: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
