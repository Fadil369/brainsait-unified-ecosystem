# AI & Arabic Language Processing Service
# Implements Arabic-first NLP and medical AI capabilities
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pydantic import BaseModel
import logging
import asyncio
import json
import re
from dataclasses import dataclass

# Arabic processing imports
import arabic_reshaper
from bidi.algorithm import get_display
import pyarabic.araby as araby

# AI/ML imports
import openai
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ArabicMedicalEntity:
    text: str
    entity_type: str  # symptom, diagnosis, medication, procedure
    confidence: float
    snomed_code: Optional[str] = None
    icd10_code: Optional[str] = None
    position_start: int = 0
    position_end: int = 0

@dataclass
class ClaimsAnalysisResult:
    claim_id: str
    risk_score: float
    fraud_probability: float
    duplicate_likelihood: float
    recommended_action: str
    analysis_details: Dict[str, Any]
    confidence_level: float

@dataclass
class DuplicateDetectionResult:
    original_claim_id: str
    duplicate_candidates: List[Dict[str, Any]]
    similarity_scores: List[float]
    estimated_savings: float
    detection_confidence: float

class AIArabicService:
    """
    AI & Arabic Language Processing Service
    Provides Arabic-first medical NLP and intelligent claims analysis
    Target: 70% reduction in medical errors, duplicate detection, Arabic medical transcription
    """
    
    def __init__(self, openai_api_key: str, models_path: str = "./models"):
        self.openai_api_key = openai_api_key
        self.models_path = models_path
        
        # Initialize OpenAI
        openai.api_key = openai_api_key
        
        # Arabic medical terminology mappings
        self.arabic_to_snomed = self._load_arabic_snomed_mappings()
        self.arabic_to_icd10 = self._load_arabic_icd10_mappings()
        
        # Load pre-trained models
        self.arabic_nlp_model = None
        self.medical_classifier = None
        self.fraud_detector = None
        
        # Initialize models asynchronously
        asyncio.create_task(self._initialize_models())
    
    async def _initialize_models(self):
        """Initialize AI models asynchronously"""
        try:
            # Arabic medical NLP model
            self.arabic_tokenizer = AutoTokenizer.from_pretrained(
                "CAMeL-Lab/bert-base-arabic-camelbert-msa"
            )
            self.arabic_model = AutoModel.from_pretrained(
                "CAMeL-Lab/bert-base-arabic-camelbert-msa"
            )
            
            # Medical classification pipeline
            self.medical_classifier = pipeline(
                "text-classification",
                model="emilyalsentzer/Bio_ClinicalBERT",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Named Entity Recognition for medical terms
            self.ner_pipeline = pipeline(
                "ner",
                model="CAMeL-Lab/bert-base-arabic-camelbert-msa-ner",
                aggregation_strategy="simple"
            )
            
            logger.info("AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI models: {e}")
    
    async def process_arabic_medical_text(self, text: str) -> Dict[str, Any]:
        """Process Arabic medical text and extract structured information"""
        
        if not text.strip():
            return {"error": "Empty text provided"}
        
        # Preprocess Arabic text
        processed_text = self._preprocess_arabic_text(text)
        
        # Extract medical entities
        entities = await self._extract_arabic_medical_entities(processed_text)
        
        # Classify medical content
        classification = await self._classify_medical_content(processed_text)
        
        # Map to international standards
        snomed_mappings = await self._map_to_snomed_codes(entities)
        icd10_mappings = await self._map_to_icd10_codes(entities)
        
        # Generate structured FHIR-compatible output
        fhir_bundle = await self._create_fhir_bundle(entities, classification, text)
        
        return {
            "original_text": text,
            "processed_text": processed_text,
            "entities": [entity.__dict__ for entity in entities],
            "classification": classification,
            "snomed_mappings": snomed_mappings,
            "icd10_mappings": icd10_mappings,
            "fhir_bundle": fhir_bundle,
            "confidence_score": self._calculate_overall_confidence(entities, classification),
            "processing_timestamp": datetime.now().isoformat()
        }
    
    async def transcribe_arabic_medical_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe Arabic medical audio using Whisper"""
        
        try:
            # Use OpenAI Whisper for Arabic transcription
            with open(audio_file_path, "rb") as audio_file:
                transcript = await openai.Audio.atranscribe(
                    model="whisper-1",
                    file=audio_file,
                    language="ar",
                    response_format="verbose_json"
                )
            
            # Process the transcribed text
            processed_result = await self.process_arabic_medical_text(transcript["text"])
            
            return {
                "transcription": transcript,
                "medical_analysis": processed_result,
                "quality_score": transcript.get("confidence", 0.9)
            }
            
        except Exception as e:
            logger.error(f"Arabic audio transcription failed: {e}")
            return {"error": str(e)}
    
    async def analyze_claims_for_fraud(self, claims_data: List[Dict[str, Any]]) -> List[ClaimsAnalysisResult]:
        """Analyze claims for potential fraud using AI"""
        
        results = []
        
        for claim in claims_data:
            try:
                # Extract features for fraud detection
                features = await self._extract_claim_features(claim)
                
                # Calculate risk scores
                risk_score = await self._calculate_risk_score(features)
                fraud_probability = await self._predict_fraud_probability(features)
                
                # Analyze patterns
                pattern_analysis = await self._analyze_claim_patterns(claim)
                
                # Generate recommendations
                recommended_action = self._generate_claim_recommendation(
                    risk_score, fraud_probability, pattern_analysis
                )
                
                result = ClaimsAnalysisResult(
                    claim_id=claim["claim_id"],
                    risk_score=risk_score,
                    fraud_probability=fraud_probability,
                    duplicate_likelihood=pattern_analysis.get("duplicate_likelihood", 0.0),
                    recommended_action=recommended_action,
                    analysis_details={
                        "pattern_analysis": pattern_analysis,
                        "feature_importance": features,
                        "risk_factors": await self._identify_risk_factors(claim)
                    },
                    confidence_level=self._calculate_analysis_confidence(features)
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Claim analysis failed for {claim.get('claim_id', 'unknown')}: {e}")
                continue
        
        return results
    
    async def detect_duplicate_procedures(self, patient_id: str, 
                                        new_procedures: List[Dict[str, Any]], 
                                        lookback_days: int = 30) -> DuplicateDetectionResult:
        """Detect potential duplicate medical procedures"""
        
        # Get patient's recent procedures
        recent_procedures = await self._get_recent_procedures(patient_id, lookback_days)
        
        duplicate_candidates = []
        similarity_scores = []
        total_estimated_savings = 0.0
        
        for new_proc in new_procedures:
            for recent_proc in recent_procedures:
                similarity = await self._calculate_procedure_similarity(new_proc, recent_proc)
                
                if similarity > 0.8:  # High similarity threshold
                    duplicate_candidates.append({
                        "original_procedure": recent_proc,
                        "new_procedure": new_proc,
                        "similarity_score": similarity,
                        "time_difference": (datetime.now() - recent_proc["date"]).days,
                        "estimated_cost": new_proc.get("cost", 0)
                    })
                    similarity_scores.append(similarity)
                    total_estimated_savings += new_proc.get("cost", 0)
        
        return DuplicateDetectionResult(
            original_claim_id=new_procedures[0].get("claim_id", ""),
            duplicate_candidates=duplicate_candidates,
            similarity_scores=similarity_scores,
            estimated_savings=total_estimated_savings,
            detection_confidence=np.mean(similarity_scores) if similarity_scores else 0.0
        )
    
    async def generate_arabic_medical_report(self, patient_data: Dict[str, Any], 
                                           template_type: str = "comprehensive") -> str:
        """Generate Arabic medical report using AI"""
        
        try:
            # Create prompt for report generation
            prompt = self._create_report_prompt(patient_data, template_type)
            
            # Generate report using OpenAI
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """أنت طبيب متخصص في إعداد التقارير الطبية باللغة العربية. 
                        اكتب تقريراً طبياً شاملاً ودقيقاً بناءً على البيانات المقدمة.
                        استخدم المصطلحات الطبية العربية الصحيحة والمتوافقة مع المعايير السعودية."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            arabic_report = response.choices[0].message.content
            
            # Format Arabic text properly
            formatted_report = self._format_arabic_medical_text(arabic_report)
            
            return formatted_report
            
        except Exception as e:
            logger.error(f"Arabic report generation failed: {e}")
            return "فشل في إنشاء التقرير الطبي"
    
    async def predict_treatment_outcomes(self, patient_profile: Dict[str, Any], 
                                       proposed_treatment: Dict[str, Any]) -> Dict[str, Any]:
        """Predict treatment outcomes using AI analysis"""
        
        # Extract patient features
        patient_features = await self._extract_patient_features(patient_profile)
        
        # Analyze treatment compatibility
        compatibility_score = await self._analyze_treatment_compatibility(
            patient_features, proposed_treatment
        )
        
        # Predict success probability
        success_probability = await self._predict_treatment_success(
            patient_features, proposed_treatment
        )
        
        # Identify potential risks
        risk_factors = await self._identify_treatment_risks(
            patient_features, proposed_treatment
        )
        
        # Generate recommendations
        recommendations = await self._generate_treatment_recommendations(
            patient_features, proposed_treatment, success_probability, risk_factors
        )
        
        return {
            "patient_id": patient_profile.get("patient_id"),
            "treatment_plan": proposed_treatment,
            "predictions": {
                "success_probability": success_probability,
                "compatibility_score": compatibility_score,
                "estimated_duration": await self._estimate_treatment_duration(proposed_treatment),
                "cost_prediction": await self._predict_treatment_cost(proposed_treatment)
            },
            "risk_assessment": {
                "risk_level": self._calculate_risk_level(risk_factors),
                "risk_factors": risk_factors,
                "mitigation_strategies": await self._suggest_risk_mitigation(risk_factors)
            },
            "recommendations": recommendations,
            "confidence_level": self._calculate_prediction_confidence(patient_features, proposed_treatment)
        }
    
    def _preprocess_arabic_text(self, text: str) -> str:
        """Preprocess Arabic medical text"""
        
        # Remove diacritics for better processing
        text = araby.strip_diacritics(text)
        
        # Normalize Arabic text
        text = araby.normalize_ligature(text)
        text = araby.normalize_teh(text)
        text = araby.normalize_alef(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def _extract_arabic_medical_entities(self, text: str) -> List[ArabicMedicalEntity]:
        """Extract medical entities from Arabic text"""
        
        entities = []
        
        if not self.ner_pipeline:
            logger.warning("NER pipeline not initialized")
            return entities
        
        try:
            # Use NER pipeline
            ner_results = self.ner_pipeline(text)
            
            for result in ner_results:
                entity_type = self._map_ner_label_to_medical_type(result.get("entity_group", ""))
                
                entity = ArabicMedicalEntity(
                    text=result["word"],
                    entity_type=entity_type,
                    confidence=result["score"],
                    position_start=result["start"],
                    position_end=result["end"]
                )
                
                entities.append(entity)
                
            # Additional rule-based extraction for Arabic medical terms
            rule_based_entities = await self._extract_rule_based_entities(text)
            entities.extend(rule_based_entities)
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
        
        return entities
    
    async def _extract_rule_based_entities(self, text: str) -> List[ArabicMedicalEntity]:
        """Extract entities using rule-based patterns for Arabic medical terms"""
        
        entities = []
        
        # Arabic medical patterns
        patterns = {
            "symptoms": [
                r"يشكو من (.+?)(?:\.|،|$)",  # "complains of"
                r"أعراض (.+?)(?:\.|،|$)",     # "symptoms"  
                r"ألم في (.+?)(?:\.|،|$)",    # "pain in"
                r"يعاني من (.+?)(?:\.|،|$)",  # "suffers from"
            ],
            "diagnosis": [
                r"تشخيص (.+?)(?:\.|،|$)",     # "diagnosis"
                r"مرض (.+?)(?:\.|،|$)",       # "disease"
                r"حالة (.+?)(?:\.|،|$)",      # "condition"
                r"إصابة بـ(.+?)(?:\.|،|$)",    # "infected with"
            ],
            "medications": [
                r"دواء (.+?)(?:\.|،|$)",      # "medication"
                r"علاج (.+?)(?:\.|،|$)",      # "treatment"  
                r"جرعة (.+?)(?:\.|،|$)",      # "dose"
                r"وصف له (.+?)(?:\.|،|$)",    # "prescribed"
            ],
            "procedures": [
                r"إجراء (.+?)(?:\.|،|$)",     # "procedure"
                r"عملية (.+?)(?:\.|،|$)",     # "operation"
                r"فحص (.+?)(?:\.|،|$)",       # "examination"
                r"تحليل (.+?)(?:\.|،|$)",     # "analysis/test"
            ]
        }
        
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity_text = match.group(1).strip()
                    if entity_text:
                        entity = ArabicMedicalEntity(
                            text=entity_text,
                            entity_type=entity_type.rstrip('s'),  # Remove plural
                            confidence=0.8,  # Rule-based confidence
                            position_start=match.start(1),
                            position_end=match.end(1)
                        )
                        entities.append(entity)
        
        return entities
    
    def _format_arabic_medical_text(self, text: str) -> str:
        """Format Arabic text for proper display with RTL support"""
        
        # Reshape Arabic text for proper display
        reshaped_text = arabic_reshaper.reshape(text)
        
        # Apply bidirectional algorithm
        bidi_text = get_display(reshaped_text)
        
        return bidi_text
    
    def _load_arabic_snomed_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load Arabic to SNOMED CT mappings"""
        
        # This would be loaded from a comprehensive database
        return {
            "صداع": {"code": "25064002", "display": "Headache"},
            "حمى": {"code": "386661006", "display": "Fever"},
            "سعال": {"code": "49727002", "display": "Cough"},
            "ألم صدر": {"code": "29857009", "display": "Chest pain"},
            "ضيق تنفس": {"code": "267036007", "display": "Dyspnea"},
            "ارتفاع ضغط الدم": {"code": "38341003", "display": "Hypertension"},
            "داء السكري": {"code": "73211009", "display": "Diabetes mellitus"},
            "التهاب الحلق": {"code": "405737000", "display": "Sore throat"},
            "آلام المعدة": {"code": "271681002", "display": "Stomach ache"},
            "دوخة": {"code": "404640003", "display": "Dizziness"}
            # Add comprehensive mappings
        }
    
    def _load_arabic_icd10_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load Arabic to ICD-10 mappings"""
        
        return {
            "صداع": {"code": "G44.9", "display": "Headache, unspecified"},
            "حمى": {"code": "R50.9", "display": "Fever, unspecified"},
            "سعال": {"code": "R05", "display": "Cough"},
            "ضيق تنفس": {"code": "R06.9", "display": "Unspecified abnormalities of breathing"},
            "ارتفاع ضغط الدم": {"code": "I10", "display": "Essential hypertension"},
            "داء السكري": {"code": "E11", "display": "Type 2 diabetes mellitus"}
            # Add comprehensive mappings
        }
    
    async def _map_to_snomed_codes(self, entities: List[ArabicMedicalEntity]) -> Dict[str, Any]:
        """Map Arabic medical entities to SNOMED CT codes"""
        
        mappings = {}
        
        for entity in entities:
            arabic_term = entity.text.lower()
            
            if arabic_term in self.arabic_to_snomed:
                mappings[entity.text] = {
                    "snomed_code": self.arabic_to_snomed[arabic_term]["code"],
                    "snomed_display": self.arabic_to_snomed[arabic_term]["display"],
                    "confidence": min(entity.confidence, 0.95),
                    "entity_type": entity.entity_type
                }
                entity.snomed_code = self.arabic_to_snomed[arabic_term]["code"]
            else:
                # Use AI similarity matching for unmapped terms
                similar_mapping = await self._find_similar_snomed_mapping(arabic_term)
                if similar_mapping:
                    mappings[entity.text] = similar_mapping
        
        return mappings
    
    async def _find_similar_snomed_mapping(self, arabic_term: str) -> Optional[Dict[str, Any]]:
        """Find similar SNOMED mapping using AI similarity"""
        
        # This would use semantic similarity with existing mappings
        # For now, return None for unmapped terms
        return None
    
    # Additional helper methods...
    async def _classify_medical_content(self, text: str) -> Dict[str, Any]:
        """Classify the type and urgency of medical content"""
        return {"category": "general", "urgency": "routine", "confidence": 0.8}
    
    def _calculate_overall_confidence(self, entities: List[ArabicMedicalEntity], 
                                    classification: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        if not entities:
            return 0.0
        
        entity_confidences = [e.confidence for e in entities]
        classification_confidence = classification.get("confidence", 0.8)
        
        return (sum(entity_confidences) / len(entity_confidences) + classification_confidence) / 2