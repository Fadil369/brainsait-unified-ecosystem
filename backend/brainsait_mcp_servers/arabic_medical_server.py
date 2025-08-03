#!/usr/bin/env python3
"""
BrainSAIT Arabic Medical Context MCP Server
Specialized Model Context Protocol server for Arabic medical terminology,
RTL layouts, and Saudi healthcare cultural adaptations
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timezone
from typing import Any, Sequence, Dict, List

# MCP Server imports (these will be available when MCP is properly installed)
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import Resource, Tool, TextContent
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    # Fallback for development without MCP installed
    MCP_AVAILABLE = False
    print("MCP not installed - running in development mode")

# Healthcare-specific imports
from ..services.ai_arabic_service import ArabicAIService
from ..core.arabic_support import ArabicProcessor
from ..core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainSAITArabicMedicalMCPServer:
    """
    Arabic Medical Context MCP Server for BrainSAIT Healthcare Platform
    
    Provides GitHub Copilot with tools for:
    - Arabic medical terminology translation and validation
    - RTL layout generation and validation
    - Cultural adaptation for Saudi healthcare
    - Islamic calendar conversions
    - Arabic medical text processing
    - Medical document Arabic localization
    """
    
    def __init__(self):
        if MCP_AVAILABLE:
            self.server = Server("brainsait-arabic-medical-mcp-server")
        self.settings = get_settings()
        self.arabic_ai_service = ArabicAIService()
        self.arabic_processor = ArabicProcessor()
        if MCP_AVAILABLE:
            self.setup_tools()
            self.setup_resources()

    def setup_tools(self):
        """Register all Arabic medical tools for Copilot"""
        
        @self.server.tool("translate_medical_term")
        async def translate_medical_term(
            term: str,
            source_language: str = "en",
            target_language: str = "ar",
            medical_specialty: str = "general",
            context: str = "clinical"
        ) -> list[types.TextContent]:
            """
            Translate medical terminology between Arabic and English
            
            Args:
                term: Medical term to translate
                source_language: Source language (en/ar)
                target_language: Target language (ar/en)
                medical_specialty: Medical specialty context
                context: Usage context (clinical/administrative/patient)
            """
            try:
                logger.info(f"Translating medical term: {term}")
                
                translation = await self.arabic_ai_service.translate_medical_term(
                    term=term,
                    source_lang=source_language,
                    target_lang=target_language,
                    specialty=medical_specialty,
                    context=context
                )
                
                result_text = f"""
🏥 Arabic Medical Translation

📝 Original Term: {term}
🔄 Translation: {translation.translated_term}
🏥 Medical Specialty: {medical_specialty}
📋 Context: {context}

📖 Additional Translations:
{chr(10).join([f"  • {alt}" for alt in translation.alternative_translations])}

💡 Usage Notes:
- Formality Level: {translation.formality_level}
- Regional Variant: {translation.regional_variant}
- Gender Consideration: {translation.gender_specific}

📚 Medical Context:
{translation.medical_context_notes}

🔤 Transliteration: {translation.transliteration}
📊 Confidence Score: {translation.confidence_score}%
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error translating medical term: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Arabic Medical Translation Error: {str(e)}"
                )]

        @self.server.tool("validate_arabic_medical_text")
        async def validate_arabic_medical_text(
            arabic_text: str,
            text_type: str = "clinical_note",  # clinical_note|prescription|report|consent
            validation_level: str = "comprehensive"  # basic|standard|comprehensive
        ) -> list[types.TextContent]:
            """
            Validate Arabic medical text for accuracy, cultural appropriateness, and medical correctness
            
            Args:
                arabic_text: Arabic text to validate
                text_type: Type of medical text
                validation_level: Depth of validation
            """
            try:
                logger.info(f"Validating Arabic medical text: {text_type}")
                
                validation = await self.arabic_ai_service.validate_medical_text(
                    text=arabic_text,
                    text_type=text_type,
                    level=validation_level
                )
                
                result_text = f"""
✅ Arabic Medical Text Validation

📝 Text Type: {text_type}
📊 Overall Score: {validation.overall_score}%
✅ Validation Level: {validation_level}

🔤 Language Validation:
- Grammar Score: {validation.grammar_score}%
- Spelling Accuracy: {validation.spelling_score}%
- Medical Terminology: {validation.terminology_score}%

🏥 Medical Accuracy:
- Clinical Accuracy: {validation.clinical_accuracy}%
- Medication Names: {validation.medication_accuracy}%
- Dosage Format: {validation.dosage_format_score}%

🌍 Cultural Appropriateness:
- Cultural Sensitivity: {validation.cultural_score}%
- Islamic Considerations: {validation.islamic_compliance}%
- Regional Appropriateness: {validation.regional_score}%

⚠️ Issues Found:
{chr(10).join([f"  • {issue.type}: {issue.description} (Line {issue.line})" for issue in validation.issues]) if validation.issues else "None"}

💡 Suggestions:
{chr(10).join([f"  • {suggestion}" for suggestion in validation.suggestions]) if validation.suggestions else "Text meets all standards"}

📋 Compliance Status:
- HIPAA Compliant: {validation.hipaa_compliant}
- Saudi Medical Standards: {validation.saudi_standards_compliant}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error validating Arabic text: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Arabic Medical Text Validation Error: {str(e)}"
                )]

        @self.server.tool("generate_rtl_layout")
        async def generate_rtl_layout(
            component_type: str,  # form|table|card|dialog|report
            content_structure: str,  # JSON string describing content
            ui_framework: str = "material-ui",
            accessibility_level: str = "wcag-aa"
        ) -> list[types.TextContent]:
            """
            Generate RTL (Right-to-Left) layout code for Arabic medical interfaces
            
            Args:
                component_type: Type of UI component
                content_structure: JSON describing content and layout
                ui_framework: UI framework (material-ui|antd|chakra-ui)
                accessibility_level: Accessibility compliance level
            """
            try:
                logger.info(f"Generating RTL layout for {component_type}")
                
                content = json.loads(content_structure)
                layout = await self.arabic_processor.generate_rtl_layout(
                    component_type=component_type,
                    content=content,
                    framework=ui_framework,
                    accessibility=accessibility_level
                )
                
                result_text = f"""
🎨 RTL Layout Generation

🔧 Component Type: {component_type}
🖼️ UI Framework: {ui_framework}
♿ Accessibility: {accessibility_level}

💻 Generated Code:
```{layout.code_language}
{layout.generated_code}
```

📱 CSS Styles:
```css
{layout.rtl_styles}
```

🌐 Responsive Breakpoints:
```css
{layout.responsive_styles}
```

♿ Accessibility Features:
{chr(10).join([f"  • {feature}" for feature in layout.accessibility_features])}

📋 RTL Considerations Applied:
{chr(10).join([f"  • {consideration}" for consideration in layout.rtl_considerations])}

🔤 Font Configuration:
- Primary Font: {layout.font_config.primary}
- Fallback Fonts: {', '.join(layout.font_config.fallbacks)}
- Font Size: {layout.font_config.size}
- Line Height: {layout.font_config.line_height}

💡 Best Practices Implemented:
{chr(10).join([f"  • {practice}" for practice in layout.best_practices])}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error generating RTL layout: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ RTL Layout Generation Error: {str(e)}"
                )]

        @self.server.tool("cultural_adaptation_check")
        async def cultural_adaptation_check(
            content: str,
            content_type: str = "medical_form",  # medical_form|patient_info|consent|instructions
            target_audience: str = "patients",  # patients|healthcare_providers|administrators
            cultural_context: str = "saudi_arabia"
        ) -> list[types.TextContent]:
            """
            Check content for cultural appropriateness in Saudi healthcare context
            
            Args:
                content: Content to check (can be Arabic or English)
                content_type: Type of healthcare content
                target_audience: Intended audience
                cultural_context: Cultural context for adaptation
            """
            try:
                logger.info(f"Checking cultural adaptation for {content_type}")
                
                adaptation = await self.arabic_ai_service.check_cultural_adaptation(
                    content=content,
                    content_type=content_type,
                    audience=target_audience,
                    context=cultural_context
                )
                
                result_text = f"""
🌍 Cultural Adaptation Analysis

📋 Content Type: {content_type}
👥 Target Audience: {target_audience}
🏛️ Cultural Context: {cultural_context}

📊 Cultural Appropriateness Score: {adaptation.appropriateness_score}%

🕌 Islamic Considerations:
- Religious Sensitivity: {adaptation.religious_sensitivity}%
- Prayer Time Considerations: {adaptation.prayer_time_awareness}
- Gender Sensitivity: {adaptation.gender_sensitivity}%
- Modesty Requirements: {adaptation.modesty_compliance}

🇸🇦 Saudi Cultural Factors:
- Language Formality: {adaptation.language_formality}
- Authority Respect: {adaptation.authority_respect}%
- Family Involvement: {adaptation.family_involvement_score}%
- Traditional Medicine: {adaptation.traditional_medicine_respect}%

⚠️ Cultural Issues Identified:
{chr(10).join([f"  • {issue.category}: {issue.description}" for issue in adaptation.cultural_issues]) if adaptation.cultural_issues else "None"}

💡 Adaptation Recommendations:
{chr(10).join([f"  • {rec.priority}: {rec.description}" for rec in adaptation.recommendations]) if adaptation.recommendations else "Content is culturally appropriate"}

🔄 Suggested Modifications:
{chr(10).join([f"  • Original: {mod.original}" + chr(10) + f"    Suggested: {mod.suggested}" for mod in adaptation.modifications]) if adaptation.modifications else "No modifications needed"}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error checking cultural adaptation: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Cultural Adaptation Check Error: {str(e)}"
                )]

        @self.server.tool("islamic_calendar_conversion")
        async def islamic_calendar_conversion(
            date_value: str,
            source_calendar: str = "gregorian",  # gregorian|hijri
            target_calendar: str = "hijri",      # hijri|gregorian
            include_religious_context: bool = True
        ) -> list[types.TextContent]:
            """
            Convert dates between Gregorian and Islamic (Hijri) calendars
            
            Args:
                date_value: Date to convert (YYYY-MM-DD or Islamic format)
                source_calendar: Source calendar system
                target_calendar: Target calendar system
                include_religious_context: Include religious significance
            """
            try:
                logger.info(f"Converting calendar date: {date_value}")
                
                conversion = await self.arabic_processor.convert_calendar_date(
                    date=date_value,
                    source=source_calendar,
                    target=target_calendar,
                    religious_context=include_religious_context
                )
                
                result_text = f"""
📅 Islamic Calendar Conversion

📆 Original Date: {date_value} ({source_calendar})
🔄 Converted Date: {conversion.converted_date} ({target_calendar})

📋 Date Information:
- Arabic Date Format: {conversion.arabic_format}
- English Date Format: {conversion.english_format}
- Day of Week: {conversion.day_of_week}
- Islamic Month: {conversion.islamic_month_name}

🕌 Religious Context:
- Islamic Month: {conversion.islamic_month}
- Sacred Month: {conversion.is_sacred_month}
- Ramadan Period: {conversion.is_ramadan}
- Hajj Season: {conversion.is_hajj_season}

📚 Cultural Significance:
{conversion.cultural_significance if conversion.cultural_significance else "No special significance"}

🕐 Prayer Times Consideration:
- Affects Prayer Schedule: {conversion.affects_prayer_times}
- Special Prayers: {conversion.special_prayers if conversion.special_prayers else "None"}

💡 Healthcare Considerations:
{chr(10).join([f"  • {consideration}" for consideration in conversion.healthcare_considerations]) if conversion.healthcare_considerations else "Standard scheduling applies"}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error converting calendar date: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Islamic Calendar Conversion Error: {str(e)}"
                )]

        @self.server.tool("arabic_medical_coding")
        async def arabic_medical_coding(
            medical_text: str,
            coding_system: str = "icd10",  # icd10|cpt|hcpcs|snomed
            language: str = "arabic",
            include_descriptions: bool = True
        ) -> list[types.TextContent]:
            """
            Extract and suggest medical codes from Arabic medical text
            
            Args:
                medical_text: Arabic medical text to analyze
                coding_system: Medical coding system to use
                language: Language of the text
                include_descriptions: Include code descriptions
            """
            try:
                logger.info(f"Processing Arabic medical coding for {coding_system}")
                
                coding = await self.arabic_ai_service.extract_medical_codes(
                    text=medical_text,
                    system=coding_system,
                    language=language,
                    descriptions=include_descriptions
                )
                
                result_text = f"""
🏥 Arabic Medical Coding Analysis

📋 Coding System: {coding_system.upper()}
🔤 Text Language: {language}
📊 Confidence Level: {coding.overall_confidence}%

🔍 Extracted Codes:
{chr(10).join([f"  • {code.code}: {code.description_en}" + (f" | {code.description_ar}" if code.description_ar else "") + f" (Confidence: {code.confidence}%)" for code in coding.extracted_codes])}

🏥 Suggested Diagnoses:
{chr(10).join([f"  • {diag.arabic_term} → {diag.icd10_code}: {diag.english_description}" for diag in coding.suggested_diagnoses])}

💊 Medications Identified:
{chr(10).join([f"  • {med.arabic_name} → {med.generic_name} ({med.dosage})" for med in coding.identified_medications])}

🔬 Procedures Mentioned:
{chr(10).join([f"  • {proc.arabic_description} → {proc.cpt_code}: {proc.english_description}" for proc in coding.mentioned_procedures])}

⚠️ Coding Uncertainties:
{chr(10).join([f"  • {uncertainty.text}: {uncertainty.reason}" for uncertainty in coding.uncertainties]) if coding.uncertainties else "All codes identified with high confidence"}

💡 Coding Recommendations:
{chr(10).join([f"  • {rec}" for rec in coding.recommendations]) if coding.recommendations else "Coding appears complete and accurate"}
"""
                
                return [types.TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Error processing Arabic medical coding: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ Arabic Medical Coding Error: {str(e)}"
                )]

    def setup_resources(self):
        """Setup MCP resources for Arabic medical terminology and cultural guidelines"""
        
        @self.server.resource("arabic-medical://terminology/{category}")
        async def get_arabic_medical_terminology(uri: str) -> str:
            """Provide Arabic medical terminology by category"""
            category = uri.split("/")[-1]
            
            terminology = {
                "anatomy": {
                    "title": "Arabic Anatomical Terms",
                    "description": "Comprehensive Arabic anatomical terminology",
                    "terms": {
                        "head": {"arabic": "رأس", "transliteration": "ra's"},
                        "heart": {"arabic": "قلب", "transliteration": "qalb"},
                        "brain": {"arabic": "دماغ", "transliteration": "dimagh"},
                        "liver": {"arabic": "كبد", "transliteration": "kabid"},
                        "kidney": {"arabic": "كلية", "transliteration": "kilya"}
                    }
                },
                "symptoms": {
                    "title": "Arabic Symptom Terminology",
                    "description": "Common medical symptoms in Arabic",
                    "terms": {
                        "pain": {"arabic": "ألم", "transliteration": "alam"},
                        "fever": {"arabic": "حمى", "transliteration": "humma"},
                        "headache": {"arabic": "صداع", "transliteration": "suda'"},
                        "nausea": {"arabic": "غثيان", "transliteration": "ghuthyan"},
                        "fatigue": {"arabic": "إرهاق", "transliteration": "irhaq"}
                    }
                },
                "medications": {
                    "title": "Arabic Medication Terms",
                    "description": "Pharmaceutical terminology in Arabic",
                    "terms": {
                        "antibiotic": {"arabic": "مضاد حيوي", "transliteration": "mudad hayawi"},
                        "painkiller": {"arabic": "مسكن", "transliteration": "musakkn"},
                        "vitamin": {"arabic": "فيتامين", "transliteration": "vitamin"},
                        "injection": {"arabic": "حقنة", "transliteration": "huqna"},
                        "tablet": {"arabic": "قرص", "transliteration": "qurs"}
                    }
                }
            }
            
            return json.dumps(terminology.get(category, {"error": "Category not found"}), 
                            indent=2, ensure_ascii=False)

        @self.server.resource("arabic-medical://cultural-guidelines/{context}")
        async def get_cultural_guidelines(uri: str) -> str:
            """Provide cultural guidelines for Saudi healthcare"""
            context = uri.split("/")[-1]
            
            guidelines = {
                "patient-interaction": {
                    "title": "Patient Interaction Guidelines",
                    "guidelines": [
                        "Use formal Arabic (فصحى) for medical documents",
                        "Address patients with appropriate titles (أستاذ/أستاذة)",
                        "Consider family involvement in medical decisions",
                        "Respect prayer times in scheduling",
                        "Provide same-gender healthcare options when possible"
                    ]
                },
                "ramadan": {
                    "title": "Ramadan Healthcare Considerations",
                    "guidelines": [
                        "Adjust medication schedules for fasting",
                        "Consider Iftar and Suhur timing for medications",
                        "Provide special guidance for diabetic patients",
                        "Schedule non-urgent procedures outside fasting hours",
                        "Offer health education about safe fasting"
                    ]
                }
            }
            
            return json.dumps(guidelines.get(context, {"error": "Context not found"}), 
                            indent=2, ensure_ascii=False)

    async def run(self):
        """Run the Arabic Medical MCP server"""
        if not MCP_AVAILABLE:
            logger.error("MCP not available - cannot start server")
            return
            
        logger.info("Starting BrainSAIT Arabic Medical MCP Server...")
        
        try:
            from mcp.server.stdio import stdio_server
            
            async with stdio_server() as (read_stream, write_stream):
                logger.info("Arabic Medical MCP Server connected and ready")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="brainsait-arabic-medical-mcp-server",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={
                                "arabic_support": True,
                                "rtl_layouts": True,
                                "cultural_adaptation": True,
                                "islamic_calendar": True,
                                "medical_translation": True
                            },
                        ),
                    ),
                )
        except Exception as e:
            logger.error(f"Error running Arabic Medical MCP server: {str(e)}")
            raise

def main():
    """Entry point for the Arabic Medical MCP server"""
    if not MCP_AVAILABLE:
        print("MCP packages not installed. Please install with:")
        print("pip install mcp")
        return
    
    server = BrainSAITArabicMedicalMCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Arabic Medical MCP Server shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in Arabic Medical MCP Server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
