"""
Trend Analyzer

Analyzes insurance data trends over time periods and provides comparative analysis
to identify patterns and changes in claim behavior.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """
    Analyzes trends in insurance claims data across different time periods
    and provides comparative insights.
    """
    
    def __init__(self):
        self.time_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        self.trend_metrics = ['volume', 'amount', 'approval_rate', 'processing_time']
    
    async def analyze_trends(
        self, 
        claims_data: List[Dict[str, Any]],
        period: str = 'monthly',
        compare_periods: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze trends in claims data over specified time periods.
        
        Args:
            claims_data: List of claim records
            period: Time period for analysis (daily, weekly, monthly, quarterly, yearly)
            compare_periods: Number of periods to analyze for trends
            
        Returns:
            Trend analysis results with metrics and visualizations data
        """
        try:
            if not claims_data:
                return {'success': False, 'error': 'No claims data provided'}
            
            df = pd.DataFrame(claims_data)
            
            # Prepare data for trend analysis
            df = await self._prepare_time_series_data(df)
            
            if df.empty:
                return {'success': False, 'error': 'No valid date data found'}
            
            # Generate time-based aggregations
            trend_data = await self._generate_trend_data(df, period, compare_periods)
            
            # Calculate trend metrics
            trend_metrics = await self._calculate_trend_metrics(trend_data)
            
            # Identify significant patterns
            patterns = await self._identify_patterns(trend_data, trend_metrics)
            
            # Generate comparative analysis
            comparative_analysis = await self._generate_comparative_analysis(trend_data)
            
            # Forecast future trends (simple projection)
            forecast = await self._generate_forecast(trend_data)
            
            return {
                'success': True,
                'analysis_date': datetime.now().isoformat(),
                'period': period,
                'periods_analyzed': compare_periods,
                'trend_data': trend_data,
                'trend_metrics': trend_metrics,
                'patterns': patterns,
                'comparative_analysis': comparative_analysis,
                'forecast': forecast
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {'success': False, 'error': 'Trend analysis failed due to an internal error.'}
    
    async def _prepare_time_series_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for time series analysis."""
        # Convert claim_date to datetime
        if 'claim_date' in df.columns:
            df['claim_date'] = pd.to_datetime(df['claim_date'], errors='coerce')
            df = df.dropna(subset=['claim_date'])
        else:
            return pd.DataFrame()
        
        # Convert numeric columns
        numeric_columns = ['claim_amount', 'approved_amount', 'processing_days']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate processing days if not available
        if 'processing_date' in df.columns and 'processing_days' not in df.columns:
            df['processing_date'] = pd.to_datetime(df['processing_date'], errors='coerce')
            df['processing_days'] = (df['processing_date'] - df['claim_date']).dt.days
        
        # Add derived columns for analysis
        df['is_approved'] = df['status'] == 'approved'
        df['is_rejected'] = df['status'] == 'rejected'
        
        return df.sort_values('claim_date')
    
    async def _generate_trend_data(
        self, 
        df: pd.DataFrame, 
        period: str, 
        compare_periods: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate aggregated data for trend analysis."""
        
        # Set up time grouping based on period
        if period == 'daily':
            df['period'] = df['claim_date'].dt.date
            freq = 'D'
        elif period == 'weekly':
            df['period'] = df['claim_date'].dt.to_period('W')
            freq = 'W'
        elif period == 'monthly':
            df['period'] = df['claim_date'].dt.to_period('M')
            freq = 'M'
        elif period == 'quarterly':
            df['period'] = df['claim_date'].dt.to_period('Q')
            freq = 'Q'
        elif period == 'yearly':
            df['period'] = df['claim_date'].dt.to_period('Y')
            freq = 'Y'
        else:
            # Default to monthly
            df['period'] = df['claim_date'].dt.to_period('M')
            freq = 'M'
        
        # Group by period and calculate metrics
        grouped = df.groupby('period').agg({
            'claim_id': 'count',
            'claim_amount': ['sum', 'mean', 'median'],
            'is_approved': ['sum', 'mean'],
            'is_rejected': ['sum', 'mean'],
            'processing_days': ['mean', 'median']
        }).reset_index()
        
        # Flatten column names
        grouped.columns = [
            'period', 'claim_count', 'total_amount', 'avg_amount', 'median_amount',
            'approved_count', 'approval_rate', 'rejected_count', 'rejection_rate',
            'avg_processing_days', 'median_processing_days'
        ]
        
        # Convert period to string for JSON serialization
        grouped['period_str'] = grouped['period'].astype(str)
        
        # Limit to requested number of periods (most recent)
        grouped = grouped.tail(compare_periods)
        
        trend_data = {
            'volume_trends': [],
            'amount_trends': [],
            'approval_trends': [],
            'processing_trends': []
        }
        
        for _, row in grouped.iterrows():
            period_str = row['period_str']
            
            # Volume trends
            trend_data['volume_trends'].append({
                'period': period_str,
                'claim_count': int(row['claim_count']),
                'approved_count': int(row['approved_count']),
                'rejected_count': int(row['rejected_count'])
            })
            
            # Amount trends
            trend_data['amount_trends'].append({
                'period': period_str,
                'total_amount': round(row['total_amount'], 2),
                'average_amount': round(row['avg_amount'], 2),
                'median_amount': round(row['median_amount'], 2)
            })
            
            # Approval trends
            trend_data['approval_trends'].append({
                'period': period_str,
                'approval_rate': round(row['approval_rate'] * 100, 2),
                'rejection_rate': round(row['rejection_rate'] * 100, 2)
            })
            
            # Processing trends
            if not pd.isna(row['avg_processing_days']):
                trend_data['processing_trends'].append({
                    'period': period_str,
                    'avg_processing_days': round(row['avg_processing_days'], 1),
                    'median_processing_days': round(row['median_processing_days'], 1)
                })
        
        return trend_data
    
    async def _calculate_trend_metrics(self, trend_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Calculate trend direction and growth rates."""
        metrics = {}
        
        # Volume trend metrics
        volume_data = trend_data['volume_trends']
        if len(volume_data) >= 2:
            metrics['volume'] = await self._calculate_metric_trends(
                [item['claim_count'] for item in volume_data]
            )
        
        # Amount trend metrics
        amount_data = trend_data['amount_trends']
        if len(amount_data) >= 2:
            metrics['amount'] = await self._calculate_metric_trends(
                [item['total_amount'] for item in amount_data]
            )
        
        # Approval rate trend metrics
        approval_data = trend_data['approval_trends']
        if len(approval_data) >= 2:
            metrics['approval_rate'] = await self._calculate_metric_trends(
                [item['approval_rate'] for item in approval_data]
            )
        
        # Processing time trend metrics
        processing_data = trend_data['processing_trends']
        if len(processing_data) >= 2:
            metrics['processing_time'] = await self._calculate_metric_trends(
                [item['avg_processing_days'] for item in processing_data]
            )
        
        return metrics
    
    async def _calculate_metric_trends(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend metrics for a series of values."""
        if len(values) < 2:
            return {'trend': 'insufficient_data'}
        
        # Calculate percentage changes
        changes = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                change = ((values[i] - values[i-1]) / values[i-1]) * 100
                changes.append(change)
        
        if not changes:
            return {'trend': 'no_change'}
        
        avg_change = np.mean(changes)
        recent_change = changes[-1] if changes else 0
        
        # Determine trend direction
        if avg_change > 5:
            trend_direction = 'increasing'
        elif avg_change < -5:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        return {
            'trend': trend_direction,
            'average_change_percent': round(avg_change, 2),
            'recent_change_percent': round(recent_change, 2),
            'total_change_percent': round(((values[-1] - values[0]) / values[0]) * 100, 2) if values[0] != 0 else 0,
            'values': values
        }
    
    async def _identify_patterns(
        self, 
        trend_data: Dict[str, List[Dict[str, Any]]],
        trend_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify significant patterns in the trend data."""
        patterns = []
        
        # Check for volume patterns
        if 'volume' in trend_metrics:
            volume_trend = trend_metrics['volume']
            if volume_trend['trend'] == 'increasing' and volume_trend['average_change_percent'] > 10:
                patterns.append({
                    'type': 'volume_surge',
                    'description': f"Claim volume increasing by {volume_trend['average_change_percent']:.1f}% on average",
                    'significance': 'high',
                    'impact': 'positive'
                })
            elif volume_trend['trend'] == 'decreasing' and volume_trend['average_change_percent'] < -10:
                patterns.append({
                    'type': 'volume_decline',
                    'description': f"Claim volume decreasing by {abs(volume_trend['average_change_percent']):.1f}% on average",
                    'significance': 'high',
                    'impact': 'negative'
                })
        
        # Check for approval rate patterns
        if 'approval_rate' in trend_metrics:
            approval_trend = trend_metrics['approval_rate']
            if approval_trend['trend'] == 'decreasing' and approval_trend['average_change_percent'] < -2:
                patterns.append({
                    'type': 'declining_approvals',
                    'description': f"Approval rate declining by {abs(approval_trend['average_change_percent']):.1f}% on average",
                    'significance': 'high',
                    'impact': 'negative'
                })
            elif approval_trend['trend'] == 'increasing' and approval_trend['average_change_percent'] > 2:
                patterns.append({
                    'type': 'improving_approvals',
                    'description': f"Approval rate improving by {approval_trend['average_change_percent']:.1f}% on average",
                    'significance': 'medium',
                    'impact': 'positive'
                })
        
        # Check for processing time patterns
        if 'processing_time' in trend_metrics:
            processing_trend = trend_metrics['processing_time']
            if processing_trend['trend'] == 'increasing' and processing_trend['average_change_percent'] > 5:
                patterns.append({
                    'type': 'slowing_processing',
                    'description': f"Processing times increasing by {processing_trend['average_change_percent']:.1f}% on average",
                    'significance': 'medium',
                    'impact': 'negative'
                })
        
        # Check for seasonal patterns (if enough data points)
        seasonal_patterns = await self._detect_seasonal_patterns(trend_data)
        patterns.extend(seasonal_patterns)
        
        return patterns
    
    async def _detect_seasonal_patterns(self, trend_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Detect seasonal patterns in the data."""
        patterns = []
        
        # For now, return placeholder for seasonal analysis
        # In full implementation, would use more sophisticated time series analysis
        if len(trend_data.get('volume_trends', [])) >= 12:
            patterns.append({
                'type': 'potential_seasonality',
                'description': 'Sufficient data points detected for seasonal analysis',
                'significance': 'low',
                'impact': 'informational'
            })
        
        return patterns
    
    async def _generate_comparative_analysis(self, trend_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate period-over-period comparative analysis."""
        comparative = {
            'current_vs_previous': {},
            'best_vs_worst_periods': {},
            'quarter_over_quarter': {}
        }
        
        # Current vs previous period comparison
        for metric_type, data in trend_data.items():
            if len(data) >= 2:
                current = data[-1]
                previous = data[-2]
                
                comparative['current_vs_previous'][metric_type] = {
                    'current_period': current,
                    'previous_period': previous,
                    'changes': await self._calculate_period_changes(current, previous)
                }
        
        # Best vs worst performing periods
        for metric_type, data in trend_data.items():
            if len(data) >= 3:
                comparative['best_vs_worst_periods'][metric_type] = await self._find_best_worst_periods(data)
        
        return comparative
    
    async def _calculate_period_changes(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, float]:
        """Calculate changes between two periods."""
        changes = {}
        
        # Compare numeric values
        for key in current:
            if key != 'period' and isinstance(current.get(key), (int, float)) and isinstance(previous.get(key), (int, float)):
                if previous[key] != 0:
                    change_percent = ((current[key] - previous[key]) / previous[key]) * 100
                    changes[f"{key}_change_percent"] = round(change_percent, 2)
                changes[f"{key}_absolute_change"] = current[key] - previous[key]
        
        return changes
    
    async def _find_best_worst_periods(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find best and worst performing periods for metrics."""
        result = {'best': {}, 'worst': {}}
        
        # Find best and worst based on key metrics
        key_metrics = ['claim_count', 'total_amount', 'approval_rate']
        
        for metric in key_metrics:
            values = [item.get(metric, 0) for item in data if metric in item]
            if values:
                max_idx = values.index(max(values))
                min_idx = values.index(min(values))
                
                result['best'][metric] = data[max_idx]
                result['worst'][metric] = data[min_idx]
        
        return result
    
    async def _generate_forecast(self, trend_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate simple forecast for next periods."""
        forecast = {
            'method': 'simple_linear_projection',
            'periods_ahead': 3,
            'predictions': {}
        }
        
        # Simple linear forecast for volume trends
        volume_data = trend_data.get('volume_trends', [])
        if len(volume_data) >= 3:
            values = [item['claim_count'] for item in volume_data[-3:]]
            trend = (values[-1] - values[0]) / 2  # Simple linear trend
            
            next_periods = []
            for i in range(1, 4):  # Forecast 3 periods ahead
                predicted_value = values[-1] + (trend * i)
                next_periods.append({
                    'period': f"forecast_{i}",
                    'predicted_claim_count': max(0, int(predicted_value))
                })
            
            forecast['predictions']['volume'] = next_periods
        
        return forecast