"""
BrainSAIT Healthcare Insurance Data Analysis Module

This module provides comprehensive insurance claim processing and analysis capabilities
for the BrainSAIT unified healthcare ecosystem.

Components:
- insurance_data_extractor: Excel/PDF data extraction utilities
- claim_analysis_engine: Claims processing and analysis
- trend_analyzer: Trend analysis and comparison
- rejection_pattern_detector: Rejection pattern identification
- financial_impact_calculator: Financial analysis and calculations
- recommendation_engine: Best practice recommendations
"""

from .insurance_data_extractor import InsuranceDataExtractor
from .claim_analysis_engine import ClaimAnalysisEngine
from .trend_analyzer import TrendAnalyzer
from .rejection_pattern_detector import RejectionPatternDetector
from .financial_impact_calculator import FinancialImpactCalculator
from .recommendation_engine import RecommendationEngine

__all__ = [
    'InsuranceDataExtractor',
    'ClaimAnalysisEngine', 
    'TrendAnalyzer',
    'RejectionPatternDetector',
    'FinancialImpactCalculator',
    'RecommendationEngine'
]