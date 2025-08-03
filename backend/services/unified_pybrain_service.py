#!/usr/bin/env python3
"""
BrainSAIT Healthcare Platform - PyBrain AI Orchestration Service
Central AI intelligence hub for the unified BrainSAIT ecosystem

This service provides:
1. Central AI orchestration across all platform components
2. Advanced Arabic healthcare intelligence with Saudi dialect support
3. Intelligent workflow automation and optimization
4. Real-time AI insights for OidTree, communication, and NPHIES systems
5. Edge AI processing with intelligent caching
6. Cultural context analysis and communication optimization

Target Performance:
- 95%+ accuracy in Arabic medical NLP
- <200ms response time for AI insights
- 99.9% uptime for critical AI operations
- HIPAA/PDPL compliant AI processing
"""

import asyncio
import logging
import json
import re
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import uuid
from collections import defaultdict, deque
import time
import os

# AI/ML imports
try:
    import openai
    from transformers import pipeline, AutoTokenizer, AutoModel, AutoProcessor
    import torch
    import torch.nn.functional as F
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.feature_extraction.text import TfidfVectorizer
    TORCH_AVAILABLE = torch.cuda.is_available()
    AI_LIBRARIES_AVAILABLE = True
except ImportError:
    AI_LIBRARIES_AVAILABLE = False
    TORCH_AVAILABLE = False

# Arabic processing imports
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    import pyarabic.araby as araby
    from pyarabic import normalize
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

# Healthcare integration imports
from .ai_arabic_service import AIArabicService, ArabicMedicalEntity
from .communication.healthcare_integration import HealthcareSystemIntegrator
from .nphies_service import NPHIESService
from .communication.patient_communication_service import PatientCommunicationService

logger = logging.getLogger(__name__)

class AITaskType(str, Enum):
    """Types of AI tasks supported by PyBrain"""
    ARABIC_NLP = "arabic_nlp"
    MEDICAL_ANALYSIS = "medical_analysis"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE_ANALYTICS = "predictive_analytics"
    CULTURAL_ANALYSIS = "cultural_analysis"
    COMMUNICATION_OPTIMIZATION = "communication_optimization"
    RISK_ASSESSMENT = "risk_assessment"
    TREATMENT_RECOMMENDATION = "treatment_recommendation"
    FRAUD_DETECTION = "fraud_detection"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    PATIENT_INSIGHTS = "patient_insights"
    CLINICAL_DECISION_SUPPORT = "clinical_decision_support"

class AIConfidenceLevel(str, Enum):
    """AI confidence levels for decision making"""
    VERY_HIGH = "very_high"  # 95%+
    HIGH = "high"           # 85-95%
    MEDIUM = "medium"       # 70-85%
    LOW = "low"            # 50-70%
    VERY_LOW = "very_low"  # <50%

class CulturalContext(str, Enum):
    """Saudi cultural contexts for AI analysis"""
    FAMILY_ORIENTED = "family_oriented"
    RELIGIOUS_SENSITIVE = "religious_sensitive"
    GENDER_SPECIFIC = "gender_specific"
    AGE_RESPECTFUL = "age_respectful"
    DIALECT_REGIONAL = "dialect_regional"
    FORMAL_MEDICAL = "formal_medical"
    COLLOQUIAL_FRIENDLY = "colloquial_friendly"

@dataclass
class AIInsight:
    """AI-generated insight with context and confidence"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: AITaskType = AITaskType.MEDICAL_ANALYSIS
    content: str = ""
    confidence_level: AIConfidenceLevel = AIConfidenceLevel.MEDIUM
    confidence_score: float = 0.75
    cultural_context: Optional[CulturalContext] = None
    recommendations: List[str] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    cache_key: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class WorkflowOptimization:
    """AI-powered workflow optimization recommendation"""
    workflow_id: str
    current_efficiency: float
    optimized_efficiency: float
    bottlenecks: List[str]
    recommendations: List[str]
    estimated_savings: Dict[str, float]  # time, cost, resources
    implementation_complexity: str  # low, medium, high
    roi_estimate: float

@dataclass
class AnomalyDetection:
    """AI anomaly detection result"""
    anomaly_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    anomaly_type: str = ""
    severity: str = "medium"  # low, medium, high, critical
    description: str = ""
    affected_systems: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    probability: float = 0.0
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class PredictiveAnalytics:
    """AI predictive analytics result"""
    prediction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prediction_type: str = ""
    predicted_outcome: Any = None
    probability: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 1.0)
    time_horizon: str = ""  # "1_week", "1_month", "3_months", etc.
    influencing_factors: List[str] = field(default_factory=list)
    uncertainty_factors: List[str] = field(default_factory=list)

class AICache:
    """Intelligent caching system for AI results"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.cache: Dict[str, AIInsight] = {}
        self.access_times: Dict[str, datetime] = {}
        self.hit_counts: Dict[str, int] = defaultdict(int)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[AIInsight]:
        """Get cached AI insight"""
        async with self.lock:
            if key in self.cache:
                insight = self.cache[key]
                if insight.expires_at and insight.expires_at > datetime.now():
                    self.access_times[key] = datetime.now()
                    self.hit_counts[key] += 1
                    return insight
                else:
                    # Expired, remove from cache
                    await self._remove(key)
            return None
    
    async def set(self, key: str, insight: AIInsight, ttl: Optional[int] = None):
        """Set cached AI insight"""
        async with self.lock:
            if len(self.cache) >= self.max_size:
                await self._evict_lru()
            
            ttl = ttl or self.default_ttl
            insight.cache_key = key
            insight.expires_at = datetime.now() + timedelta(seconds=ttl)
            
            self.cache[key] = insight
            self.access_times[key] = datetime.now()
            self.hit_counts[key] = 1
    
    async def _remove(self, key: str):
        """Remove item from cache"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.hit_counts.pop(key, None)
    
    async def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        await self._remove(lru_key)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self.lock:
            total_requests = sum(self.hit_counts.values())
            cache_size = len(self.cache)
            hit_rate = (total_requests - cache_size) / total_requests if total_requests > 0 else 0
            
            return {
                "cache_size": cache_size,
                "max_size": self.max_size,
                "hit_rate": round(hit_rate * 100, 2),
                "total_requests": total_requests,
                "memory_usage_mb": cache_size * 0.01  # Rough estimate
            }

class ArabicHealthcareIntelligence:
    """Advanced Arabic healthcare intelligence with Saudi dialect support"""
    
    def __init__(self):
        self.saudi_dialect_patterns = self._load_saudi_dialect_patterns()
        self.cultural_context_rules = self._load_cultural_context_rules()
        self.medical_terminology_ar = self._load_arabic_medical_terminology()
        self.sentiment_analyzer = None
        self.ner_pipeline = None
        
        if AI_LIBRARIES_AVAILABLE:
            asyncio.create_task(self._initialize_models())
    
    def _load_saudi_dialect_patterns(self) -> Dict[str, List[str]]:
        """Load Saudi dialect patterns and variations"""
        return {
            "pain_expressions": [
                "يوجعني", "يؤلمني", "اتعور", "احس بألم", "يضايقني", "متضايق",
                "مو طبيعي", "غريب", "مو زين", "تعبان", "مريض"
            ],
            "severity_indicators": [
                "كثير", "واجد", "مرة", "جداً", "شديد", "ما اقدر", "صعب",
                "قوي", "مستحيل", "ما اطيق", "خلاص", "تعبت"
            ],
            "time_expressions": [
                "من زمان", "من فترة", "من كم يوم", "امس", "اليوم", "باجر",
                "الصبح", "العصر", "المغرب", "الليل", "نص الليل"
            ],
            "family_concerns": [
                "امي تقول", "ابوي يقول", "اهلي خايفين", "زوجتي تقول",
                "ولدي", "بنتي", "اخوي", "اختي", "جدتي", "جدي"
            ],
            "religious_expressions": [
                "الحمدلله", "ان شاء الله", "ماشاء الله", "الله يشفيني",
                "ادعيلي", "بإذن الله", "ربي يعافيني", "حسبي الله"
            ]
        }
    
    def _load_cultural_context_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load Saudi cultural context rules"""
        return {
            "gender_sensitivity": {
                "male_provider_preference": ["أفضل دكتور رجال", "أبي دكتور ذكر"],
                "female_provider_preference": ["أفضل دكتورة", "أبي دكتورة نساء"],
                "family_involvement": ["أبي اهلي يعرفون", "لازم اهلي موافقين"]
            },
            "age_respect": {
                "elderly_terms": ["العم", "الخال", "الوالد", "الوالدة", "كبير السن"],
                "respectful_address": ["حضرتك", "سعادتك", "أستاذ", "دكتور محترم"]
            },
            "religious_sensitivity": {
                "prayer_times": ["وقت الصلاة", "أذان", "فجر", "ظهر", "عصر", "مغرب", "عشاء"],
                "fasting_concerns": ["صايم", "رمضان", "إفطار", "سحور", "صيام"],
                "halal_concerns": ["حلال", "حرام", "مسموح", "ممنوع شرعي"]
            }
        }
    
    def _load_arabic_medical_terminology(self) -> Dict[str, Dict[str, str]]:
        """Load comprehensive Arabic medical terminology"""
        return {
            "symptoms": {
                "صداع": "headache", "حمى": "fever", "سعال": "cough",
                "ضيق تنفس": "dyspnea", "ألم صدر": "chest_pain",
                "غثيان": "nausea", "قيء": "vomiting", "إسهال": "diarrhea",
                "إمساك": "constipation", "دوخة": "dizziness", "تعب": "fatigue",
                "أرق": "insomnia", "فقدان شهية": "anorexia", "زيادة وزن": "weight_gain"
            },
            "body_parts": {
                "رأس": "head", "عين": "eye", "أذن": "ear", "أنف": "nose",
                "فم": "mouth", "رقبة": "neck", "صدر": "chest", "قلب": "heart",
                "رئة": "lung", "بطن": "abdomen", "معدة": "stomach", "كبد": "liver",
                "كلى": "kidney", "ظهر": "back", "يد": "hand", "رجل": "leg"
            },
            "medications": {
                "مسكن": "painkiller", "مضاد حيوي": "antibiotic", "فيتامين": "vitamin",
                "أنسولين": "insulin", "ضغط": "blood_pressure_med", "قلب": "heart_medication",
                "حبوب منع حمل": "contraceptive", "مهدئ": "sedative", "منوم": "sleep_aid"
            }
        }
    
    async def _initialize_models(self):
        """Initialize Arabic AI models"""
        try:
            if AI_LIBRARIES_AVAILABLE:
                # Initialize Arabic sentiment analysis
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment",
                    device=0 if TORCH_AVAILABLE else -1
                )
                
                # Initialize Arabic NER
                self.ner_pipeline = pipeline(
                    "ner",
                    model="CAMeL-Lab/bert-base-arabic-camelbert-msa-ner",
                    aggregation_strategy="simple",
                    device=0 if TORCH_AVAILABLE else -1
                )
                
                logger.info("Arabic AI models initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Arabic models: {e}")
    
    async def analyze_cultural_context(self, text: str, patient_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cultural context in Arabic healthcare communication"""
        analysis = {
            "cultural_markers": [],
            "sensitivity_flags": [],
            "communication_style": "neutral",
            "recommended_approach": [],
            "dialect_indicators": [],
            "family_involvement": False,
            "religious_considerations": []
        }
        
        # Detect cultural markers
        for category, patterns in self.saudi_dialect_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    analysis["cultural_markers"].append({
                        "category": category,
                        "pattern": pattern,
                        "context": self._extract_context(text, pattern)
                    })
        
        # Analyze communication style
        if any(pattern in text for pattern in ["حضرتك", "سعادتك", "دكتور محترم"]):
            analysis["communication_style"] = "formal"
        elif any(pattern in text for pattern in ["يا دكتور", "دكتور", "أستاذ"]):
            analysis["communication_style"] = "respectful"
        elif any(pattern in text for pattern in ["يوجعني", "اتعور", "تعبان"]):
            analysis["communication_style"] = "colloquial"
        
        # Detect family involvement
        family_patterns = self.saudi_dialect_patterns.get("family_concerns", [])
        if any(pattern in text for pattern in family_patterns):
            analysis["family_involvement"] = True
            analysis["recommended_approach"].append("involve_family_in_communication")
        
        # Detect religious considerations
        religious_patterns = self.saudi_dialect_patterns.get("religious_expressions", [])
        religious_found = [pattern for pattern in religious_patterns if pattern in text]
        if religious_found:
            analysis["religious_considerations"] = religious_found
            analysis["recommended_approach"].append("acknowledge_religious_expressions")
        
        # Gender sensitivity
        patient_gender = patient_metadata.get("gender", "").lower()
        if patient_gender in ["female", "أنثى", "امرأة"]:
            analysis["sensitivity_flags"].append("female_patient_considerations")
        
        # Age considerations
        patient_age = patient_metadata.get("age", 0)
        if patient_age >= 60:
            analysis["sensitivity_flags"].append("elderly_patient_respect")
            analysis["recommended_approach"].append("use_respectful_titles")
        
        return analysis
    
    def _extract_context(self, text: str, pattern: str, window: int = 20) -> str:
        """Extract context around a pattern match"""
        pattern_index = text.find(pattern)
        if pattern_index == -1:
            return ""
        
        start = max(0, pattern_index - window)
        end = min(len(text), pattern_index + len(pattern) + window)
        return text[start:end].strip()
    
    async def optimize_arabic_communication(self, 
                                          message: str, 
                                          cultural_context: Dict[str, Any],
                                          patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize Arabic communication based on cultural context"""
        optimization = {
            "optimized_message": message,
            "improvements_made": [],
            "cultural_adaptations": [],
            "tone_adjustments": [],
            "respectfulness_score": 0.8
        }
        
        # Apply cultural adaptations
        if cultural_context.get("family_involvement"):
            if "العائلة" not in message and "الأهل" not in message:
                optimization["optimized_message"] += " يرجى إشراك العائلة في القرارات الطبية."
                optimization["cultural_adaptations"].append("added_family_involvement")
        
        # Apply religious sensitivity
        if cultural_context.get("religious_considerations"):
            if not any(expr in message for expr in ["إن شاء الله", "بإذن الله", "الحمدلله"]):
                optimization["optimized_message"] = "بإذن الله، " + optimization["optimized_message"]
                optimization["cultural_adaptations"].append("added_religious_expression")
        
        # Adjust tone based on age
        patient_age = patient_profile.get("age", 0)
        if patient_age >= 60:
            # Make more formal and respectful
            optimization["optimized_message"] = optimization["optimized_message"].replace(
                "يمكنك", "يمكن لحضرتك"
            ).replace("أنت", "حضرتك")
            optimization["tone_adjustments"].append("increased_formality_for_elderly")
        
        # Gender-appropriate language
        patient_gender = patient_profile.get("gender", "").lower()
        if patient_gender in ["female", "أنثى"]:
            # Ensure feminine forms are used
            optimization["optimized_message"] = self._feminize_arabic_text(
                optimization["optimized_message"]
            )
            optimization["tone_adjustments"].append("gender_appropriate_language")
        
        # Calculate respectfulness score
        respectful_indicators = ["حضرتك", "سعادتك", "دكتور محترم", "بإذن الله", "إن شاء الله"]
        respectfulness_count = sum(1 for indicator in respectful_indicators 
                                 if indicator in optimization["optimized_message"])
        optimization["respectfulness_score"] = min(1.0, respectfulness_count * 0.2 + 0.6)
        
        return optimization
    
    def _feminize_arabic_text(self, text: str) -> str:
        """Apply feminine forms to Arabic text"""
        # Basic feminine form conversions
        conversions = {
            "مريض": "مريضة",
            "المريض": "المريضة",
            "متعب": "متعبة",
            "شاكر": "شاكرة",
            "مهتم": "مهتمة"
        }
        
        for masculine, feminine in conversions.items():
            text = text.replace(masculine, feminine)
        
        return text

class IntelligentWorkflowOptimizer:
    """AI-powered workflow optimization for healthcare processes"""
    
    def __init__(self):
        self.workflow_patterns = {}
        self.performance_metrics = defaultdict(list)
        self.optimization_history = []
        
    async def analyze_workflow_efficiency(self, 
                                        workflow_data: Dict[str, Any],
                                        historical_data: List[Dict[str, Any]]) -> WorkflowOptimization:
        """Analyze and optimize healthcare workflow efficiency"""
        
        workflow_id = workflow_data.get("workflow_id", "unknown")
        current_metrics = workflow_data.get("metrics", {})
        
        # Calculate current efficiency
        current_efficiency = self._calculate_efficiency_score(current_metrics)
        
        # Identify bottlenecks
        bottlenecks = await self._identify_bottlenecks(workflow_data, historical_data)
        
        # Generate optimization recommendations
        recommendations = await self._generate_workflow_recommendations(
            workflow_data, bottlenecks, historical_data
        )
        
        # Estimate optimized efficiency
        optimized_efficiency = await self._estimate_optimized_efficiency(
            current_efficiency, recommendations
        )
        
        # Calculate potential savings
        estimated_savings = await self._calculate_potential_savings(
            current_metrics, recommendations
        )
        
        # Assess implementation complexity
        implementation_complexity = self._assess_implementation_complexity(recommendations)
        
        # Calculate ROI estimate
        roi_estimate = self._calculate_roi_estimate(estimated_savings, implementation_complexity)
        
        optimization = WorkflowOptimization(
            workflow_id=workflow_id,
            current_efficiency=current_efficiency,
            optimized_efficiency=optimized_efficiency,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            estimated_savings=estimated_savings,
            implementation_complexity=implementation_complexity,
            roi_estimate=roi_estimate
        )
        
        # Store optimization for learning
        self.optimization_history.append(optimization)
        
        return optimization
    
    def _calculate_efficiency_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate workflow efficiency score (0.0 to 1.0)"""
        factors = {
            "processing_time": metrics.get("avg_processing_time", 600),  # seconds
            "error_rate": metrics.get("error_rate", 0.05),  # percentage
            "resource_utilization": metrics.get("resource_utilization", 0.7),  # percentage
            "patient_satisfaction": metrics.get("patient_satisfaction", 0.8),  # score
            "staff_satisfaction": metrics.get("staff_satisfaction", 0.75)  # score
        }
        
        # Normalize and weight factors
        time_score = max(0, 1 - (factors["processing_time"] - 300) / 1200)  # 5-25 min range
        error_score = max(0, 1 - factors["error_rate"] * 10)  # Error rate impact
        resource_score = factors["resource_utilization"]
        patient_score = factors["patient_satisfaction"]
        staff_score = factors["staff_satisfaction"]
        
        # Weighted average
        efficiency = (
            time_score * 0.25 +
            error_score * 0.2 +
            resource_score * 0.2 +
            patient_score * 0.2 +
            staff_score * 0.15
        )
        
        return round(efficiency, 3)
    
    async def _identify_bottlenecks(self, 
                                  workflow_data: Dict[str, Any],
                                  historical_data: List[Dict[str, Any]]) -> List[str]:
        """Identify workflow bottlenecks using AI analysis"""
        bottlenecks = []
        
        # Analyze step durations
        steps = workflow_data.get("steps", [])
        for step in steps:
            avg_duration = step.get("avg_duration", 0)
            if avg_duration > 300:  # More than 5 minutes
                bottlenecks.append(f"Step '{step.get('name')}' takes too long ({avg_duration}s)")
        
        # Analyze resource constraints
        resources = workflow_data.get("resource_usage", {})
        for resource, utilization in resources.items():
            if utilization > 0.9:  # Over 90% utilization
                bottlenecks.append(f"Resource '{resource}' is overutilized ({utilization*100:.1f}%)")
        
        # Analyze error patterns
        errors = workflow_data.get("common_errors", [])
        for error in errors:
            if error.get("frequency", 0) > 0.1:  # More than 10% occurrence
                bottlenecks.append(f"Frequent error: {error.get('type')} ({error.get('frequency')*100:.1f}%)")
        
        # Analyze waiting times
        wait_times = workflow_data.get("wait_times", {})
        for stage, wait_time in wait_times.items():
            if wait_time > 600:  # More than 10 minutes
                bottlenecks.append(f"Long wait time at '{stage}' ({wait_time}s)")
        
        return bottlenecks
    
    async def _generate_workflow_recommendations(self, 
                                               workflow_data: Dict[str, Any],
                                               bottlenecks: List[str],
                                               historical_data: List[Dict[str, Any]]) -> List[str]:
        """Generate AI-powered workflow optimization recommendations"""
        recommendations = []
        
        # Analyze bottlenecks and suggest solutions
        for bottleneck in bottlenecks:
            if "takes too long" in bottleneck:
                recommendations.append("Implement parallel processing for time-consuming steps")
                recommendations.append("Add automation for repetitive tasks")
            
            elif "overutilized" in bottleneck:
                recommendations.append("Scale up resources during peak hours")
                recommendations.append("Implement load balancing for resource distribution")
            
            elif "Frequent error" in bottleneck:
                recommendations.append("Implement additional validation checks")
                recommendations.append("Provide targeted staff training")
            
            elif "Long wait time" in bottleneck:
                recommendations.append("Optimize scheduling algorithms")
                recommendations.append("Implement queue management system")
        
        # General optimization recommendations
        current_efficiency = self._calculate_efficiency_score(workflow_data.get("metrics", {}))
        if current_efficiency < 0.7:
            recommendations.extend([
                "Conduct comprehensive workflow analysis",
                "Implement real-time monitoring dashboard",
                "Establish performance benchmarks"
            ])
        
        # AI-powered predictive recommendations
        if len(historical_data) > 10:
            recommendations.extend([
                "Implement predictive scheduling based on historical patterns",
                "Use AI-powered resource allocation optimization",
                "Deploy anomaly detection for early problem identification"
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _estimate_optimized_efficiency(self, 
                                           current_efficiency: float,
                                           recommendations: List[str]) -> float:
        """Estimate efficiency after implementing recommendations"""
        improvement_factors = {
            "automation": 0.15,
            "parallel processing": 0.12,
            "load balancing": 0.08,
            "predictive": 0.10,
            "monitoring": 0.05,
            "training": 0.06,
            "validation": 0.04,
            "optimization": 0.07
        }
        
        total_improvement = 0.0
        for recommendation in recommendations:
            for factor, improvement in improvement_factors.items():
                if factor in recommendation.lower():
                    total_improvement += improvement
                    break
        
        # Apply diminishing returns
        max_improvement = min(total_improvement, 0.3)  # Cap at 30% improvement
        optimized_efficiency = min(1.0, current_efficiency + max_improvement)
        
        return round(optimized_efficiency, 3)
    
    async def _calculate_potential_savings(self, 
                                         current_metrics: Dict[str, Any],
                                         recommendations: List[str]) -> Dict[str, float]:
        """Calculate potential savings from optimization"""
        savings = {
            "time_saved_hours_per_day": 0.0,
            "cost_saved_per_month": 0.0,
            "error_reduction_percentage": 0.0,
            "resource_efficiency_gain": 0.0
        }
        
        # Time savings estimation
        current_processing_time = current_metrics.get("avg_processing_time", 600)
        if any("automation" in rec.lower() for rec in recommendations):
            savings["time_saved_hours_per_day"] += 2.0
        if any("parallel" in rec.lower() for rec in recommendations):
            savings["time_saved_hours_per_day"] += 1.5
        
        # Cost savings estimation
        if savings["time_saved_hours_per_day"] > 0:
            savings["cost_saved_per_month"] = savings["time_saved_hours_per_day"] * 30 * 50  # $50/hour
        
        # Error reduction estimation
        if any("validation" in rec.lower() or "training" in rec.lower() for rec in recommendations):
            savings["error_reduction_percentage"] = 15.0
        
        # Resource efficiency estimation
        if any("load balancing" in rec.lower() or "optimization" in rec.lower() for rec in recommendations):
            savings["resource_efficiency_gain"] = 20.0
        
        return savings
    
    def _assess_implementation_complexity(self, recommendations: List[str]) -> str:
        """Assess implementation complexity of recommendations"""
        complexity_scores = {
            "training": 1,
            "monitoring": 2,
            "validation": 2,
            "automation": 4,
            "parallel processing": 4,
            "predictive": 5,
            "ai-powered": 5,
            "comprehensive": 3
        }
        
        total_score = 0
        for recommendation in recommendations:
            for keyword, score in complexity_scores.items():
                if keyword in recommendation.lower():
                    total_score += score
                    break
        
        avg_score = total_score / len(recommendations) if recommendations else 0
        
        if avg_score < 2:
            return "low"
        elif avg_score < 4:
            return "medium"
        else:
            return "high"
    
    def _calculate_roi_estimate(self, 
                              estimated_savings: Dict[str, float],
                              implementation_complexity: str) -> float:
        """Calculate ROI estimate for workflow optimization"""
        # Implementation cost estimates
        complexity_costs = {
            "low": 5000,      # $5K
            "medium": 15000,  # $15K
            "high": 50000     # $50K
        }
        
        implementation_cost = complexity_costs.get(implementation_complexity, 15000)
        annual_savings = estimated_savings.get("cost_saved_per_month", 0) * 12
        
        if implementation_cost == 0:
            return 0.0
        
        roi = ((annual_savings - implementation_cost) / implementation_cost) * 100
        return round(roi, 1)

class UnifiedPyBrainService:
    """Central AI orchestration service for the BrainSAIT platform"""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 cache_size: int = 10000,
                 enable_edge_ai: bool = True):
        
        # Core configuration
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.enable_edge_ai = enable_edge_ai
        
        # Initialize components
        self.cache = AICache(max_size=cache_size)
        self.arabic_intelligence = ArabicHealthcareIntelligence()
        self.workflow_optimizer = IntelligentWorkflowOptimizer()
        
        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "average_response_time_ms": 0.0,
            "cache_hit_rate": 0.0,
            "error_rate": 0.0,
            "insights_generated": 0
        }
        
        # Initialize AI services integration
        self.ai_arabic_service = None
        self.healthcare_integrator = None
        self.nphies_service = None
        
        # Initialize OpenAI if available
        if self.openai_api_key and AI_LIBRARIES_AVAILABLE:
            openai.api_key = self.openai_api_key
            logger.info("PyBrain AI orchestration service initialized successfully")
        else:
            logger.warning("PyBrain initialized with limited AI capabilities")
    
    async def initialize_integrations(self, 
                                    ai_arabic_service: Optional[AIArabicService] = None,
                                    healthcare_integrator: Optional[HealthcareSystemIntegrator] = None,
                                    nphies_service: Optional[NPHIESService] = None):
        """Initialize integrations with existing BrainSAIT services"""
        self.ai_arabic_service = ai_arabic_service
        self.healthcare_integrator = healthcare_integrator
        self.nphies_service = nphies_service
        logger.info("PyBrain service integrations initialized")
    
    async def generate_ai_insight(self, 
                                task_type: AITaskType,
                                input_data: Dict[str, Any],
                                context: Optional[Dict[str, Any]] = None,
                                force_refresh: bool = False) -> AIInsight:
        """Generate AI insight with intelligent caching"""
        start_time = time.time()
        
        try:
            # Create cache key
            cache_key = self._create_cache_key(task_type, input_data, context)
            
            # Check cache first (unless forced refresh)
            if not force_refresh:
                cached_insight = await self.cache.get(cache_key)
                if cached_insight:
                    logger.debug(f"Cache hit for {task_type.value}")
                    return cached_insight
            
            # Generate new insight
            insight = await self._generate_insight_by_type(task_type, input_data, context)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            insight.processing_time_ms = processing_time
            
            # Cache the result
            await self.cache.set(cache_key, insight)
            
            # Update metrics
            await self._update_metrics(processing_time)
            
            logger.info(f"Generated {task_type.value} insight in {processing_time:.2f}ms")
            return insight
            
        except Exception as e:
            logger.error(f"Failed to generate AI insight for {task_type.value}: {e}")
            return AIInsight(
                task_type=task_type,
                content=f"Error generating insight: {str(e)}",
                confidence_level=AIConfidenceLevel.VERY_LOW,
                confidence_score=0.0
            )
    
    async def _generate_insight_by_type(self, 
                                      task_type: AITaskType,
                                      input_data: Dict[str, Any],
                                      context: Optional[Dict[str, Any]]) -> AIInsight:
        """Generate insight based on task type"""
        
        if task_type == AITaskType.ARABIC_NLP:
            return await self._analyze_arabic_text(input_data, context)
        
        elif task_type == AITaskType.MEDICAL_ANALYSIS:
            return await self._analyze_medical_content(input_data, context)
        
        elif task_type == AITaskType.WORKFLOW_OPTIMIZATION:
            return await self._optimize_workflow(input_data, context)
        
        elif task_type == AITaskType.ANOMALY_DETECTION:
            return await self._detect_anomalies(input_data, context)
        
        elif task_type == AITaskType.CULTURAL_ANALYSIS:
            return await self._analyze_cultural_context(input_data, context)
        
        elif task_type == AITaskType.COMMUNICATION_OPTIMIZATION:
            return await self._optimize_communication(input_data, context)
        
        elif task_type == AITaskType.PREDICTIVE_ANALYTICS:
            return await self._generate_predictions(input_data, context)
        
        elif task_type == AITaskType.RISK_ASSESSMENT:
            return await self._assess_risks(input_data, context)
        
        elif task_type == AITaskType.FRAUD_DETECTION:
            return await self._detect_fraud(input_data, context)
        
        elif task_type == AITaskType.CLINICAL_DECISION_SUPPORT:
            return await self._provide_clinical_support(input_data, context)
        
        else:
            return AIInsight(
                task_type=task_type,
                content="Unsupported task type",
                confidence_level=AIConfidenceLevel.VERY_LOW,
                confidence_score=0.0
            )
    
    async def _analyze_arabic_text(self, 
                                 input_data: Dict[str, Any],
                                 context: Optional[Dict[str, Any]]) -> AIInsight:
        """Analyze Arabic text with healthcare context"""
        text = input_data.get("text", "")
        patient_data = context.get("patient_data", {}) if context else {}
        
        # Use existing AI Arabic service if available
        if self.ai_arabic_service:
            analysis_result = await self.ai_arabic_service.process_arabic_medical_text(text)
            
            insight = AIInsight(
                task_type=AITaskType.ARABIC_NLP,
                content=f"Analyzed Arabic medical text with {len(analysis_result.get('entities', []))} entities identified",
                confidence_score=analysis_result.get("confidence_score", 0.8),
                supporting_data=analysis_result
            )
        else:
            # Fallback analysis
            insight = AIInsight(
                task_type=AITaskType.ARABIC_NLP,
                content=f"Basic Arabic text analysis completed. Text length: {len(text)} characters",
                confidence_score=0.6,
                supporting_data={"text_length": len(text), "language": "arabic"}
            )
        
        # Add cultural context analysis
        if patient_data:
            cultural_analysis = await self.arabic_intelligence.analyze_cultural_context(
                text, patient_data
            )
            insight.supporting_data["cultural_analysis"] = cultural_analysis
            
            if cultural_analysis.get("family_involvement"):
                insight.cultural_context = CulturalContext.FAMILY_ORIENTED
            elif cultural_analysis.get("religious_considerations"):
                insight.cultural_context = CulturalContext.RELIGIOUS_SENSITIVE
        
        return insight
    
    async def _analyze_medical_content(self, 
                                     input_data: Dict[str, Any],
                                     context: Optional[Dict[str, Any]]) -> AIInsight:
        """Analyze medical content for insights"""
        medical_data = input_data.get("medical_data", {})
        patient_id = input_data.get("patient_id", "")
        
        analysis = {
            "risk_factors": [],
            "treatment_recommendations": [],
            "follow_up_required": False,
            "urgency_level": "routine"
        }
        
        # Analyze vital signs if present
        vitals = medical_data.get("vitals", {})
        if vitals:
            if vitals.get("blood_pressure_systolic", 0) > 140:
                analysis["risk_factors"].append("Hypertension")
                analysis["treatment_recommendations"].append("Monitor blood pressure regularly")
            
            if vitals.get("temperature", 36.5) > 38.0:
                analysis["risk_factors"].append("Fever")
                analysis["urgency_level"] = "urgent"
        
        # Analyze symptoms
        symptoms = medical_data.get("symptoms", [])
        if symptoms:
            serious_symptoms = ["chest pain", "difficulty breathing", "severe headache"]
            if any(symptom in symptoms for symptom in serious_symptoms):
                analysis["urgency_level"] = "emergency"
                analysis["follow_up_required"] = True
        
        confidence_score = 0.8 if vitals or symptoms else 0.5
        
        return AIInsight(
            task_type=AITaskType.MEDICAL_ANALYSIS,
            content=f"Medical analysis completed for patient {patient_id}",
            confidence_score=confidence_score,
            supporting_data=analysis,
            recommendations=analysis["treatment_recommendations"]
        )
    
    async def _optimize_workflow(self, 
                               input_data: Dict[str, Any],
                               context: Optional[Dict[str, Any]]) -> AIInsight:
        """Optimize healthcare workflow using AI"""
        workflow_data = input_data.get("workflow_data", {})
        historical_data = input_data.get("historical_data", [])
        
        optimization = await self.workflow_optimizer.analyze_workflow_efficiency(
            workflow_data, historical_data
        )
        
        # Determine confidence based on data quality
        confidence_score = 0.9 if len(historical_data) > 50 else 0.7
        if not workflow_data.get("metrics"):
            confidence_score *= 0.8
        
        confidence_level = AIConfidenceLevel.HIGH if confidence_score > 0.85 else AIConfidenceLevel.MEDIUM
        
        return AIInsight(
            task_type=AITaskType.WORKFLOW_OPTIMIZATION,
            content=f"Workflow optimization completed. Current efficiency: {optimization.current_efficiency:.1%}, "
                   f"Optimized efficiency: {optimization.optimized_efficiency:.1%}",
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            supporting_data=optimization.__dict__,
            recommendations=optimization.recommendations
        )
    
    async def _detect_anomalies(self, 
                              input_data: Dict[str, Any],
                              context: Optional[Dict[str, Any]]) -> AIInsight:
        """Detect anomalies in healthcare data"""
        data_points = input_data.get("data_points", [])
        system_metrics = input_data.get("system_metrics", {})
        
        anomalies = []
        
        # Check for data anomalies
        if data_points:
            # Simple statistical anomaly detection
            values = [point.get("value", 0) for point in data_points if isinstance(point.get("value"), (int, float))]
            if values:
                mean_val = np.mean(values)
                std_val = np.std(values)
                threshold = 2 * std_val
                
                for i, value in enumerate(values):
                    if abs(value - mean_val) > threshold:
                        anomalies.append({
                            "type": "statistical_outlier",
                            "index": i,
                            "value": value,
                            "deviation": abs(value - mean_val),
                            "severity": "high" if abs(value - mean_val) > 3 * std_val else "medium"
                        })
        
        # Check system metrics anomalies
        if system_metrics:
            if system_metrics.get("error_rate", 0) > 0.1:  # >10% error rate
                anomalies.append({
                    "type": "high_error_rate",
                    "value": system_metrics["error_rate"],
                    "severity": "critical"
                })
            
            if system_metrics.get("response_time", 0) > 5000:  # >5 seconds
                anomalies.append({
                    "type": "slow_response_time",
                    "value": system_metrics["response_time"],
                    "severity": "high"
                })
        
        confidence_score = 0.85 if len(data_points) > 100 else 0.7
        
        return AIInsight(
            task_type=AITaskType.ANOMALY_DETECTION,
            content=f"Anomaly detection completed. Found {len(anomalies)} anomalies",
            confidence_score=confidence_score,
            supporting_data={"anomalies": anomalies, "total_data_points": len(data_points)},
            recommendations=[f"Investigate {anomaly['type']}" for anomaly in anomalies[:3]]
        )
    
    async def _analyze_cultural_context(self, 
                                      input_data: Dict[str, Any],
                                      context: Optional[Dict[str, Any]]) -> AIInsight:
        """Analyze cultural context for Saudi healthcare"""
        text = input_data.get("text", "")
        patient_profile = input_data.get("patient_profile", {})
        
        cultural_analysis = await self.arabic_intelligence.analyze_cultural_context(
            text, patient_profile
        )
        
        # Determine primary cultural context
        primary_context = CulturalContext.FORMAL_MEDICAL
        if cultural_analysis.get("family_involvement"):
            primary_context = CulturalContext.FAMILY_ORIENTED
        elif cultural_analysis.get("religious_considerations"):
            primary_context = CulturalContext.RELIGIOUS_SENSITIVE
        elif patient_profile.get("gender") == "female":
            primary_context = CulturalContext.GENDER_SPECIFIC
        
        return AIInsight(
            task_type=AITaskType.CULTURAL_ANALYSIS,
            content=f"Cultural context analysis completed. Primary context: {primary_context.value}",
            confidence_score=0.85,
            cultural_context=primary_context,
            supporting_data=cultural_analysis,
            recommendations=cultural_analysis.get("recommended_approach", [])
        )
    
    async def _optimize_communication(self, 
                                    input_data: Dict[str, Any],
                                    context: Optional[Dict[str, Any]]) -> AIInsight:
        """Optimize healthcare communication"""
        message = input_data.get("message", "")
        patient_profile = input_data.get("patient_profile", {})
        communication_channel = input_data.get("channel", "sms")
        
        # Get cultural context first
        cultural_context = await self.arabic_intelligence.analyze_cultural_context(
            message, patient_profile
        )
        
        # Optimize the communication
        optimization = await self.arabic_intelligence.optimize_arabic_communication(
            message, cultural_context, patient_profile
        )
        
        return AIInsight(
            task_type=AITaskType.COMMUNICATION_OPTIMIZATION,
            content=f"Communication optimized for {communication_channel}. "
                   f"Respectfulness score: {optimization['respectfulness_score']:.2f}",
            confidence_score=0.9,
            supporting_data={
                "original_message": message,
                "optimized_message": optimization["optimized_message"],
                "improvements": optimization["improvements_made"],
                "cultural_adaptations": optimization["cultural_adaptations"],
                "respectfulness_score": optimization["respectfulness_score"]
            },
            recommendations=optimization["cultural_adaptations"]
        )
    
    async def _generate_predictions(self, 
                                  input_data: Dict[str, Any],
                                  context: Optional[Dict[str, Any]]) -> AIInsight:
        """Generate predictive analytics insights"""
        prediction_type = input_data.get("prediction_type", "patient_outcome")
        historical_data = input_data.get("historical_data", [])
        patient_data = input_data.get("patient_data", {})
        
        predictions = {
            "primary_prediction": None,
            "confidence_interval": (0.0, 1.0),
            "influencing_factors": [],
            "time_horizon": "30_days"
        }
        
        if prediction_type == "patient_outcome":
            # Simple outcome prediction based on risk factors
            risk_factors = patient_data.get("risk_factors", [])
            age = patient_data.get("age", 40)
            
            # Basic risk scoring
            risk_score = len(risk_factors) * 0.1 + (age - 40) * 0.002
            risk_score = min(1.0, max(0.0, risk_score))
            
            predictions["primary_prediction"] = {
                "outcome": "positive" if risk_score < 0.3 else "needs_monitoring" if risk_score < 0.7 else "high_risk",
                "probability": 1 - risk_score if risk_score < 0.3 else risk_score
            }
            predictions["influencing_factors"] = risk_factors + ["age", "medical_history"]
        
        elif prediction_type == "resource_demand":
            # Predict resource demand based on historical patterns
            if historical_data:
                recent_demand = sum(data.get("demand", 0) for data in historical_data[-7:]) / 7
                predictions["primary_prediction"] = {
                    "predicted_demand": recent_demand * 1.1,  # 10% increase assumption
                    "confidence": 0.75
                }
        
        confidence_score = 0.8 if len(historical_data) > 30 else 0.6
        
        return AIInsight(
            task_type=AITaskType.PREDICTIVE_ANALYTICS,
            content=f"Predictive analysis completed for {prediction_type}",
            confidence_score=confidence_score,
            supporting_data=predictions
        )
    
    async def _assess_risks(self, 
                          input_data: Dict[str, Any],
                          context: Optional[Dict[str, Any]]) -> AIInsight:
        """Assess healthcare risks using AI"""
        patient_data = input_data.get("patient_data", {})
        procedure_data = input_data.get("procedure_data", {})
        
        risk_assessment = {
            "overall_risk_level": "low",
            "specific_risks": [],
            "mitigation_strategies": [],
            "monitoring_requirements": []
        }
        
        # Assess patient-specific risks
        age = patient_data.get("age", 0)
        medical_history = patient_data.get("medical_history", [])
        current_medications = patient_data.get("medications", [])
        
        risk_score = 0.0
        
        # Age-based risk
        if age > 65:
            risk_score += 0.2
            risk_assessment["specific_risks"].append("Age-related complications")
        
        # Medical history risks
        high_risk_conditions = ["diabetes", "hypertension", "heart disease", "kidney disease"]
        for condition in medical_history:
            if any(high_risk in condition.lower() for high_risk in high_risk_conditions):
                risk_score += 0.15
                risk_assessment["specific_risks"].append(f"Pre-existing {condition}")
        
        # Medication interaction risks
        if len(current_medications) > 5:
            risk_score += 0.1
            risk_assessment["specific_risks"].append("Polypharmacy risk")
        
        # Procedure-specific risks
        if procedure_data:
            procedure_type = procedure_data.get("type", "").lower()
            if "surgery" in procedure_type:
                risk_score += 0.2
                risk_assessment["specific_risks"].append("Surgical complications")
        
        # Determine overall risk level
        if risk_score < 0.3:
            risk_assessment["overall_risk_level"] = "low"
        elif risk_score < 0.6:
            risk_assessment["overall_risk_level"] = "medium"
        else:
            risk_assessment["overall_risk_level"] = "high"
        
        # Generate mitigation strategies
        if risk_score > 0.3:
            risk_assessment["mitigation_strategies"] = [
                "Enhanced pre-procedure screening",
                "Continuous monitoring during procedure",
                "Post-procedure follow-up within 24 hours"
            ]
        
        confidence_score = 0.85 if medical_history else 0.7
        
        return AIInsight(
            task_type=AITaskType.RISK_ASSESSMENT,
            content=f"Risk assessment completed. Overall risk level: {risk_assessment['overall_risk_level']}",
            confidence_score=confidence_score,
            supporting_data=risk_assessment,
            recommendations=risk_assessment["mitigation_strategies"]
        )
    
    async def _detect_fraud(self, 
                          input_data: Dict[str, Any],
                          context: Optional[Dict[str, Any]]) -> AIInsight:
        """Detect potential fraud in healthcare claims"""
        claims_data = input_data.get("claims_data", [])
        
        if self.ai_arabic_service:
            # Use existing fraud detection service
            fraud_results = await self.ai_arabic_service.analyze_claims_for_fraud(claims_data)
            
            high_risk_claims = [result for result in fraud_results if result.fraud_probability > 0.7]
            
            return AIInsight(
                task_type=AITaskType.FRAUD_DETECTION,
                content=f"Fraud detection completed. {len(high_risk_claims)} high-risk claims identified",
                confidence_score=0.9,
                supporting_data={"fraud_results": [result.__dict__ for result in fraud_results]},
                recommendations=[f"Investigate claim {claim.claim_id}" for claim in high_risk_claims[:5]]
            )
        else:
            # Basic fraud detection
            suspicious_patterns = []
            
            for claim in claims_data:
                claim_amount = claim.get("amount", 0)
                if claim_amount > 50000:  # High amount threshold
                    suspicious_patterns.append({
                        "claim_id": claim.get("claim_id"),
                        "pattern": "high_amount",
                        "risk_score": 0.7
                    })
            
            return AIInsight(
                task_type=AITaskType.FRAUD_DETECTION,
                content=f"Basic fraud screening completed. {len(suspicious_patterns)} suspicious patterns found",
                confidence_score=0.6,
                supporting_data={"suspicious_patterns": suspicious_patterns}
            )
    
    async def _provide_clinical_support(self, 
                                      input_data: Dict[str, Any],
                                      context: Optional[Dict[str, Any]]) -> AIInsight:
        """Provide AI-powered clinical decision support"""
        patient_data = input_data.get("patient_data", {})
        clinical_question = input_data.get("clinical_question", "")
        
        support_data = {
            "recommendations": [],
            "differential_diagnosis": [],
            "suggested_tests": [],
            "treatment_options": [],
            "guidelines_referenced": []
        }
        
        # Analyze symptoms for recommendations
        symptoms = patient_data.get("symptoms", [])
        if symptoms:
            if "chest pain" in symptoms:
                support_data["differential_diagnosis"] = [
                    "Myocardial infarction", "Angina", "Pulmonary embolism", "Costochondritis"
                ]
                support_data["suggested_tests"] = ["ECG", "Troponin", "Chest X-ray"]
                support_data["recommendations"] = ["Immediate cardiac evaluation", "Monitor vital signs"]
            
            elif "headache" in symptoms:
                support_data["differential_diagnosis"] = [
                    "Tension headache", "Migraine", "Cluster headache", "Secondary headache"
                ]
                support_data["suggested_tests"] = ["Neurological examination", "CT scan if red flags"]
        
        # Generate general recommendations based on clinical question
        if "treatment" in clinical_question.lower():
            support_data["treatment_options"] = [
                "Conservative management",
                "Pharmacological intervention",
                "Specialist referral if indicated"
            ]
        
        confidence_score = 0.8 if symptoms else 0.6
        
        return AIInsight(
            task_type=AITaskType.CLINICAL_DECISION_SUPPORT,
            content=f"Clinical decision support provided for: {clinical_question}",
            confidence_score=confidence_score,
            supporting_data=support_data,
            recommendations=support_data["recommendations"]
        )
    
    def _create_cache_key(self, 
                         task_type: AITaskType,
                         input_data: Dict[str, Any],
                         context: Optional[Dict[str, Any]]) -> str:
        """Create cache key for AI insight"""
        # Create deterministic hash of input data
        data_str = json.dumps({
            "task_type": task_type.value,
            "input_data": input_data,
            "context": context or {}
        }, sort_keys=True, default=str)
        
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def _update_metrics(self, processing_time_ms: float):
        """Update performance metrics"""
        self.performance_metrics["total_requests"] += 1
        self.performance_metrics["insights_generated"] += 1
        
        # Update average response time
        current_avg = self.performance_metrics["average_response_time_ms"]
        total_requests = self.performance_metrics["total_requests"]
        new_avg = ((current_avg * (total_requests - 1)) + processing_time_ms) / total_requests
        self.performance_metrics["average_response_time_ms"] = round(new_avg, 2)
        
        # Update cache hit rate
        cache_stats = await self.cache.get_stats()
        self.performance_metrics["cache_hit_rate"] = cache_stats.get("hit_rate", 0.0)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        cache_stats = await self.cache.get_stats()
        
        return {
            **self.performance_metrics,
            "cache_stats": cache_stats,
            "uptime_hours": time.time() / 3600,  # Rough uptime calculation
            "system_status": "healthy" if self.performance_metrics["error_rate"] < 0.05 else "degraded"
        }
    
    async def batch_process_insights(self, 
                                   tasks: List[Dict[str, Any]],
                                   max_concurrent: int = 10) -> List[AIInsight]:
        """Process multiple AI tasks concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_task(task_data: Dict[str, Any]) -> AIInsight:
            async with semaphore:
                return await self.generate_ai_insight(
                    AITaskType(task_data["task_type"]),
                    task_data.get("input_data", {}),
                    task_data.get("context", {}),
                    task_data.get("force_refresh", False)
                )
        
        results = await asyncio.gather(
            *[process_single_task(task) for task in tasks],
            return_exceptions=True
        )
        
        # Convert exceptions to error insights
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_insight = AIInsight(
                    task_type=AITaskType(tasks[i]["task_type"]),
                    content=f"Error processing task: {str(result)}",
                    confidence_level=AIConfidenceLevel.VERY_LOW,
                    confidence_score=0.0
                )
                processed_results.append(error_insight)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_realtime_insights(self, 
                                  system_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get real-time AI insights for system monitoring"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "system_health": {},
            "anomalies": [],
            "recommendations": [],
            "predictions": {}
        }
        
        # System health analysis
        performance_metrics = await self.get_performance_metrics()
        insights["system_health"] = {
            "status": performance_metrics["system_status"],
            "response_time_ms": performance_metrics["average_response_time_ms"],
            "cache_hit_rate": performance_metrics["cache_hit_rate"],
            "error_rate": performance_metrics["error_rate"]
        }
        
        # Real-time anomaly detection
        if system_context.get("metrics"):
            anomaly_insight = await self.generate_ai_insight(
                AITaskType.ANOMALY_DETECTION,
                {"system_metrics": system_context["metrics"]}
            )
            insights["anomalies"] = anomaly_insight.supporting_data.get("anomalies", [])
        
        # Real-time recommendations
        if performance_metrics["average_response_time_ms"] > 1000:
            insights["recommendations"].append("Consider scaling AI processing resources")
        
        if performance_metrics["cache_hit_rate"] < 50:
            insights["recommendations"].append("Optimize caching strategy for better performance")
        
        return insights

# Export main service class
__all__ = [
    "UnifiedPyBrainService",
    "AITaskType",
    "AIConfidenceLevel",
    "CulturalContext",
    "AIInsight",
    "WorkflowOptimization",
    "AnomalyDetection",
    "PredictiveAnalytics"
]