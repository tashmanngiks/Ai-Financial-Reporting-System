"""
Financial Metrics Engine

Calculates key financial indicators, trends, and benchmark comparisons
from structured financial data.
"""

# import numpy as np
# import pandas as pd
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class FinancialMetricsEngine:
    """Core metrics calculation engine for financial analysis"""
    
    def __init__(self, data: Dict):
        """
        Initialize with financial data
        
        Args:
            data: Dictionary containing dashboard, qc_dashboard, income_risk, dupont
        """
        self.data = data
        self.dashboard = data.get('dashboard', {})
        self.qc_dashboard = data.get('qc_dashboard', {})
        self.income_risk = data.get('income_risk', {})
        self.dupont = data.get('dupont', {})
        
    def calculate_all_metrics(self) -> Dict:
        """
        Calculate all financial metrics
        
        Returns:
            Dictionary containing all calculated metrics
        """
        metrics = {}
        
        # Key Performance Indicators
        metrics.update(self._calculate_kpis())
        
        # Growth rates
        metrics.update(self._calculate_growth_rates())
        
        # Risk metrics
        metrics.update(self._calculate_risk_metrics())
        
        # Benchmark comparisons
        metrics.update(self._calculate_benchmark_comparisons())
        
        # Trend analysis
        metrics.update(self._calculate_trend_metrics())
        
        return metrics
    
    def _calculate_kpis(self) -> Dict:
        """Calculate key performance indicators"""
        kpis = {}
        
        # Return on Assets (ROA)
        net_income = self._safe_get_decimal(self.dashboard, 'net_income')
        total_assets = self._safe_get_decimal(self.dashboard, 'total_assets')
        if total_assets and total_assets > 0:
            kpis['roa'] = float(net_income / total_assets * 100)
        
        # Return on Equity (ROE)
        total_equity = self._safe_get_decimal(self.dashboard, 'total_equity')
        if total_equity and total_equity > 0:
            kpis['roe'] = float(net_income / total_equity * 100)
        
        # Tier 1 Capital Ratio
        tier1_capital = self._safe_get_decimal(self.dashboard, 'tier1_capital')
        risk_weighted_assets = self._safe_get_decimal(self.dashboard, 'risk_weighted_assets')
        if risk_weighted_assets and risk_weighted_assets > 0:
            kpis['tier1_ratio'] = float(tier1_capital / risk_weighted_assets * 100)
        
        # Loss Rate
        loan_losses = self._safe_get_decimal(self.dashboard, 'loan_losses')
        total_loans = self._safe_get_decimal(self.dashboard, 'total_loans')
        if total_loans and total_loans > 0:
            kpis['loss_rate'] = float(loan_losses / total_loans * 100)
        
        # Efficiency Ratio
        operating_expenses = self._safe_get_decimal(self.dashboard, 'operating_expenses')
        operating_income = self._safe_get_decimal(self.dashboard, 'operating_income')
        if operating_income and operating_income > 0:
            kpis['efficiency_ratio'] = float(operating_expenses / operating_income * 100)
        
        return kpis
    
    def _calculate_growth_rates(self) -> Dict:
        """Calculate period-over-period growth rates"""
        growth = {}
        
        # Get time series data from qc_dashboard
        time_series = self.qc_dashboard.get('time_series', {})
        
        if time_series:
            # Asset growth
            asset_series = time_series.get('total_assets', [])
            if len(asset_series) >= 2:
                growth['asset_growth'] = self._calculate_growth_rate(asset_series)
            
            # Loan growth
            loan_series = time_series.get('total_loans', [])
            if len(loan_series) >= 2:
                growth['loan_growth'] = self._calculate_growth_rate(loan_series)
            
            # Deposit growth
            deposit_series = time_series.get('total_deposits', [])
            if len(deposit_series) >= 2:
                growth['deposit_growth'] = self._calculate_growth_rate(deposit_series)
        
        return growth
    
    def _calculate_risk_metrics(self) -> Dict:
        """Calculate risk assessment metrics"""
        risk = {}
        
        # Credit Risk Score (0-100, higher is riskier)
        loss_rate = self._safe_get_decimal(self.dashboard, 'loss_rate')
        non_performing_loans = self._safe_get_decimal(self.dashboard, 'non_performing_loans')
        total_loans = self._safe_get_decimal(self.dashboard, 'total_loans')
        
        if total_loans and total_loans > 0:
            npl_ratio = float(non_performing_loans / total_loans * 100)
            # Weighted credit risk score
            risk['credit_risk_score'] = min(100, (loss_rate * 0.6 + npl_ratio * 0.4) * 10)
        
        # Liquidity Ratio
        liquid_assets = self._safe_get_decimal(self.dashboard, 'liquid_assets')
        total_deposits = self._safe_get_decimal(self.dashboard, 'total_deposits')
        if total_deposits and total_deposits > 0:
            risk['liquidity_ratio'] = float(liquid_assets / total_deposits * 100)
        
        # Capital Adequacy
        tier1_ratio = self._safe_get_decimal(self.dashboard, 'tier1_ratio')
        total_capital_ratio = self._safe_get_decimal(self.dashboard, 'total_capital_ratio')
        if tier1_ratio and total_capital_ratio:
            risk['capital_adequacy'] = float((tier1_ratio + total_capital_ratio) / 2)
        
        return risk
    
    def _calculate_benchmark_comparisons(self) -> Dict:
        """Calculate comparisons against benchmark data"""
        comparisons = {}
        
        benchmark_data = self.income_risk.get('benchmark', {})
        bank_data = self.income_risk.get('bank', {})
        
        if benchmark_data and bank_data:
            # ROA comparison
            bank_roa = self._safe_get_decimal(bank_data, 'roa')
            benchmark_roa = self._safe_get_decimal(benchmark_data, 'roa')
            if benchmark_roa and benchmark_roa > 0:
                comparisons['roa_vs_benchmark'] = float(bank_roa - benchmark_roa)
            
            # ROE comparison
            bank_roe = self._safe_get_decimal(bank_data, 'roe')
            benchmark_roe = self._safe_get_decimal(benchmark_data, 'roe')
            if benchmark_roe and benchmark_roe > 0:
                comparisons['roe_vs_benchmark'] = float(bank_roe - benchmark_roe)
            
            # Efficiency comparison (lower is better)
            bank_efficiency = self._safe_get_decimal(bank_data, 'efficiency_ratio')
            benchmark_efficiency = self._safe_get_decimal(benchmark_data, 'efficiency_ratio')
            if benchmark_efficiency and benchmark_efficiency > 0:
                comparisons['efficiency_vs_benchmark'] = float(benchmark_efficiency - bank_efficiency)
        
        return comparisons
    
    def _calculate_trend_metrics(self) -> Dict:
        """Calculate trend analysis metrics"""
        trends = {}
        
        time_series = self.qc_dashboard.get('time_series', {})
        
        for metric_name, values in time_series.items():
            if len(values) >= 3:  # Need at least 3 points for trend analysis
                trend_data = self._analyze_trend(values)
                trends[f'{metric_name}_trend'] = trend_data
        
        return trends
    
    def _analyze_trend(self, values: List[float]) -> Dict:
        """Analyze trend direction and volatility"""
        if len(values) < 2:
            return {'direction': 'insufficient_data', 'volatility': 0}
        
        # Calculate trend direction using simple method (numpy disabled)
        # x = np.arange(len(values))
        # y = np.array(values)
        
        # Simple trend calculation
        if len(values) < 2:
            return {'direction': 'insufficient_data', 'volatility': 0}
        
        # Calculate simple slope
        first_half = values[:len(values)//2] if len(values) > 2 else values[:1]
        second_half = values[len(values)//2:] if len(values) > 2 else values[1:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        slope = second_avg - first_avg
        
        # Determine direction
        if abs(slope) < 0.01:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        # Calculate simple volatility
        mean_val = sum(values) / len(values)
        if mean_val != 0:
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            std_dev = variance ** 0.5
            volatility = float(std_dev / abs(mean_val) * 100)
        else:
            volatility = 0
        
        return {
            'direction': direction,
            'slope': float(slope),
            'volatility': volatility,
            'recent_change': self._calculate_recent_change(values)
        }
    
    def _calculate_recent_change(self, values: List[float]) -> float:
        """Calculate percentage change between most recent periods"""
        if len(values) < 2:
            return 0
        
        current = values[-1]
        previous = values[-2]
        
        if previous == 0:
            return 0
        
        return float((current - previous) / abs(previous) * 100)
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate compound annual growth rate from time series"""
        if len(values) < 2:
            return 0
        
        # Use most recent values for growth calculation
        current = values[-1]
        previous = values[-2]
        
        if previous == 0:
            return 0
        
        return float((current - previous) / abs(previous) * 100)
    
    def _safe_get_decimal(self, data: Dict, key: str) -> Decimal:
        """Safely get and convert value to Decimal"""
        try:
            value = data.get(key, 0)
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '')
            return Decimal(str(value))
        except (ValueError, TypeError):
            return Decimal('0')
    
    def assess_risk_level(self, metrics: Dict) -> str:
        """
        Assess overall risk level based on metrics
        
        Args:
            metrics: Dictionary of calculated metrics
            
        Returns:
            Risk level: 'low', 'moderate', 'high', or 'critical'
        """
        risk_score = 0
        
        # Credit risk assessment
        credit_risk = metrics.get('credit_risk_score', 0)
        if credit_risk > 70:
            risk_score += 3
        elif credit_risk > 40:
            risk_score += 2
        elif credit_risk > 20:
            risk_score += 1
        
        # Liquidity assessment
        liquidity = metrics.get('liquidity_ratio', 100)
        if liquidity < 10:
            risk_score += 3
        elif liquidity < 20:
            risk_score += 2
        elif liquidity < 30:
            risk_score += 1
        
        # Capital adequacy assessment
        capital = metrics.get('capital_adequacy', 20)
        if capital < 8:
            risk_score += 3
        elif capital < 12:
            risk_score += 2
        elif capital < 15:
            risk_score += 1
        
        # Performance assessment
        roa = metrics.get('roa', 1)
        if roa < -2:
            risk_score += 3
        elif roa < 0:
            risk_score += 2
        elif roa < 0.5:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 8:
            return 'critical'
        elif risk_score >= 5:
            return 'high'
        elif risk_score >= 2:
            return 'moderate'
        else:
            return 'low'
    
    def calculate_overall_score(self, metrics: Dict) -> float:
        """
        Calculate overall financial health score (0-100)
        
        Args:
            metrics: Dictionary of calculated metrics
            
        Returns:
            Overall score
        """
        score = 50  # Base score
        
        # Performance factors (40 points total)
        roa = metrics.get('roa', 0)
        if roa > 1.5:
            score += 15
        elif roa > 1.0:
            score += 10
        elif roa > 0.5:
            score += 5
        elif roa < 0:
            score -= 10
        
        roe = metrics.get('roe', 0)
        if roe > 15:
            score += 15
        elif roe > 10:
            score += 10
        elif roe > 5:
            score += 5
        elif roe < 0:
            score -= 10
        
        efficiency = metrics.get('efficiency_ratio', 60)
        if efficiency < 50:
            score += 10
        elif efficiency < 60:
            score += 5
        elif efficiency > 80:
            score -= 10
        
        # Risk factors (30 points total)
        credit_risk = metrics.get('credit_risk_score', 30)
        if credit_risk < 20:
            score += 15
        elif credit_risk < 40:
            score += 10
        elif credit_risk < 60:
            score += 5
        elif credit_risk > 80:
            score -= 15
        
        liquidity = metrics.get('liquidity_ratio', 30)
        if liquidity > 30:
            score += 10
        elif liquidity > 20:
            score += 5
        elif liquidity < 10:
            score -= 15
        
        capital = metrics.get('capital_adequacy', 15)
        if capital > 15:
            score += 5
        elif capital < 8:
            score -= 15
        
        # Growth factors (20 points total)
        asset_growth = metrics.get('asset_growth', 0)
        if 5 < asset_growth < 15:
            score += 10
        elif 0 < asset_growth < 5:
            score += 5
        elif asset_growth < -5:
            score -= 10
        
        # Benchmark factors (10 points total)
        roa_vs_benchmark = metrics.get('roa_vs_benchmark', 0)
        if roa_vs_benchmark > 0.5:
            score += 5
        elif roa_vs_benchmark < -0.5:
            score -= 5
        
        return max(0, min(100, score))
    
    def generate_key_insights(self, metrics: Dict) -> List[str]:
        """Generate key insights from calculated metrics"""
        insights = []
        
        # Performance insights
        roa = metrics.get('roa', 0)
        if roa > 1.5:
            insights.append("Strong profitability with ROA significantly above industry average")
        elif roa < 0:
            insights.append("Negative returns indicate serious profitability concerns")
        
        # Risk insights
        credit_risk = metrics.get('credit_risk_score', 30)
        if credit_risk > 70:
            insights.append("High credit risk concentration requires immediate attention")
        elif credit_risk < 20:
            insights.append("Conservative credit risk management demonstrates strong underwriting")
        
        # Efficiency insights
        efficiency = metrics.get('efficiency_ratio', 60)
        if efficiency > 80:
            insights.append("High operational efficiency ratio suggests cost management issues")
        elif efficiency < 50:
            insights.append("Excellent operational efficiency demonstrates effective cost control")
        
        # Growth insights
        asset_growth = metrics.get('asset_growth', 0)
        if asset_growth > 15:
            insights.append("Rapid asset growth may indicate expansion opportunities or increased risk")
        elif asset_growth < -5:
            insights.append("Asset contraction suggests strategic challenges or market pressures")
        
        # Liquidity insights
        liquidity = metrics.get('liquidity_ratio', 30)
        if liquidity < 15:
            insights.append("Low liquidity ratios indicate potential funding stress")
        
        return insights
