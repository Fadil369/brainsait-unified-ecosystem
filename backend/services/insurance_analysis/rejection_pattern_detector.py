"""
Rejection Pattern Detector

Identifies patterns in claim rejections to help improve approval rates
and reduce future rejections through targeted improvements.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re

logger = logging.getLogger(__name__)

class RejectionPatternDetector:
    """
    Analyzes rejection patterns in insurance claims to identify
    common causes and suggest improvements.
    """
    
    def __init__(self):
        self.common_rejection_categories = {
            'documentation': ['missing document', 'incomplete form', 'invalid signature'],
            'eligibility': ['not covered', 'policy expired', 'out of network'],
            'medical_necessity': ['not medically necessary', 'experimental', 'cosmetic'],
            'coding': ['invalid code', 'wrong diagnosis', 'unbundling'],
            'administrative': ['duplicate claim', 'timely filing', 'prior authorization']
        }
        
    async def detect_rejection_patterns(self, claims_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze rejection patterns in claims data.
        
        Args:
            claims_data: List of claim records with rejection information
            
        Returns:
            Analysis of rejection patterns and recommendations
        """
        try:
            if not claims_data:
                return {'success': False, 'error': 'No claims data provided'}
            
            df = pd.DataFrame(claims_data)
            
            # Filter to rejected claims only
            rejected_claims = df[df['status'] == 'rejected'].copy()
            
            if rejected_claims.empty:
                return {
                    'success': True,
                    'message': 'No rejected claims found',
                    'rejection_rate': 0.0,
                    'patterns': []
                }
            
            # Basic rejection statistics
            rejection_stats = await self._calculate_rejection_statistics(df, rejected_claims)
            
            # Categorize rejection reasons
            categorized_rejections = await self._categorize_rejections(rejected_claims)
            
            # Identify temporal patterns
            temporal_patterns = await self._analyze_temporal_patterns(rejected_claims)
            
            # Provider-specific patterns
            provider_patterns = await self._analyze_provider_patterns(rejected_claims)
            
            # Amount-based patterns
            amount_patterns = await self._analyze_amount_patterns(rejected_claims)
            
            # Root cause analysis
            root_causes = await self._identify_root_causes(categorized_rejections, rejected_claims)
            
            # Generate improvement recommendations
            recommendations = await self._generate_recommendations(
                categorized_rejections, provider_patterns, root_causes
            )
            
            return {
                'success': True,
                'analysis_date': datetime.now().isoformat(),
                'rejection_statistics': rejection_stats,
                'categorized_rejections': categorized_rejections,
                'temporal_patterns': temporal_patterns,
                'provider_patterns': provider_patterns,
                'amount_patterns': amount_patterns,
                'root_causes': root_causes,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error detecting rejection patterns: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _calculate_rejection_statistics(self, all_claims: pd.DataFrame, rejected_claims: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic rejection statistics."""
        total_claims = len(all_claims)
        total_rejected = len(rejected_claims)
        
        stats = {
            'total_claims': total_claims,
            'total_rejected': total_rejected,
            'rejection_rate': round((total_rejected / total_claims) * 100, 2) if total_claims > 0 else 0,
            'rejected_amount': 0.0,
            'average_rejected_amount': 0.0
        }
        
        # Calculate financial impact
        if 'claim_amount' in rejected_claims.columns:
            rejected_amounts = pd.to_numeric(rejected_claims['claim_amount'], errors='coerce').dropna()
            if len(rejected_amounts) > 0:
                stats['rejected_amount'] = round(rejected_amounts.sum(), 2)
                stats['average_rejected_amount'] = round(rejected_amounts.mean(), 2)
        
        return stats
    
    async def _categorize_rejections(self, rejected_claims: pd.DataFrame) -> Dict[str, Any]:
        """Categorize rejections by reason type."""
        categorized = {
            'by_category': defaultdict(int),
            'detailed_reasons': [],
            'uncategorized_reasons': []
        }
        
        if 'rejection_reason' not in rejected_claims.columns:
            return categorized
        
        # Count rejection reasons
        reason_counts = rejected_claims['rejection_reason'].value_counts()
        
        for reason, count in reason_counts.items():
            if pd.isna(reason) or reason == '':
                continue
                
            reason_lower = str(reason).lower()
            category_found = False
            
            # Try to categorize the reason
            for category, keywords in self.common_rejection_categories.items():
                if any(keyword in reason_lower for keyword in keywords):
                    categorized['by_category'][category] += count
                    category_found = True
                    break
            
            # Add to detailed reasons
            categorized['detailed_reasons'].append({
                'reason': reason,
                'count': int(count),
                'percentage': round((count / len(rejected_claims)) * 100, 2)
            })
            
            # Track uncategorized reasons
            if not category_found:
                categorized['uncategorized_reasons'].append({
                    'reason': reason,
                    'count': int(count)
                })
        
        # Convert defaultdict to regular dict
        categorized['by_category'] = dict(categorized['by_category'])
        
        # Sort detailed reasons by count
        categorized['detailed_reasons'].sort(key=lambda x: x['count'], reverse=True)
        
        return categorized
    
    async def _analyze_temporal_patterns(self, rejected_claims: pd.DataFrame) -> Dict[str, Any]:
        """Analyze rejection patterns over time."""
        patterns = {
            'monthly_trends': [],
            'day_of_week_patterns': {},
            'seasonal_patterns': {}
        }
        
        if 'claim_date' not in rejected_claims.columns:
            return patterns
        
        # Convert dates
        rejected_claims['claim_date'] = pd.to_datetime(rejected_claims['claim_date'], errors='coerce')
        valid_dates = rejected_claims.dropna(subset=['claim_date'])
        
        if valid_dates.empty:
            return patterns
        
        # Monthly trends
        monthly_rejections = valid_dates.groupby(valid_dates['claim_date'].dt.to_period('M')).size()
        patterns['monthly_trends'] = [
            {'month': str(month), 'rejection_count': int(count)}
            for month, count in monthly_rejections.items()
        ]
        
        # Day of week patterns
        dow_rejections = valid_dates['claim_date'].dt.day_name().value_counts()
        patterns['day_of_week_patterns'] = {
            day: int(count) for day, count in dow_rejections.items()
        }
        
        # Find peak rejection days
        if dow_rejections.count() > 0:
            peak_day = dow_rejections.index[0]
            patterns['peak_rejection_day'] = {
                'day': peak_day,
                'count': int(dow_rejections.iloc[0])
            }
        
        return patterns
    
    async def _analyze_provider_patterns(self, rejected_claims: pd.DataFrame) -> Dict[str, Any]:
        """Analyze rejection patterns by provider."""
        patterns = {
            'high_rejection_providers': [],
            'provider_specific_reasons': {},
            'provider_rejection_rates': {}
        }
        
        if 'provider_id' not in rejected_claims.columns:
            return patterns
        
        # Provider rejection counts
        provider_rejections = rejected_claims['provider_id'].value_counts()
        
        # Get providers with high rejection counts (top 10)
        high_rejection_providers = provider_rejections.head(10)
        patterns['high_rejection_providers'] = [
            {'provider_id': provider, 'rejection_count': int(count)}
            for provider, count in high_rejection_providers.items()
        ]
        
        # Provider-specific rejection reasons
        if 'rejection_reason' in rejected_claims.columns:
            for provider in high_rejection_providers.index[:5]:  # Top 5 providers
                provider_data = rejected_claims[rejected_claims['provider_id'] == provider]
                reason_counts = provider_data['rejection_reason'].value_counts().head(3)
                
                patterns['provider_specific_reasons'][provider] = [
                    {'reason': reason, 'count': int(count)}
                    for reason, count in reason_counts.items()
                ]
        
        return patterns
    
    async def _analyze_amount_patterns(self, rejected_claims: pd.DataFrame) -> Dict[str, Any]:
        """Analyze rejection patterns by claim amount."""
        patterns = {
            'amount_distribution': {},
            'high_value_rejections': {},
            'amount_vs_reason_correlation': []
        }
        
        if 'claim_amount' not in rejected_claims.columns:
            return patterns
        
        amounts = pd.to_numeric(rejected_claims['claim_amount'], errors='coerce').dropna()
        
        if amounts.empty:
            return patterns
        
        # Amount distribution of rejected claims
        amount_ranges = [
            (0, 1000, 'Low (0-1K)'),
            (1000, 5000, 'Medium (1K-5K)'),
            (5000, 10000, 'High (5K-10K)'),
            (10000, float('inf'), 'Very High (10K+)')
        ]
        
        for min_val, max_val, label in amount_ranges:
            count = len(amounts[(amounts >= min_val) & (amounts < max_val)])
            patterns['amount_distribution'][label] = {
                'count': count,
                'percentage': round(count/len(amounts)*100, 2) if len(amounts) > 0 else 0
            }
        
        # High value rejections analysis
        high_value_threshold = amounts.quantile(0.9)  # Top 10%
        high_value_rejections = rejected_claims[
            pd.to_numeric(rejected_claims['claim_amount'], errors='coerce') >= high_value_threshold
        ]
        
        patterns['high_value_rejections'] = {
            'threshold': round(high_value_threshold, 2),
            'count': len(high_value_rejections),
            'total_amount': round(pd.to_numeric(high_value_rejections['claim_amount'], errors='coerce').sum(), 2),
            'average_amount': round(pd.to_numeric(high_value_rejections['claim_amount'], errors='coerce').mean(), 2)
        }
        
        return patterns
    
    async def _identify_root_causes(
        self, 
        categorized_rejections: Dict[str, Any], 
        rejected_claims: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Identify root causes of rejections."""
        root_causes = []
        
        # Analyze top rejection categories
        categories = categorized_rejections.get('by_category', {})
        total_rejections = sum(categories.values()) if categories else 0
        
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = round((count / total_rejections) * 100, 2)
                
                # Determine severity and impact
                if percentage > 30:
                    severity = 'high'
                    impact = 'critical'
                elif percentage > 15:
                    severity = 'medium'
                    impact = 'significant'
                else:
                    severity = 'low'
                    impact = 'moderate'
                
                root_causes.append({
                    'category': category,
                    'count': count,
                    'percentage': percentage,
                    'severity': severity,
                    'impact': impact,
                    'description': await self._get_category_description(category)
                })
        
        return root_causes
    
    async def _get_category_description(self, category: str) -> str:
        """Get description for rejection category."""
        descriptions = {
            'documentation': 'Missing or incomplete documentation and forms',
            'eligibility': 'Patient eligibility and coverage issues',
            'medical_necessity': 'Medical necessity and treatment appropriateness',
            'coding': 'Medical coding and billing errors',
            'administrative': 'Administrative and process-related issues'
        }
        return descriptions.get(category, f'Issues related to {category}')
    
    async def _generate_recommendations(
        self,
        categorized_rejections: Dict[str, Any],
        provider_patterns: Dict[str, Any],
        root_causes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations to reduce rejections."""
        recommendations = []
        
        # Recommendations based on root causes
        for cause in root_causes:
            category = cause['category']
            
            if category == 'documentation' and cause['severity'] == 'high':
                recommendations.append({
                    'priority': 'high',
                    'category': 'process_improvement',
                    'title': 'Implement Documentation Quality Control',
                    'description': 'Establish pre-submission documentation review process',
                    'expected_impact': f"Could reduce rejections by up to {cause['percentage']:.1f}%",
                    'implementation_effort': 'medium'
                })
            
            elif category == 'coding' and cause['severity'] in ['high', 'medium']:
                recommendations.append({
                    'priority': 'high',
                    'category': 'training',
                    'title': 'Enhanced Medical Coding Training',
                    'description': 'Provide additional training on proper coding practices',
                    'expected_impact': f"Could reduce coding-related rejections by {cause['percentage']:.1f}%",
                    'implementation_effort': 'low'
                })
            
            elif category == 'eligibility' and cause['severity'] == 'high':
                recommendations.append({
                    'priority': 'medium',
                    'category': 'technology',
                    'title': 'Real-time Eligibility Verification',
                    'description': 'Implement automated eligibility checking before claim submission',
                    'expected_impact': f"Could prevent {cause['percentage']:.1f}% of eligibility-related rejections",
                    'implementation_effort': 'high'
                })
        
        # Provider-specific recommendations
        high_rejection_providers = provider_patterns.get('high_rejection_providers', [])
        if len(high_rejection_providers) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'provider_support',
                'title': 'Targeted Provider Education',
                'description': f'Focus on top {len(high_rejection_providers)} providers with high rejection rates',
                'expected_impact': 'Reduce overall rejection rate by 10-15%',
                'implementation_effort': 'medium'
            })
        
        # General recommendations
        total_detailed_reasons = len(categorized_rejections.get('detailed_reasons', []))
        if total_detailed_reasons > 10:
            recommendations.append({
                'priority': 'low',
                'category': 'analytics',
                'title': 'Advanced Rejection Analytics',
                'description': 'Implement machine learning for rejection prediction and prevention',
                'expected_impact': 'Proactive identification of potential rejections',
                'implementation_effort': 'high'
            })
        
        # Sort recommendations by priority
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return recommendations