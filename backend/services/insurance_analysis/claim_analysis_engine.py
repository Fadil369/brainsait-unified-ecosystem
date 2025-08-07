"""
Claim Analysis Engine

Processes insurance claims data and performs comprehensive analysis including
categorization, status tracking, and pattern identification.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

class ClaimAnalysisEngine:
    """
    Analyzes insurance claims data to provide insights on approval patterns,
    processing times, and claim characteristics.
    """
    
    def __init__(self):
        self.claim_statuses = ['approved', 'rejected', 'pending', 'under_review']
        self.claim_types = ['inpatient', 'outpatient', 'emergency', 'preventive', 'diagnostic']
        
    async def analyze_claims_data(self, claims_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of claims data.
        
        Args:
            claims_data: List of claim records
            
        Returns:
            Analysis results with metrics and insights
        """
        try:
            if not claims_data:
                return {'success': False, 'error': 'No claims data provided'}
            
            df = pd.DataFrame(claims_data)
            
            # Basic statistics
            basic_stats = await self._calculate_basic_statistics(df)
            
            # Status analysis
            status_analysis = await self._analyze_claim_status(df)
            
            # Amount analysis
            amount_analysis = await self._analyze_claim_amounts(df)
            
            # Time-based analysis
            time_analysis = await self._analyze_processing_times(df)
            
            # Provider analysis
            provider_analysis = await self._analyze_provider_performance(df)
            
            return {
                'success': True,
                'analysis_date': datetime.now().isoformat(),
                'total_claims': len(df),
                'basic_statistics': basic_stats,
                'status_analysis': status_analysis,
                'amount_analysis': amount_analysis,
                'time_analysis': time_analysis,
                'provider_analysis': provider_analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing claims data: {str(e)}")
            return {'success': False, 'error': 'An internal error occurred during claims analysis.'}
    
    async def _calculate_basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic statistical measures."""
        stats = {
            'total_claims': len(df),
            'date_range': {},
            'status_distribution': {},
            'average_processing_time': None
        }
        
        # Date range analysis
        if 'claim_date' in df.columns:
            df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')
            valid_dates = df['claim_date'].dropna()
            if len(valid_dates) > 0:
                stats['date_range'] = {
                    'earliest': valid_dates.min().isoformat(),
                    'latest': valid_dates.max().isoformat(),
                    'span_days': (valid_dates.max() - valid_dates.min()).days
                }
        
        # Status distribution
        if 'status' in df.columns:
            status_counts = df['status'].value_counts().to_dict()
            total = len(df)
            stats['status_distribution'] = {
                status: {'count': count, 'percentage': round(count/total*100, 2)}
                for status, count in status_counts.items()
            }
        
        return stats
    
    async def _analyze_claim_status(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze claim status patterns."""
        analysis = {
            'approval_rate': 0.0,
            'rejection_rate': 0.0,
            'pending_rate': 0.0,
            'top_rejection_reasons': []
        }
        
        if 'status' in df.columns:
            status_counts = df['status'].value_counts()
            total = len(df)
            
            # Calculate rates
            analysis['approval_rate'] = round(status_counts.get('approved', 0) / total * 100, 2)
            analysis['rejection_rate'] = round(status_counts.get('rejected', 0) / total * 100, 2)
            analysis['pending_rate'] = round(status_counts.get('pending', 0) / total * 100, 2)
            
        # Top rejection reasons
        if 'rejection_reason' in df.columns:
            rejected_claims = df[df['status'] == 'rejected']
            if len(rejected_claims) > 0:
                reason_counts = rejected_claims['rejection_reason'].value_counts().head(10)
                analysis['top_rejection_reasons'] = [
                    {'reason': reason, 'count': count, 'percentage': round(count/len(rejected_claims)*100, 2)}
                    for reason, count in reason_counts.items()
                ]
        
        return analysis
    
    async def _analyze_claim_amounts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze claim amount patterns."""
        analysis = {
            'total_amount': 0.0,
            'average_amount': 0.0,
            'median_amount': 0.0,
            'amount_distribution': {},
            'high_value_claims': []
        }
        
        if 'claim_amount' in df.columns:
            amounts = pd.to_numeric(df['claim_amount'], errors='coerce').dropna()
            
            if len(amounts) > 0:
                analysis['total_amount'] = round(amounts.sum(), 2)
                analysis['average_amount'] = round(amounts.mean(), 2)
                analysis['median_amount'] = round(amounts.median(), 2)
                
                # Amount distribution by ranges
                amount_ranges = [
                    (0, 1000, 'Low (0-1K)'),
                    (1000, 5000, 'Medium (1K-5K)'),
                    (5000, 10000, 'High (5K-10K)'),
                    (10000, float('inf'), 'Very High (10K+)')
                ]
                
                for min_val, max_val, label in amount_ranges:
                    count = len(amounts[(amounts >= min_val) & (amounts < max_val)])
                    analysis['amount_distribution'][label] = {
                        'count': count,
                        'percentage': round(count/len(amounts)*100, 2)
                    }
                
                # High value claims (top 5%)
                high_value_threshold = amounts.quantile(0.95)
                high_value_claims = df[pd.to_numeric(df['claim_amount'], errors='coerce') >= high_value_threshold]
                analysis['high_value_claims'] = {
                    'threshold': round(high_value_threshold, 2),
                    'count': len(high_value_claims),
                    'total_amount': round(pd.to_numeric(high_value_claims['claim_amount'], errors='coerce').sum(), 2)
                }
        
        return analysis
    
    async def _analyze_processing_times(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze claim processing time patterns."""
        analysis = {
            'average_processing_days': None,
            'median_processing_days': None,
            'processing_time_distribution': {},
            'delayed_claims': []
        }
        
        # Calculate processing times if we have both submission and processing dates
        if 'claim_date' in df.columns and 'processing_date' in df.columns:
            df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')
            df['processing_date'] = pd.to_datetime(df['processing_date'], errors='coerce')
            
            # Calculate processing time in days
            processing_times = (df['processing_date'] - df['claim_date']).dt.days
            valid_times = processing_times.dropna()
            
            if len(valid_times) > 0:
                analysis['average_processing_days'] = round(valid_times.mean(), 1)
                analysis['median_processing_days'] = round(valid_times.median(), 1)
                
                # Processing time distribution
                time_ranges = [
                    (0, 7, 'Fast (0-7 days)'),
                    (7, 14, 'Normal (7-14 days)'),
                    (14, 30, 'Slow (14-30 days)'),
                    (30, float('inf'), 'Very Slow (30+ days)')
                ]
                
                for min_val, max_val, label in time_ranges:
                    count = len(valid_times[(valid_times >= min_val) & (valid_times < max_val)])
                    analysis['processing_time_distribution'][label] = {
                        'count': count,
                        'percentage': round(count/len(valid_times)*100, 2)
                    }
                
                # Delayed claims (over 30 days)
                delayed_threshold = 30
                delayed_claims = df[processing_times > delayed_threshold]
                analysis['delayed_claims'] = {
                    'count': len(delayed_claims),
                    'percentage': round(len(delayed_claims)/len(df)*100, 2),
                    'average_delay': round(processing_times[processing_times > delayed_threshold].mean(), 1) if len(delayed_claims) > 0 else 0
                }
        
        return analysis
    
    async def _analyze_provider_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by provider."""
        analysis = {
            'total_providers': 0,
            'top_providers': [],
            'provider_approval_rates': []
        }
        
        if 'provider_id' in df.columns:
            provider_stats = df.groupby('provider_id').agg({
                'claim_id': 'count',
                'claim_amount': 'sum',
                'status': lambda x: (x == 'approved').sum()
            }).reset_index()
            
            provider_stats.columns = ['provider_id', 'total_claims', 'total_amount', 'approved_claims']
            provider_stats['approval_rate'] = (provider_stats['approved_claims'] / provider_stats['total_claims'] * 100).round(2)
            
            analysis['total_providers'] = len(provider_stats)
            
            # Top providers by claim volume
            top_by_volume = provider_stats.nlargest(10, 'total_claims')
            analysis['top_providers'] = [
                {
                    'provider_id': row['provider_id'],
                    'total_claims': int(row['total_claims']),
                    'total_amount': round(row['total_amount'], 2),
                    'approval_rate': row['approval_rate']
                }
                for _, row in top_by_volume.iterrows()
            ]
            
            # Provider approval rates (for providers with at least 10 claims)
            qualified_providers = provider_stats[provider_stats['total_claims'] >= 10]
            analysis['provider_approval_rates'] = {
                'average': round(qualified_providers['approval_rate'].mean(), 2),
                'median': round(qualified_providers['approval_rate'].median(), 2),
                'best_performers': qualified_providers.nlargest(5, 'approval_rate')[['provider_id', 'approval_rate']].to_dict('records'),
                'poor_performers': qualified_providers.nsmallest(5, 'approval_rate')[['provider_id', 'approval_rate']].to_dict('records')
            }
        
        return analysis
    
    async def generate_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from analysis results."""
        insights = []
        
        if not analysis_results.get('success'):
            return ['Unable to generate insights due to analysis errors.']
        
        # Approval rate insights
        status_analysis = analysis_results.get('status_analysis', {})
        approval_rate = status_analysis.get('approval_rate', 0)
        
        if approval_rate < 70:
            insights.append(f"Low approval rate ({approval_rate}%) indicates potential issues with claim quality or documentation.")
        elif approval_rate > 90:
            insights.append(f"High approval rate ({approval_rate}%) suggests good claim quality and compliance.")
        
        # Processing time insights
        time_analysis = analysis_results.get('time_analysis', {})
        avg_processing = time_analysis.get('average_processing_days')
        if avg_processing and avg_processing > 14:
            insights.append(f"Average processing time ({avg_processing} days) exceeds industry standards.")
        
        # Amount insights
        amount_analysis = analysis_results.get('amount_analysis', {})
        high_value_claims = amount_analysis.get('high_value_claims', {})
        if high_value_claims.get('count', 0) > 0:
            insights.append(f"Monitor {high_value_claims['count']} high-value claims for potential audit requirements.")
        
        # Top rejection reasons
        top_rejections = status_analysis.get('top_rejection_reasons', [])
        if top_rejections:
            top_reason = top_rejections[0]
            insights.append(f"Address primary rejection reason: '{top_reason['reason']}' ({top_reason['percentage']}% of rejections).")
        
        return insights