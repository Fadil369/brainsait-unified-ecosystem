#!/usr/bin/env python3
"""
BrainSAIT PyBrain Integration Module
Unified AI and Intelligence Hub for the BrainSAIT Healthcare Ecosystem

This module provides the brainsait-pybrain functionality by integrating:
- Advanced Arabic healthcare NLP
- Intelligent decision support systems
- Predictive analytics for healthcare
- Cultural context-aware AI processing
- Real-time AI insights and recommendations
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import pickle
import base64

# AI/ML imports
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    import torch.nn.functional as F
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support
    from sklearn.model_selection import train_test_split
    AI_LIBRARIES_AVAILABLE = True
except ImportError:
    AI_LIBRARIES_AVAILABLE = False

# Arabic processing
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    import pyarabic.araby as araby
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# Healthcare standards
try:
    import hl7
    HEALTHCARE_STANDARDS = True
except ImportError:
    HEALTHCARE_STANDARDS = False

# Import existing services
from ..services.unified_pybrain_service import (
    UnifiedPyBrainService, AITaskType, AIConfidenceLevel, 
    AIInsight, CulturalContext
)
from ..services.ai_arabic_service import AIArabicService

logger = logging.getLogger(__name__)

class BrainSAITIntelligenceLevel(str, Enum):
    """Intelligence processing levels for BrainSAIT AI"""
    BASIC = "basic"           # Simple rule-based processing
    ADVANCED = "advanced"     # ML-based analysis
    EXPERT = "expert"         # Deep learning with cultural context
    GENIUS = "genius"         # Multi-modal AI with reasoning

class HealthcareAIDomain(str, Enum):
    """Healthcare AI processing domains"""
    CLINICAL_DECISION = "clinical_decision"
    RADIOLOGY = "radiology"
    PATHOLOGY = "pathology"
    PHARMACY = "pharmacy"
    NURSING = "nursing"
    ADMINISTRATION = "administration"
    RESEARCH = "research"
    PREVENTION = "prevention"
    EMERGENCY = "emergency"
    MENTAL_HEALTH = "mental_health"

@dataclass
class BrainSAITAIModel:
    """BrainSAIT AI Model Configuration"""
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: HealthcareAIDomain = HealthcareAIDomain.CLINICAL_DECISION
    intelligence_level: BrainSAITIntelligenceLevel = BrainSAITIntelligenceLevel.ADVANCED
    language_support: List[str] = field(default_factory=lambda: ["ar", "en"])
    cultural_context: bool = True
    accuracy_score: float = 0.0
    training_date: Optional[datetime] = None
    model_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthcareAIInsight:
    """Enhanced healthcare AI insight with domain-specific information"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: HealthcareAIDomain = HealthcareAIDomain.CLINICAL_DECISION
    intelligence_level: BrainSAITIntelligenceLevel = BrainSAITIntelligenceLevel.ADVANCED
    content: str = ""
    content_ar: str = ""
    confidence_score: float = 0.75
    clinical_significance: str = "medium"  # low, medium, high, critical
    evidence_level: str = "moderate"  # low, moderate, high, expert_consensus
    recommendations: List[str] = field(default_factory=list)
    recommendations_ar: List[str] = field(default_factory=list)
    cultural_adaptations: Dict[str, Any] = field(default_factory=dict)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    compliance_flags: List[str] = field(default_factory=list)
    follow_up_required: bool = False
    urgency_level: str = "routine"  # routine, urgent, emergency
    created_at: datetime = field(default_factory=datetime.now)

class AdvancedArabicHealthcareNLP:
    """Advanced Arabic healthcare NLP with cultural intelligence"""
    
    def __init__(self):
        self.models = {}
        self.cultural_rules = self._load_cultural_intelligence_rules()
        self.medical_ontology = self._load_arabic_medical_ontology()
        self.dialect_recognizer = None
        
        if AI_LIBRARIES_AVAILABLE:
            asyncio.create_task(self._initialize_advanced_models())
    
    def _load_cultural_intelligence_rules(self) -> Dict[str, Any]:
        """Load Saudi cultural intelligence rules for healthcare AI"""
        return {
            "communication_styles": {
                "formal": {
                    "indicators": ["حضرتك", "سعادتك", "الدكتور المحترم"],
                    "response_style": "formal_medical",
                    "cultural_weight": 0.9
                },
                "family_oriented": {
                    "indicators": ["العائلة", "الأهل", "أمي تقول", "أبي يقول"],
                    "response_style": "family_inclusive",
                    "cultural_weight": 0.85
                },
                "religious": {
                    "indicators": ["الحمدلله", "إن شاء الله", "بإذن الله", "ادعيلي"],
                    "response_style": "religiously_sensitive",
                    "cultural_weight": 0.8
                }
            },
            "gender_sensitivity": {
                "female_patient_markers": ["أفضل دكتورة", "نساء", "نسائي"],
                "male_patient_markers": ["دكتور رجال", "ذكر", "رجالي"],
                "family_decision_involvement": True
            },
            "age_respect_patterns": {
                "elderly": ["كبير السن", "العم", "الخال", "الوالد", "الوالدة"],
                "youth": ["شاب", "شابة", "صغير", "صغيرة"]
            },
            "regional_dialects": {
                "najdi": ["واجد", "ذا", "شلون", "متى ما"],
                "hijazi": ["كدا", "ازاي", "لسه", "خالص"],
                "eastern": ["شنو", "وين", "جي", "ما صار"],
                "southern": ["ايش", "فين", "كيف", "ما جا"]
            }
        }
    
    def _load_arabic_medical_ontology(self) -> Dict[str, Any]:
        """Load comprehensive Arabic medical ontology"""
        return {
            "symptoms": {
                "pain": {
                    "ar_terms": ["ألم", "وجع", "يوجعني", "يؤلمني", "مؤلم"],
                    "severity_modifiers": ["شديد", "خفيف", "متوسط", "قوي", "مو طبيعي"],
                    "icd10_mappings": ["R52", "R51"]
                },
                "fever": {
                    "ar_terms": ["حمى", "سخونة", "حرارة", "سخان", "محموم"],
                    "icd10_mappings": ["R50"]
                },
                "breathing": {
                    "ar_terms": ["ضيق تنفس", "صعوبة تنفس", "ما اقدر اتنفس", "نهجان"],
                    "icd10_mappings": ["R06.0", "R06.2"]
                }
            },
            "body_parts": {
                "head": {"ar_terms": ["رأس", "راس", "دماغ"], "snomed": "69536005"},
                "chest": {"ar_terms": ["صدر", "قلب منطقة"], "snomed": "51185008"},
                "abdomen": {"ar_terms": ["بطن", "معدة", "كرش"], "snomed": "818983003"}
            },
            "medications": {
                "analgesics": {
                    "ar_terms": ["مسكن", "مسكن ألم", "دوا وجع"],
                    "common_drugs": ["باراسيتامول", "إيبوبروفين", "ديكلوفيناك"]
                }
            },
            "procedures": {
                "examination": {
                    "ar_terms": ["فحص", "كشف", "معاينة"],
                    "types": ["physical", "laboratory", "imaging"]
                }
            }
        }
    
    async def _initialize_advanced_models(self):
        """Initialize advanced Arabic healthcare models"""
        try:
            # Initialize Arabic healthcare sentiment model
            self.models["sentiment"] = pipeline(
                "sentiment-analysis",
                model="CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment"
            )
            
            # Initialize Arabic NER for medical entities
            self.models["ner"] = pipeline(
                "ner",
                model="CAMeL-Lab/bert-base-arabic-camelbert-msa-ner",
                aggregation_strategy="simple"
            )
            
            logger.info("Advanced Arabic healthcare models initialized")
        except Exception as e:
            logger.error(f"Failed to initialize advanced models: {e}")
    
    async def analyze_healthcare_text(self, 
                                    text: str,
                                    patient_context: Dict[str, Any]) -> HealthcareAIInsight:
        """Comprehensive Arabic healthcare text analysis"""
        
        # Extract medical entities
        medical_entities = await self._extract_medical_entities(text)
        
        # Analyze cultural context
        cultural_analysis = await self._analyze_cultural_intelligence(text, patient_context)
        
        # Assess clinical significance
        clinical_assessment = await self._assess_clinical_significance(
            text, medical_entities, patient_context
        )
        
        # Generate Arabic translation if needed
        arabic_content = await self._generate_arabic_response(
            clinical_assessment["summary"], cultural_analysis
        )
        
        # Create comprehensive insight
        insight = HealthcareAIInsight(
            domain=HealthcareAIDomain.CLINICAL_DECISION,
            intelligence_level=BrainSAITIntelligenceLevel.EXPERT,
            content=clinical_assessment["summary"],
            content_ar=arabic_content,
            confidence_score=clinical_assessment["confidence"],
            clinical_significance=clinical_assessment["significance"],
            evidence_level=clinical_assessment["evidence_level"],
            recommendations=clinical_assessment["recommendations"],
            recommendations_ar=clinical_assessment["recommendations_ar"],
            cultural_adaptations=cultural_analysis,
            supporting_data={
                "medical_entities": medical_entities,
                "patient_context": patient_context,
                "processed_text_length": len(text)
            },
            follow_up_required=clinical_assessment["follow_up_required"],
            urgency_level=clinical_assessment["urgency_level"]
        )
        
        return insight
    
    async def _extract_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical entities from Arabic text"""
        entities = []
        
        # Use ontology-based extraction
        for category, terms_data in self.medical_ontology.items():
            if isinstance(terms_data, dict):
                for entity_type, entity_data in terms_data.items():
                    ar_terms = entity_data.get("ar_terms", [])
                    for term in ar_terms:
                        if term in text:
                            entities.append({
                                "text": term,
                                "label": entity_type,
                                "category": category,
                                "confidence": 0.9,
                                "start": text.find(term),
                                "end": text.find(term) + len(term),
                                "snomed_code": entity_data.get("snomed"),
                                "icd10_codes": entity_data.get("icd10_mappings", [])
                            })
        
        # Use NER model if available
        if AI_LIBRARIES_AVAILABLE and "ner" in self.models:
            try:
                ner_results = self.models["ner"](text)
                for result in ner_results:
                    entities.append({
                        "text": result["word"],
                        "label": result["entity_group"],
                        "category": "ner_detected",
                        "confidence": result["score"],
                        "start": result["start"],
                        "end": result["end"]
                    })
            except Exception as e:
                logger.warning(f"NER processing failed: {e}")
        
        return entities
    
    async def _analyze_cultural_intelligence(self, 
                                           text: str,
                                           patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cultural intelligence patterns in text"""
        analysis = {
            "communication_style": "neutral",
            "cultural_markers": [],
            "sensitivity_flags": [],
            "response_adaptations": [],
            "confidence": 0.7
        }
        
        # Analyze communication style
        for style, style_data in self.cultural_rules["communication_styles"].items():
            indicators = style_data["indicators"]
            matches = [indicator for indicator in indicators if indicator in text]
            
            if matches:
                analysis["communication_style"] = style
                analysis["cultural_markers"].extend(matches)
                analysis["response_adaptations"].append(style_data["response_style"])
                analysis["confidence"] = max(analysis["confidence"], style_data["cultural_weight"])
        
        # Gender sensitivity analysis
        gender_markers = self.cultural_rules["gender_sensitivity"]
        patient_gender = patient_context.get("gender", "").lower()
        
        if patient_gender in ["female", "أنثى"]:
            if any(marker in text for marker in gender_markers["female_patient_markers"]):
                analysis["sensitivity_flags"].append("female_provider_preference")
        
        # Age respect analysis
        age_patterns = self.cultural_rules["age_respect_patterns"]
        patient_age = patient_context.get("age", 0)
        
        if patient_age >= 60:
            elderly_terms = [term for term in age_patterns["elderly"] if term in text]
            if elderly_terms:
                analysis["sensitivity_flags"].append("elderly_respect_required")
                analysis["response_adaptations"].append("use_formal_address")
        
        # Regional dialect detection
        for dialect, markers in self.cultural_rules["regional_dialects"].items():
            dialect_matches = [marker for marker in markers if marker in text]
            if dialect_matches:
                analysis["cultural_markers"].append(f"dialect_{dialect}")
                analysis["response_adaptations"].append(f"adapt_to_{dialect}_dialect")
        
        return analysis
    
    async def _assess_clinical_significance(self,
                                          text: str,
                                          entities: List[Dict[str, Any]],
                                          patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess clinical significance of the text and entities"""
        assessment = {
            "summary": "",
            "significance": "medium",
            "evidence_level": "moderate",
            "confidence": 0.7,
            "recommendations": [],
            "recommendations_ar": [],
            "follow_up_required": False,
            "urgency_level": "routine"
        }
        
        # Analyze severity indicators
        high_severity_terms = ["شديد", "قوي", "كثير", "واجد", "مستحيل", "ما اقدر"]
        severity_score = sum(1 for term in high_severity_terms if term in text)
        
        # Analyze emergency indicators
        emergency_terms = ["طوارئ", "إسعاف", "حالة حرجة", "خطير", "ما اقدر اتنفس"]
        emergency_score = sum(1 for term in emergency_terms if term in text)
        
        # Assess based on entities found
        critical_entities = [e for e in entities if e["category"] in ["symptoms", "emergency"]]
        
        # Determine significance
        if emergency_score > 0 or len(critical_entities) > 2:
            assessment["significance"] = "critical"
            assessment["urgency_level"] = "emergency"
            assessment["follow_up_required"] = True
            assessment["confidence"] = 0.9
        elif severity_score > 1 or len(critical_entities) > 0:
            assessment["significance"] = "high"
            assessment["urgency_level"] = "urgent"
            assessment["follow_up_required"] = True
            assessment["confidence"] = 0.8
        
        # Generate summary
        entity_summary = ", ".join([e["text"] for e in entities[:5]])
        assessment["summary"] = f"Healthcare text analysis completed. Found {len(entities)} medical entities: {entity_summary}"
        
        # Generate recommendations
        if assessment["significance"] == "critical":
            assessment["recommendations"] = [
                "Immediate medical evaluation required",
                "Contact emergency services if needed",
                "Monitor vital signs closely"
            ]
            assessment["recommendations_ar"] = [
                "يتطلب تقييم طبي فوري",
                "اتصل بخدمات الطوارئ إذا لزم الأمر",
                "راقب العلامات الحيوية عن كثب"
            ]
        elif assessment["significance"] == "high":
            assessment["recommendations"] = [
                "Schedule urgent medical consultation",
                "Document symptoms and timeline",
                "Follow up within 24 hours"
            ]
            assessment["recommendations_ar"] = [
                "حدد موعد استشارة طبية عاجلة",
                "وثق الأعراض والجدول الزمني",
                "تابع خلال 24 ساعة"
            ]
        else:
            assessment["recommendations"] = [
                "Regular monitoring recommended",
                "Schedule routine follow-up",
                "Maintain current treatment plan"
            ]
            assessment["recommendations_ar"] = [
                "يُنصح بالمراقبة المنتظمة",
                "حدد موعد متابعة روتيني",
                "حافظ على خطة العلاج الحالية"
            ]
        
        return assessment
    
    async def _generate_arabic_response(self,
                                      english_content: str,
                                      cultural_context: Dict[str, Any]) -> str:
        """Generate culturally appropriate Arabic response"""
        
        # Basic translation mappings
        translations = {
            "Healthcare text analysis completed": "تم تحليل النص الطبي بنجاح",
            "Found": "تم العثور على",
            "medical entities": "كيانات طبية",
            "immediate": "فوري",
            "urgent": "عاجل",
            "routine": "روتيني",
            "consultation": "استشارة",
            "follow up": "متابعة"
        }
        
        arabic_content = english_content
        for en_term, ar_term in translations.items():
            arabic_content = arabic_content.replace(en_term, ar_term)
        
        # Apply cultural adaptations
        communication_style = cultural_context.get("communication_style", "neutral")
        
        if communication_style == "formal":
            arabic_content = "حضرتك، " + arabic_content
        elif communication_style == "family_oriented":
            arabic_content += " ويُرجى إشراك العائلة في القرارات الطبية"
        elif communication_style == "religious":
            arabic_content = "بإذن الله، " + arabic_content + " والله الشافي"
        
        # Format for RTL display
        if ARABIC_SUPPORT:
            try:
                reshaped = arabic_reshaper.reshape(arabic_content)
                arabic_content = get_display(reshaped)
            except Exception as e:
                logger.warning(f"Arabic reshaping failed: {e}")
        
        return arabic_content

class HealthcarePredictiveAnalytics:
    """Advanced predictive analytics for healthcare"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.trained_models = {}
        
    async def train_healthcare_model(self,
                                   model_type: str,
                                   training_data: pd.DataFrame,
                                   target_column: str) -> BrainSAITAIModel:
        """Train a healthcare prediction model"""
        
        if not AI_LIBRARIES_AVAILABLE:
            raise ValueError("AI libraries not available for model training")
        
        model_id = str(uuid.uuid4())
        
        # Prepare data
        X = training_data.drop(columns=[target_column])
        y = training_data[target_column]
        
        # Handle categorical variables
        for col in X.select_dtypes(include=['object']).columns:
            encoder = LabelEncoder()
            X[col] = encoder.fit_transform(X[col].astype(str))
            self.encoders[f"{model_id}_{col}"] = encoder
        
        # Scale numerical features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers[model_id] = scaler
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model based on type
        if model_type == "random_forest":
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(random_state=42)
        elif model_type == "neural_network":
            model = MLPClassifier(hidden_layer_sizes=(100, 50), random_state=42)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # Train the model
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        # Store model
        self.trained_models[model_id] = model
        
        # Serialize model for storage
        model_data = pickle.dumps(model)
        
        # Create BrainSAIT AI Model
        brainsait_model = BrainSAITAIModel(
            model_id=model_id,
            name=f"Healthcare {model_type.replace('_', ' ').title()} Model",
            domain=HealthcareAIDomain.CLINICAL_DECISION,
            intelligence_level=BrainSAITIntelligenceLevel.ADVANCED,
            accuracy_score=accuracy,
            training_date=datetime.now(),
            model_data=model_data,
            metadata={
                "model_type": model_type,
                "features": list(X.columns),
                "target": target_column,
                "training_samples": len(training_data),
                "test_accuracy": accuracy
            }
        )
        
        return brainsait_model
    
    async def predict_healthcare_outcome(self,
                                       model_id: str,
                                       input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make healthcare predictions using trained model"""
        
        if model_id not in self.trained_models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.trained_models[model_id]
        scaler = self.scalers[model_id]
        
        # Prepare input data
        input_df = pd.DataFrame([input_data])
        
        # Apply same encoding as training
        for col in input_df.select_dtypes(include=['object']).columns:
            encoder_key = f"{model_id}_{col}"
            if encoder_key in self.encoders:
                try:
                    input_df[col] = self.encoders[encoder_key].transform(input_df[col].astype(str))
                except ValueError:
                    # Handle unseen categories
                    input_df[col] = 0
        
        # Scale features
        input_scaled = scaler.transform(input_df)
        
        # Make prediction
        prediction = model.predict(input_scaled)[0]
        prediction_proba = model.predict_proba(input_scaled)[0]
        
        return {
            "prediction": prediction,
            "confidence": float(max(prediction_proba)),
            "probability_distribution": prediction_proba.tolist(),
            "model_id": model_id,
            "prediction_time": datetime.now().isoformat()
        }

class BrainSAITPyBrain:
    """
    Main BrainSAIT PyBrain Integration Class
    Provides unified AI and intelligence capabilities for the healthcare ecosystem
    """
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 enable_advanced_models: bool = True,
                 cache_size: int = 10000):
        
        # Initialize core components
        self.unified_service = UnifiedPyBrainService(
            openai_api_key=openai_api_key,
            cache_size=cache_size,
            enable_edge_ai=enable_advanced_models
        )
        
        self.arabic_nlp = AdvancedArabicHealthcareNLP()
        self.predictive_analytics = HealthcarePredictiveAnalytics()
        
        # Model registry
        self.model_registry = {}
        self.performance_metrics = {
            "total_insights_generated": 0,
            "average_confidence_score": 0.0,
            "arabic_text_processed": 0,
            "predictions_made": 0,
            "models_trained": 0
        }
        
        logger.info("BrainSAIT PyBrain initialized successfully")
    
    async def initialize_healthcare_ai(self,
                                     ai_arabic_service: Optional[AIArabicService] = None,
                                     additional_config: Optional[Dict[str, Any]] = None):
        """Initialize healthcare AI components"""
        
        # Initialize unified service integrations
        await self.unified_service.initialize_integrations(
            ai_arabic_service=ai_arabic_service
        )
        
        logger.info("BrainSAIT PyBrain healthcare AI initialized")
    
    async def generate_healthcare_insight(self,
                                        text: str,
                                        domain: HealthcareAIDomain,
                                        patient_context: Optional[Dict[str, Any]] = None,
                                        intelligence_level: BrainSAITIntelligenceLevel = BrainSAITIntelligenceLevel.ADVANCED) -> HealthcareAIInsight:
        """Generate comprehensive healthcare AI insight"""
        
        patient_context = patient_context or {}
        
        # Use advanced Arabic NLP for text analysis
        if intelligence_level in [BrainSAITIntelligenceLevel.EXPERT, BrainSAITIntelligenceLevel.GENIUS]:
            insight = await self.arabic_nlp.analyze_healthcare_text(text, patient_context)
            insight.domain = domain
            insight.intelligence_level = intelligence_level
        else:
            # Use basic unified service
            task_type = self._map_domain_to_task_type(domain)
            basic_insight = await self.unified_service.generate_ai_insight(
                task_type,
                {"text": text, "patient_context": patient_context},
                patient_context
            )
            
            # Convert to HealthcareAIInsight
            insight = HealthcareAIInsight(
                domain=domain,
                intelligence_level=intelligence_level,
                content=basic_insight.content,
                confidence_score=basic_insight.confidence_score,
                supporting_data=basic_insight.supporting_data,
                recommendations=basic_insight.recommendations
            )
        
        # Update metrics
        self.performance_metrics["total_insights_generated"] += 1
        self.performance_metrics["arabic_text_processed"] += len(text)
        
        return insight
    
    async def train_custom_healthcare_model(self,
                                          model_name: str,
                                          training_data: pd.DataFrame,
                                          target_column: str,
                                          model_type: str = "random_forest",
                                          domain: HealthcareAIDomain = HealthcareAIDomain.CLINICAL_DECISION) -> str:
        """Train a custom healthcare AI model"""
        
        # Train the model
        model = await self.predictive_analytics.train_healthcare_model(
            model_type, training_data, target_column
        )
        
        # Update model metadata
        model.name = model_name
        model.domain = domain
        
        # Register model
        self.model_registry[model.model_id] = model
        
        # Update metrics
        self.performance_metrics["models_trained"] += 1
        
        logger.info(f"Custom healthcare model '{model_name}' trained with ID: {model.model_id}")
        
        return model.model_id
    
    async def predict_healthcare_outcome(self,
                                       model_id: str,
                                       input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make healthcare predictions using trained models"""
        
        # Make prediction
        prediction_result = await self.predictive_analytics.predict_healthcare_outcome(
            model_id, input_data
        )
        
        # Update metrics
        self.performance_metrics["predictions_made"] += 1
        
        return prediction_result
    
    async def analyze_arabic_medical_text(self,
                                        text: str,
                                        patient_context: Optional[Dict[str, Any]] = None) -> HealthcareAIInsight:
        """Specialized Arabic medical text analysis"""
        
        patient_context = patient_context or {}
        
        # Use advanced Arabic NLP
        insight = await self.arabic_nlp.analyze_healthcare_text(text, patient_context)
        
        return insight
    
    async def generate_cultural_healthcare_recommendations(self,
                                                         patient_profile: Dict[str, Any],
                                                         clinical_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate culturally appropriate healthcare recommendations"""
        
        recommendations = {
            "clinical_recommendations": [],
            "cultural_adaptations": [],
            "communication_style": "neutral",
            "family_involvement": False,
            "religious_considerations": [],
            "gender_specific_needs": [],
            "language_preferences": []
        }
        
        # Analyze patient cultural profile
        age = patient_profile.get("age", 0)
        gender = patient_profile.get("gender", "").lower()
        cultural_background = patient_profile.get("cultural_background", "saudi")
        language_preference = patient_profile.get("language_preference", "ar")
        
        # Age-based adaptations
        if age >= 60:
            recommendations["cultural_adaptations"].append("elderly_respect_protocol")
            recommendations["communication_style"] = "formal"
            recommendations["clinical_recommendations"].append("Consider age-appropriate treatment modifications")
        
        # Gender-specific considerations
        if gender in ["female", "أنثى"]:
            recommendations["gender_specific_needs"].append("female_provider_preference_option")
            recommendations["cultural_adaptations"].append("gender_sensitive_care")
        
        # Religious considerations
        if cultural_background == "saudi":
            recommendations["religious_considerations"] = [
                "prayer_time_accommodation",
                "halal_medication_verification",
                "fasting_considerations"
            ]
            recommendations["family_involvement"] = True
        
        # Language preferences
        if language_preference == "ar":
            recommendations["language_preferences"] = [
                "arabic_documentation",
                "arabic_speaking_staff",
                "cultural_medical_terminology"
            ]
        
        return recommendations
    
    async def get_realtime_ai_insights(self) -> Dict[str, Any]:
        """Get real-time AI system insights and metrics"""
        
        # Get unified service metrics
        unified_metrics = await self.unified_service.get_performance_metrics()
        
        # Combine with PyBrain specific metrics
        combined_metrics = {
            "brainsait_pybrain_metrics": self.performance_metrics,
            "unified_service_metrics": unified_metrics,
            "model_registry_status": {
                "total_models": len(self.model_registry),
                "model_types": list(set(model.domain.value for model in self.model_registry.values())),
                "average_model_accuracy": np.mean([model.accuracy_score for model in self.model_registry.values()]) if self.model_registry else 0.0
            },
            "system_health": {
                "ai_libraries_available": AI_LIBRARIES_AVAILABLE,
                "arabic_support": ARABIC_SUPPORT,
                "healthcare_standards": HEALTHCARE_STANDARDS,
                "status": "healthy" if AI_LIBRARIES_AVAILABLE else "limited"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return combined_metrics
    
    def _map_domain_to_task_type(self, domain: HealthcareAIDomain) -> AITaskType:
        """Map healthcare domain to AI task type"""
        mapping = {
            HealthcareAIDomain.CLINICAL_DECISION: AITaskType.CLINICAL_DECISION_SUPPORT,
            HealthcareAIDomain.RADIOLOGY: AITaskType.MEDICAL_ANALYSIS,
            HealthcareAIDomain.PATHOLOGY: AITaskType.MEDICAL_ANALYSIS,
            HealthcareAIDomain.PHARMACY: AITaskType.RISK_ASSESSMENT,
            HealthcareAIDomain.NURSING: AITaskType.PATIENT_INSIGHTS,
            HealthcareAIDomain.ADMINISTRATION: AITaskType.WORKFLOW_OPTIMIZATION,
            HealthcareAIDomain.RESEARCH: AITaskType.PREDICTIVE_ANALYTICS,
            HealthcareAIDomain.PREVENTION: AITaskType.RISK_ASSESSMENT,
            HealthcareAIDomain.EMERGENCY: AITaskType.ANOMALY_DETECTION,
            HealthcareAIDomain.MENTAL_HEALTH: AITaskType.PATIENT_INSIGHTS
        }
        
        return mapping.get(domain, AITaskType.MEDICAL_ANALYSIS)
    
    async def batch_process_healthcare_insights(self,
                                              texts: List[str],
                                              domain: HealthcareAIDomain,
                                              patient_contexts: Optional[List[Dict[str, Any]]] = None) -> List[HealthcareAIInsight]:
        """Process multiple healthcare texts in batch"""
        
        if patient_contexts is None:
            patient_contexts = [{}] * len(texts)
        
        tasks = []
        for i, text in enumerate(texts):
            task = self.generate_healthcare_insight(
                text, domain, patient_contexts[i]
            )
            tasks.append(task)
        
        # Process concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, HealthcareAIInsight)]
        
        return valid_results

# Export main class
__all__ = [
    "BrainSAITPyBrain",
    "HealthcareAIInsight", 
    "BrainSAITIntelligenceLevel",
    "HealthcareAIDomain",
    "BrainSAITAIModel"
]
