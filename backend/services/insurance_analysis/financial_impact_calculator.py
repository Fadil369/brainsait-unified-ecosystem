"""
Financial Impact Calculator

Calculates financial impacts and metrics for insurance claims analysis,
including cost savings opportunities and revenue optimization.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class FinancialImpactCalculator:
    """
    Calculates financial metrics and impact analysis for insurance claims data.
    Provides insights on revenue optimization and cost savings opportunities.
    """
    
    def __init__(self):
        self.default_processing_cost = 50.0  # Default cost per claim processing
        self.default_appeal_cost = 200.0     # Default cost per appeal
        
    async def calculate_financial_impact(self, claims_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive financial impact analysis.
        
        Args:
            claims_data: List of claim records
            
        Returns:
            Financial impact analysis with metrics and opportunities
        """
        try:
            if not claims_data:
                return {'success': False, 'error': 'No claims data provided'}
            
            df = pd.DataFrame(claims_data)
            
            # Basic financial metrics
            basic_metrics = await self._calculate_basic_metrics(df)
            
            # Revenue analysis
            revenue_analysis = await self._analyze_revenue_impact(df)
            
            # Cost analysis
            cost_analysis = await self._analyze_cost_impact(df)
            
            # Rejection financial impact
            rejection_impact = await self._calculate_rejection_impact(df)
            
            # Processing efficiency metrics
            efficiency_metrics = await self._calculate_efficiency_metrics(df)
            
            # Opportunities for improvement
            opportunities = await self._identify_opportunities(df, basic_metrics, rejection_impact)
            
            # ROI calculations for potential improvements
            roi_analysis = await self._calculate_improvement_roi(opportunities, basic_metrics)
            
            return {
                'success': True,
                'analysis_date': datetime.now().isoformat(),
                'basic_metrics': basic_metrics,
                'revenue_analysis': revenue_analysis,
                'cost_analysis': cost_analysis,
                'rejection_impact': rejection_impact,
                'efficiency_metrics': efficiency_metrics,
                'opportunities': opportunities,
                'roi_analysis': roi_analysis
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial impact: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _calculate_basic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic financial metrics."""
        metrics = {
            'total_claims': len(df),
            'total_claimed_amount': 0.0,
            'total_approved_amount': 0.0,
            'total_rejected_amount': 0.0,
            'average_claim_amount': 0.0,
            'approval_rate': 0.0,
            'financial_approval_rate': 0.0
        }
        
        # Calculate amounts
        if 'claim_amount' in df.columns:
            claim_amounts = pd.to_numeric(df['claim_amount'], errors='coerce').dropna()
            metrics['total_claimed_amount'] = round(claim_amounts.sum(), 2)
            metrics['average_claim_amount'] = round(claim_amounts.mean(), 2) if len(claim_amounts) > 0 else 0
        
        # Calculate approved amounts
        approved_claims = df[df['status'] == 'approved']
        if len(approved_claims) > 0 and 'claim_amount' in approved_claims.columns:
            approved_amounts = pd.to_numeric(approved_claims['claim_amount'], errors='coerce').dropna()
            metrics['total_approved_amount'] = round(approved_amounts.sum(), 2)
        
        # Calculate rejected amounts
        rejected_claims = df[df['status'] == 'rejected']
        if len(rejected_claims) > 0 and 'claim_amount' in rejected_claims.columns:
            rejected_amounts = pd.to_numeric(rejected_claims['claim_amount'], errors='coerce').dropna()
            metrics['total_rejected_amount'] = round(rejected_amounts.sum(), 2)
        
        # Calculate rates
        if len(df) > 0:
            metrics['approval_rate'] = round((len(approved_claims) / len(df)) * 100, 2)
            
            if metrics['total_claimed_amount'] > 0:
                metrics['financial_approval_rate'] = round(
                    (metrics['total_approved_amount'] / metrics['total_claimed_amount']) * 100, 2
                )
        
        return metrics
    
    async def _analyze_revenue_impact(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze revenue impact and patterns."""
        analysis = {
            'monthly_revenue': [],
            'revenue_by_provider': [],
            'revenue_by_claim_type': {},
            'revenue_trends': {}
        }
        
        if 'claim_amount' not in df.columns:
            return analysis
        
        # Monthly revenue analysis
        if 'claim_date' in df.columns:
            df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')
            approved_claims = df[df['status'] == 'approved'].copy()
            
            if not approved_claims.empty:
                monthly_revenue = approved_claims.groupby(
                    approved_claims['claim_date'].dt.to_period('M')
                )['claim_amount'].apply(lambda x: pd.to_numeric(x, errors='coerce').sum())
                
                analysis['monthly_revenue'] = [
                    {'month': str(month), 'revenue': round(revenue, 2)}
                    for month, revenue in monthly_revenue.items()
                ]
        
        # Revenue by provider
        if 'provider_id' in df.columns:
            approved_claims = df[df['status'] == 'approved']
            provider_revenue = approved_claims.groupby('provider_id')['claim_amount'].apply(
                lambda x: pd.to_numeric(x, errors='coerce').sum()
            ).nlargest(10)
            
            analysis['revenue_by_provider'] = [
                {'provider_id': provider, 'revenue': round(revenue, 2)}
                for provider, revenue in provider_revenue.items()
            ]
        
        # Revenue trends
        if len(analysis['monthly_revenue']) >= 2:
            revenues = [item['revenue'] for item in analysis['monthly_revenue']]
            recent_change = ((revenues[-1] - revenues[-2]) / revenues[-2]) * 100 if revenues[-2] != 0 else 0
            
            analysis['revenue_trends'] = {
                'recent_month_change_percent': round(recent_change, 2),
                'total_change_percent': round(((revenues[-1] - revenues[0]) / revenues[0]) * 100, 2) if revenues[0] != 0 else 0,
                'average_monthly_revenue': round(np.mean(revenues), 2)
            }
        
        return analysis
    
    async def _analyze_cost_impact(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cost impacts of claims processing."""
        analysis = {
            'processing_costs': {},
            'appeal_costs': {},
            'rework_costs': {},
            'total_operational_costs': 0.0
        }
        
        total_claims = len(df)
        rejected_claims = len(df[df['status'] == 'rejected'])
        
        # Processing costs
        total_processing_cost = total_claims * self.default_processing_cost
        analysis['processing_costs'] = {
            'cost_per_claim': self.default_processing_cost,
            'total_claims': total_claims,
            'total_processing_cost': round(total_processing_cost, 2)
        }
        
        # Appeal costs (assume 30% of rejections result in appeals)
        estimated_appeals = int(rejected_claims * 0.3)
        total_appeal_cost = estimated_appeals * self.default_appeal_cost
        analysis['appeal_costs'] = {
            'cost_per_appeal': self.default_appeal_cost,
            'estimated_appeals': estimated_appeals,
            'total_appeal_cost': round(total_appeal_cost, 2)
        }
        
        # Rework costs (reprocessing rejected claims)
        rework_cost = rejected_claims * (self.default_processing_cost * 0.5)  # 50% of processing cost
        analysis['rework_costs'] = {
            'rejected_claims': rejected_claims,
            'cost_per_rework': round(self.default_processing_cost * 0.5, 2),
            'total_rework_cost': round(rework_cost, 2)
        }
        
        # Total operational costs
        analysis['total_operational_costs'] = round(
            total_processing_cost + total_appeal_cost + rework_cost, 2
        )
        
        return analysis
    
    async def _calculate_rejection_impact(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate financial impact of claim rejections."""
        impact = {
            'direct_revenue_loss': 0.0,
            'processing_waste': 0.0,
            'opportunity_cost': 0.0,
            'total_rejection_cost': 0.0,
            'cost_per_rejection': 0.0
        }
        
        rejected_claims = df[df['status'] == 'rejected']
        
        if rejected_claims.empty:
            return impact
        
        # Direct revenue loss
        if 'claim_amount' in rejected_claims.columns:
            rejected_amounts = pd.to_numeric(rejected_claims['claim_amount'], errors='coerce').dropna()
            impact['direct_revenue_loss'] = round(rejected_amounts.sum(), 2)
        
        # Processing waste (cost of processing claims that were rejected)
        processing_waste = len(rejected_claims) * self.default_processing_cost
        impact['processing_waste'] = round(processing_waste, 2)
        
        # Opportunity cost (time and resources that could have been used elsewhere)
        # Assume 20% additional cost for opportunity loss
        opportunity_cost = processing_waste * 0.2
        impact['opportunity_cost'] = round(opportunity_cost, 2)
        
        # Total rejection cost
        impact['total_rejection_cost'] = round(
            impact['processing_waste'] + impact['opportunity_cost'], 2
        )
        
        # Cost per rejection
        if len(rejected_claims) > 0:
            impact['cost_per_rejection'] = round(
                impact['total_rejection_cost'] / len(rejected_claims), 2
            )
        
        return impact
    
    async def _calculate_efficiency_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate processing efficiency metrics."""
        metrics = {
            'claims_per_day': 0.0,
            'revenue_per_day': 0.0,
            'processing_efficiency': 0.0,
            'cost_effectiveness': 0.0
        }
        
        if 'claim_date' not in df.columns:
            return metrics
        
        df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')
        valid_dates = df.dropna(subset=['claim_date'])
        
        if valid_dates.empty:
            return metrics
        
        # Calculate date range
        date_range = (valid_dates['claim_date'].max() - valid_dates['claim_date'].min()).days
        
        if date_range > 0:
            # Claims per day
            metrics['claims_per_day'] = round(len(valid_dates) / date_range, 2)
            
            # Revenue per day
            approved_claims = valid_dates[valid_dates['status'] == 'approved']
            if not approved_claims.empty and 'claim_amount' in approved_claims.columns:
                total_revenue = pd.to_numeric(approved_claims['claim_amount'], errors='coerce').sum()
                metrics['revenue_per_day'] = round(total_revenue / date_range, 2)
            
            # Processing efficiency (approved claims / total claims)
            if len(valid_dates) > 0:
                metrics['processing_efficiency'] = round(
                    (len(approved_claims) / len(valid_dates)) * 100, 2
                )
            
            # Cost effectiveness (revenue / operational cost)
            total_operational_cost = len(valid_dates) * self.default_processing_cost
            if total_operational_cost > 0 and metrics['revenue_per_day'] > 0:
                total_revenue = metrics['revenue_per_day'] * date_range
                metrics['cost_effectiveness'] = round(total_revenue / total_operational_cost, 2)
        
        return metrics
    
    async def _identify_opportunities(
        self, 
        df: pd.DataFrame, 
        basic_metrics: Dict[str, Any],
        rejection_impact: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify financial improvement opportunities."""
        opportunities = []
        
        # Low approval rate opportunity
        approval_rate = basic_metrics.get('approval_rate', 0)
        if approval_rate < 80:
            potential_revenue = rejection_impact.get('direct_revenue_loss', 0)
            opportunities.append({
                'type': 'approval_rate_improvement',
                'description': f'Improve approval rate from {approval_rate}% to 85%',
                'potential_revenue_gain': round(potential_revenue * 0.25, 2),  # 25% improvement
                'implementation_effort': 'medium',
                'timeframe_months': 6
            })
        
        # High-value rejection opportunity
        if 'claim_amount' in df.columns:
            rejected_high_value = df[
                (df['status'] == 'rejected') & 
                (pd.to_numeric(df['claim_amount'], errors='coerce') > 5000)
            ]
            
            if len(rejected_high_value) > 0:
                high_value_loss = pd.to_numeric(rejected_high_value['claim_amount'], errors='coerce').sum()
                opportunities.append({
                    'type': 'high_value_claim_focus',
                    'description': f'Focus on {len(rejected_high_value)} high-value rejected claims',
                    'potential_revenue_gain': round(high_value_loss * 0.4, 2),  # 40% recovery
                    'implementation_effort': 'low',
                    'timeframe_months': 3
                })
        
        # Processing efficiency opportunity
        processing_waste = rejection_impact.get('processing_waste', 0)
        if processing_waste > 10000:  # Significant processing waste
            opportunities.append({
                'type': 'processing_efficiency',
                'description': 'Implement pre-submission validation to reduce processing waste',
                'potential_cost_savings': round(processing_waste * 0.3, 2),  # 30% reduction
                'implementation_effort': 'high',
                'timeframe_months': 9
            })
        
        # Provider performance opportunity
        if 'provider_id' in df.columns:
            provider_performance = df.groupby('provider_id').agg({
                'status': lambda x: (x == 'approved').mean(),
                'claim_amount': lambda x: pd.to_numeric(x, errors='coerce').sum()
            })
            
            poor_performers = provider_performance[provider_performance['status'] < 0.6]  # <60% approval
            if len(poor_performers) > 0:
                potential_improvement = poor_performers['claim_amount'].sum() * 0.2  # 20% improvement
                opportunities.append({
                    'type': 'provider_education',
                    'description': f'Target education for {len(poor_performers)} underperforming providers',
                    'potential_revenue_gain': round(potential_improvement, 2),
                    'implementation_effort': 'medium',
                    'timeframe_months': 4
                })
        
        return opportunities
    
    async def _calculate_improvement_roi(
        self, 
        opportunities: List[Dict[str, Any]], 
        basic_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate ROI for improvement opportunities."""
        roi_analysis = {
            'total_potential_gain': 0.0,
            'total_potential_savings': 0.0,
            'opportunity_roi': [],
            'implementation_priorities': []
        }
        
        for opportunity in opportunities:
            revenue_gain = opportunity.get('potential_revenue_gain', 0)
            cost_savings = opportunity.get('potential_cost_savings', 0)
            total_benefit = revenue_gain + cost_savings
            
            # Estimate implementation cost based on effort
            effort = opportunity.get('implementation_effort', 'medium')
            if effort == 'low':
                implementation_cost = 5000
            elif effort == 'medium':
                implementation_cost = 15000
            else:  # high
                implementation_cost = 50000
            
            # Calculate ROI
            roi = ((total_benefit - implementation_cost) / implementation_cost) * 100 if implementation_cost > 0 else 0
            
            roi_analysis['opportunity_roi'].append({
                'type': opportunity['type'],
                'total_benefit': round(total_benefit, 2),
                'implementation_cost': implementation_cost,
                'roi_percent': round(roi, 1),
                'payback_months': round(implementation_cost / (total_benefit / 12), 1) if total_benefit > 0 else float('inf')
            })
            
            roi_analysis['total_potential_gain'] += revenue_gain
            roi_analysis['total_potential_savings'] += cost_savings
        
        # Sort opportunities by ROI for implementation priority
        roi_analysis['opportunity_roi'].sort(key=lambda x: x['roi_percent'], reverse=True)
        
        # Create implementation priority list
        for i, item in enumerate(roi_analysis['opportunity_roi']):
            priority = 'high' if i < 2 else 'medium' if i < 4 else 'low'
            roi_analysis['implementation_priorities'].append({
                'priority': priority,
                'type': item['type'],
                'roi_percent': item['roi_percent']
            })
        
        roi_analysis['total_potential_gain'] = round(roi_analysis['total_potential_gain'], 2)
        roi_analysis['total_potential_savings'] = round(roi_analysis['total_potential_savings'], 2)
        
        return roi_analysis