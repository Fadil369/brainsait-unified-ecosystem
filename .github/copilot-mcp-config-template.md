
# BrainSAIT Healthcare Platform - Copilot MCP Configuration

## Manual Configuration Steps

1. **Navigate to your GitHub repository settings**:
   - Go to: https://github.com/Fadil369/brainsait-unified-ecosystem/settings
   - Click: **Code & automation** → **Copilot** → **Coding agent**

2. **Add MCP Configuration**:
   Copy and paste the following JSON configuration:

```json
{
  "mcpServers": {
    "brainsait_nphies": {
      "type": "local",
      "command": "python",
      "args": [
        "-m",
        "brainsait_mcp_servers.nphies_server"
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
        "-m",
        "brainsait_mcp_servers.arabic_medical_server"
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
        "-m",
        "brainsait_mcp_servers.fhir_server"
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
        "-m",
        "brainsait_mcp_servers.compliance_server"
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
        "-m",
        "brainsait_mcp_servers.analytics_server"
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
