"""
Financial Report Generator

Combines metrics, insights, and data to generate comprehensive
financial analysis reports in structured format.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal

from .metrics_engine import FinancialMetricsEngine
from .dynamic_report_builder import build_dynamic_report_sections, build_statistics_bundle
from .insight_engine import FinancialInsightEngine
from .report_prompt_registry import get_report_prompt_registry


class FinancialReportGenerator:
    """Generates comprehensive financial analysis reports"""
    
    def __init__(self):
        self.metrics_engine = FinancialMetricsEngine
        self.insight_engine = FinancialInsightEngine()
    
    def generate_complete_report(self, data: Dict, upload_info: Dict = None, report_options: Dict = None) -> Dict:
        """
        Generate a complete financial analysis report
        
        Args:
            data: Structured financial data
            upload_info: Upload metadata (filename, user, etc.)
            
        Returns:
            Complete structured report
        """
        # Initialize metrics engine with data
        metrics_engine = self.metrics_engine(data)
        
        # Calculate all metrics
        metrics = metrics_engine.calculate_all_metrics()
        
        # Add assessment metrics
        metrics['risk_level'] = metrics_engine.assess_risk_level(metrics)
        metrics['overall_score'] = metrics_engine.calculate_overall_score(metrics)
        
        # Generate key insights
        metrics['key_insights'] = metrics_engine.generate_key_insights(metrics)
        
        # Generate AI-powered insights
        registry = get_report_prompt_registry()
        report_options = registry.build_report_options(report_options or {})
        insights = self.insight_engine.generate_all_insights(metrics, data, report_options=report_options)
        
        # Build complete report structure
        report = self._build_report_structure(
            data=data,
            metrics=metrics,
            insights=insights,
            upload_info=upload_info,
            report_options=report_options,
        )
        
        return report
    
    def _build_report_structure(self, data: Dict, metrics: Dict, insights: Dict, upload_info: Dict = None, report_options: Dict = None) -> Dict:
        """Build the complete report structure"""
        
        # Extract basic information
        bank_name = data.get('dashboard', {}).get('bank_name', 'Financial Institution')
        period = data.get('dashboard', {}).get('period', 'Current Period')
        report_date = datetime.now().strftime('%B %d, %Y')
        
        # Build report sections
        registry = get_report_prompt_registry()
        report_options = registry.build_report_options(report_options or {})
        adaptive_sections = build_dynamic_report_sections(report_options.get('sections', []), data, report_options)
        statistics_bundle = build_statistics_bundle(data)

        report = {
            'metadata': {
                'title': f'Financial Analysis Report - {bank_name}',
                'bank_name': bank_name,
                'period': period,
                'report_date': report_date,
                'generated_by': 'AI Financial Analytics System',
                'upload_info': upload_info or {},
                'report_options': report_options,
            },
            'report_options': report_options,
            'adaptive_sections': adaptive_sections,
            'statistical_highlights': statistics_bundle,
            
            'executive_summary': self._build_executive_summary_section(metrics, insights),
            
            'financial_performance': self._build_financial_performance_section(metrics, data),
            
            'trend_analysis': self._build_trend_analysis_section(metrics, insights, data),
            
            'risk_assessment': self._build_risk_assessment_section(metrics, insights),
            
            'benchmark_comparison': self._build_benchmark_comparison_section(metrics, insights),
            
            'strengths_weaknesses': self._build_strengths_weaknesses_section(insights),
            
            'recommendations': self._build_recommendations_section(insights),
            
            'key_metrics': self._build_key_metrics_section(metrics),
            
            'appendix': self._build_appendix_section(data, metrics)
        }

        return report
    
    def _build_executive_summary_section(self, metrics: Dict, insights: Dict) -> Dict:
        """Build executive summary section"""
        ai_insight = insights.get('executive_summary', {}).get('content', '')
        key_points = insights.get('executive_summary', {}).get('key_points', [])
        
        return {
            'title': 'Executive Summary',
            'content': ai_insight,
            'key_points': key_points,
            'overall_assessment': {
                'score': metrics.get('overall_score', 0),
                'risk_level': metrics.get('risk_level', 'unknown'),
                'performance_rating': self._get_performance_rating(metrics.get('overall_score', 0))
            },
            'highlights': metrics.get('key_insights', [])
        }
    
    def _build_financial_performance_section(self, metrics: Dict, data: Dict) -> Dict:
        """Build financial performance section"""
        return {
            'title': 'Financial Performance Analysis',
            'profitability_metrics': {
                'return_on_assets': {
                    'value': metrics.get('roa', 0),
                    'benchmark': data.get('income_risk', {}).get('benchmark', {}).get('roa', 0),
                    'analysis': self._analyze_roa(metrics.get('roa', 0))
                },
                'return_on_equity': {
                    'value': metrics.get('roe', 0),
                    'benchmark': data.get('income_risk', {}).get('benchmark', {}).get('roe', 0),
                    'analysis': self._analyze_roe(metrics.get('roe', 0))
                },
                'efficiency_ratio': {
                    'value': metrics.get('efficiency_ratio', 0),
                    'benchmark': data.get('income_risk', {}).get('benchmark', {}).get('efficiency_ratio', 0),
                    'analysis': self._analyze_efficiency(metrics.get('efficiency_ratio', 0))
                }
            },
            'capital_metrics': {
                'tier1_ratio': {
                    'value': metrics.get('tier1_ratio', 0),
                    'analysis': self._analyze_tier1(metrics.get('tier1_ratio', 0))
                },
                'capital_adequacy': {
                    'value': metrics.get('capital_adequacy', 0),
                    'analysis': self._analyze_capital_adequacy(metrics.get('capital_adequacy', 0))
                }
            },
            'asset_quality': {
                'loss_rate': {
                    'value': metrics.get('loss_rate', 0),
                    'analysis': self._analyze_loss_rate(metrics.get('loss_rate', 0))
                },
                'credit_risk_score': {
                    'value': metrics.get('credit_risk_score', 0),
                    'analysis': self._analyze_credit_risk(metrics.get('credit_risk_score', 0))
                }
            }
        }
    
    def _build_trend_analysis_section(self, metrics: Dict, insights: Dict, data: Dict) -> Dict:
        """Build trend analysis section"""
        ai_insight = insights.get('trend_analysis', {}).get('content', '')
        key_points = insights.get('trend_analysis', {}).get('key_points', [])
        
        # Extract trend metrics
        trend_metrics = {}
        for key, value in metrics.items():
            if 'trend' in key:
                trend_metrics[key] = value
        
        return {
            'title': 'Trend Analysis',
            'content': ai_insight,
            'key_points': key_points,
            'growth_metrics': {
                'asset_growth': {
                    'value': metrics.get('asset_growth', 0),
                    'trend': self._categorize_growth(metrics.get('asset_growth', 0))
                },
                'loan_growth': {
                    'value': metrics.get('loan_growth', 0),
                    'trend': self._categorize_growth(metrics.get('loan_growth', 0))
                },
                'deposit_growth': {
                    'value': metrics.get('deposit_growth', 0),
                    'trend': self._categorize_growth(metrics.get('deposit_growth', 0))
                }
            },
            'trend_details': trend_metrics,
            'time_series_data': data.get('qc_dashboard', {}).get('time_series', {})
        }
    
    def _build_risk_assessment_section(self, metrics: Dict, insights: Dict) -> Dict:
        """Build risk assessment section"""
        ai_insight = insights.get('risk_assessment', {}).get('content', '')
        key_points = insights.get('risk_assessment', {}).get('key_points', [])
        
        return {
            'title': 'Risk Assessment',
            'content': ai_insight,
            'key_points': key_points,
            'overall_risk': {
                'level': metrics.get('risk_level', 'unknown'),
                'score': metrics.get('credit_risk_score', 0),
                'assessment': self._get_risk_assessment_text(metrics.get('risk_level', 'unknown'))
            },
            'risk_categories': {
                'credit_risk': {
                    'score': metrics.get('credit_risk_score', 0),
                    'level': self._get_risk_level_from_score(metrics.get('credit_risk_score', 0)),
                    'factors': ['Loss Rate', 'Non-Performing Loans', 'Loan Portfolio Quality']
                },
                'liquidity_risk': {
                    'ratio': metrics.get('liquidity_ratio', 0),
                    'level': self._get_liquidity_risk_level(metrics.get('liquidity_ratio', 0)),
                    'factors': ['Liquidity Ratio', 'Deposit Stability', 'Access to Funding']
                },
                'capital_risk': {
                    'ratio': metrics.get('capital_adequacy', 0),
                    'level': self._get_capital_risk_level(metrics.get('capital_adequacy', 0)),
                    'factors': ['Tier 1 Capital', 'Capital Adequacy', 'Buffer Strength']
                }
            }
        }
    
    def _build_benchmark_comparison_section(self, metrics: Dict, insights: Dict) -> Dict:
        """Build benchmark comparison section"""
        ai_insight = insights.get('benchmark_comparison', {}).get('content', '')
        key_points = insights.get('benchmark_comparison', {}).get('key_points', [])
        
        return {
            'title': 'Benchmark Comparison',
            'content': ai_insight,
            'key_points': key_points,
            'performance_gaps': {
                'roa_gap': {
                    'bank': metrics.get('roa', 0),
                    'benchmark': metrics.get('roa', 0) - metrics.get('roa_vs_benchmark', 0),
                    'difference': metrics.get('roa_vs_benchmark', 0),
                    'assessment': self._assess_performance_gap(metrics.get('roa_vs_benchmark', 0))
                },
                'roe_gap': {
                    'bank': metrics.get('roe', 0),
                    'benchmark': metrics.get('roe', 0) - metrics.get('roe_vs_benchmark', 0),
                    'difference': metrics.get('roe_vs_benchmark', 0),
                    'assessment': self._assess_performance_gap(metrics.get('roe_vs_benchmark', 0))
                },
                'efficiency_gap': {
                    'bank': metrics.get('efficiency_ratio', 0),
                    'benchmark': metrics.get('efficiency_ratio', 0) + metrics.get('efficiency_vs_benchmark', 0),
                    'difference': metrics.get('efficiency_vs_benchmark', 0),
                    'assessment': self._assess_efficiency_gap(metrics.get('efficiency_vs_benchmark', 0))
                }
            },
            'competitive_positioning': self._assess_competitive_position(metrics)
        }
    
    def _build_strengths_weaknesses_section(self, insights: Dict) -> Dict:
        """Build strengths and weaknesses section"""
        ai_insight = insights.get('strengths_weaknesses', {}).get('content', '')
        key_points = insights.get('strengths_weaknesses', {}).get('key_points', [])
        
        return {
            'title': 'Strengths and Weaknesses',
            'content': ai_insight,
            'key_points': key_points,
            'strategic_assessment': {
                'primary_strengths': self._extract_strengths_from_insight(ai_insight),
                'critical_weaknesses': self._extract_weaknesses_from_insight(ai_insight),
                'strategic_implications': self._extract_strategic_implications(ai_insight)
            }
        }
    
    def _build_recommendations_section(self, insights: Dict) -> Dict:
        """Build recommendations section"""
        ai_insight = insights.get('recommendations', {}).get('content', '')
        key_points = insights.get('recommendations', {}).get('key_points', [])
        
        return {
            'title': 'Strategic Recommendations',
            'content': ai_insight,
            'key_points': key_points,
            'action_plan': self._extract_action_items(ai_insight),
            'implementation_priorities': self._prioritize_recommendations(key_points)
        }
    
    def _build_key_metrics_section(self, metrics: Dict) -> Dict:
        """Build key metrics summary section"""
        return {
            'title': 'Key Financial Metrics Summary',
            'profitability': {
                'roa': metrics.get('roa', 0),
                'roe': metrics.get('roe', 0),
                'efficiency_ratio': metrics.get('efficiency_ratio', 0)
            },
            'risk_metrics': {
                'credit_risk_score': metrics.get('credit_risk_score', 0),
                'liquidity_ratio': metrics.get('liquidity_ratio', 0),
                'capital_adequacy': metrics.get('capital_adequacy', 0),
                'loss_rate': metrics.get('loss_rate', 0)
            },
            'growth_metrics': {
                'asset_growth': metrics.get('asset_growth', 0),
                'loan_growth': metrics.get('loan_growth', 0),
                'deposit_growth': metrics.get('deposit_growth', 0)
            },
            'capital_metrics': {
                'tier1_ratio': metrics.get('tier1_ratio', 0),
                'overall_score': metrics.get('overall_score', 0),
                'risk_level': metrics.get('risk_level', 'unknown')
            }
        }
    
    def _build_appendix_section(self, data: Dict, metrics: Dict) -> Dict:
        """Build appendix with detailed data"""
        return {
            'title': 'Appendix - Detailed Data',
            'raw_data_summary': {
                'dashboard_data': self._summarize_data_section(data.get('dashboard', {})),
                'time_series_data': self._summarize_data_section(data.get('qc_dashboard', {})),
                'risk_data': self._summarize_data_section(data.get('income_risk', {})),
                'dupont_data': self._summarize_data_section(data.get('dupont', {}))
            },
            'calculation_methodology': self._get_calculation_methodology(),
            'data_quality_assessment': self._assess_data_quality(data)
        }
    
    # Helper methods for analysis and categorization
    
    def _get_performance_rating(self, score: float) -> str:
        """Get performance rating from overall score"""
        if score >= 85:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 55:
            return 'Average'
        elif score >= 40:
            return 'Below Average'
        else:
            return 'Poor'
    
    def _analyze_roa(self, roa: float) -> str:
        """Analyze ROA performance"""
        if roa > 1.5:
            return "Strong profitability significantly above industry average"
        elif roa > 1.0:
            return "Good profitability above industry standards"
        elif roa > 0.5:
            return "Moderate profitability with room for improvement"
        elif roa > 0:
            return "Low profitability requires attention"
        else:
            return "Negative returns indicate serious profitability issues"
    
    def _analyze_roe(self, roe: float) -> str:
        """Analyze ROE performance"""
        if roe > 15:
            return "Excellent shareholder returns"
        elif roe > 10:
            return "Strong shareholder value creation"
        elif roe > 5:
            return "Adequate returns to shareholders"
        elif roe > 0:
            return "Weak returns requiring improvement"
        else:
            return "Negative returns eroding shareholder value"
    
    def _analyze_efficiency(self, efficiency: float) -> str:
        """Analyze efficiency ratio (lower is better)"""
        if efficiency < 50:
            return "Excellent operational efficiency"
        elif efficiency < 60:
            return "Good efficiency with effective cost control"
        elif efficiency < 75:
            return "Average efficiency with opportunities for improvement"
        elif efficiency < 85:
            return "Below average efficiency indicates cost management issues"
        else:
            return "Poor efficiency requiring immediate attention"
    
    def _analyze_tier1(self, tier1: float) -> str:
        """Analyze Tier 1 capital ratio"""
        if tier1 > 12:
            return "Strong capital position well above regulatory requirements"
        elif tier1 > 8:
            return "Adequate capital meeting regulatory standards"
        elif tier1 > 6:
            return "Minimum capital levels requiring monitoring"
        else:
            return "Inadequate capital below regulatory requirements"
    
    def _analyze_capital_adequacy(self, capital: float) -> str:
        """Analyze capital adequacy"""
        if capital > 15:
            return "Strong capital buffer"
        elif capital > 12:
            return "Adequate capital levels"
        elif capital > 8:
            return "Minimum acceptable capital"
        else:
            return "Insufficient capital"
    
    def _analyze_loss_rate(self, loss_rate: float) -> str:
        """Analyze loss rate"""
        if loss_rate < 0.5:
            return "Excellent asset quality with minimal losses"
        elif loss_rate < 1.0:
            return "Good asset quality with controlled losses"
        elif loss_rate < 2.0:
            return "Acceptable loss levels within industry norms"
        elif loss_rate < 3.0:
            return "Elevated loss rates requiring attention"
        else:
            return "High loss rates indicating asset quality concerns"
    
    def _analyze_credit_risk(self, risk_score: float) -> str:
        """Analyze credit risk score"""
        if risk_score < 20:
            return "Low credit risk profile"
        elif risk_score < 40:
            return "Moderate credit risk with good controls"
        elif risk_score < 60:
            return "Elevated credit risk requiring monitoring"
        elif risk_score < 80:
            return "High credit risk requiring immediate action"
        else:
            return "Critical credit risk levels"
    
    def _categorize_growth(self, growth: float) -> str:
        """Categorize growth rate"""
        if growth > 15:
            return "Rapid Growth"
        elif growth > 5:
            return "Healthy Growth"
        elif growth > 0:
            return "Modest Growth"
        elif growth > -5:
            return "Stable"
        else:
            return "Declining"
    
    def _get_risk_assessment_text(self, risk_level: str) -> str:
        """Get risk assessment description"""
        descriptions = {
            'low': "Strong risk management practices with minimal concerns",
            'moderate': "Adequate risk controls with some areas requiring attention",
            'high': "Elevated risk levels requiring immediate management focus",
            'critical': "Critical risk issues requiring urgent corrective action",
            'unknown': "Risk level could not be determined"
        }
        return descriptions.get(risk_level, "Risk assessment not available")
    
    def _get_risk_level_from_score(self, score: float) -> str:
        """Get risk level from credit risk score"""
        if score < 20:
            return 'Low'
        elif score < 40:
            return 'Moderate'
        elif score < 60:
            return 'High'
        else:
            return 'Critical'
    
    def _get_liquidity_risk_level(self, ratio: float) -> str:
        """Get liquidity risk level from ratio"""
        if ratio > 30:
            return 'Low'
        elif ratio > 20:
            return 'Moderate'
        elif ratio > 15:
            return 'High'
        else:
            return 'Critical'
    
    def _get_capital_risk_level(self, ratio: float) -> str:
        """Get capital risk level from ratio"""
        if ratio > 15:
            return 'Low'
        elif ratio > 12:
            return 'Moderate'
        elif ratio > 8:
            return 'High'
        else:
            return 'Critical'
    
    def _assess_performance_gap(self, gap: float) -> str:
        """Assess performance gap"""
        if gap > 1.0:
            return "Significant outperformance vs benchmark"
        elif gap > 0.5:
            return "Moderate outperformance vs benchmark"
        elif gap > -0.5:
            return "Performance in line with benchmark"
        elif gap > -1.0:
            return "Moderate underperformance vs benchmark"
        else:
            return "Significant underperformance vs benchmark"
    
    def _assess_efficiency_gap(self, gap: float) -> str:
        """Assess efficiency gap (positive is better)"""
        if gap > 5:
            return "Significant efficiency advantage vs benchmark"
        elif gap > 2:
            return "Moderate efficiency advantage vs benchmark"
        elif gap > -2:
            return "Efficiency in line with benchmark"
        elif gap > -5:
            return "Moderate efficiency disadvantage vs benchmark"
        else:
            return "Significant efficiency disadvantage vs benchmark"
    
    def _assess_competitive_position(self, metrics: Dict) -> str:
        """Assess overall competitive positioning"""
        roa_gap = metrics.get('roa_vs_benchmark', 0)
        roe_gap = metrics.get('roe_vs_benchmark', 0)
        efficiency_gap = metrics.get('efficiency_vs_benchmark', 0)
        
        positive_gaps = sum(1 for gap in [roa_gap, roe_gap, efficiency_gap] if gap > 0)
        
        if positive_gaps >= 2:
            return "Strong competitive position with multiple performance advantages"
        elif positive_gaps == 1:
            return "Moderate competitive position with selective advantages"
        else:
            return "Challenged competitive position requiring performance improvements"
    
    def _extract_strengths_from_insight(self, insight: str) -> List[str]:
        """Extract strengths from AI insight"""
        strengths = []
        lines = insight.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['strength', 'strong', 'advantage', 'excellent']):
                strengths.append(line.strip())
        return strengths[:3]
    
    def _extract_weaknesses_from_insight(self, insight: str) -> List[str]:
        """Extract weaknesses from AI insight"""
        weaknesses = []
        lines = insight.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['weakness', 'weak', 'challenge', 'concern', 'issue']):
                weaknesses.append(line.strip())
        return weaknesses[:3]
    
    def _extract_strategic_implications(self, insight: str) -> List[str]:
        """Extract strategic implications from AI insight"""
        implications = []
        lines = insight.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['strategic', 'implication', 'impact', 'position']):
                implications.append(line.strip())
        return implications[:3]
    
    def _extract_action_items(self, insight: str) -> List[str]:
        """Extract action items from recommendations"""
        actions = []
        lines = insight.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'action', 'implement', 'improve', 'enhance']):
                actions.append(line.strip())
        return actions[:5]
    
    def _prioritize_recommendations(self, key_points: List[str]) -> Dict:
        """Prioritize recommendations by urgency and impact"""
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for point in key_points:
            if any(keyword in point.lower() for keyword in ['urgent', 'critical', 'immediate', 'essential']):
                high_priority.append(point)
            elif any(keyword in point.lower() for keyword in ['important', 'significant', 'major']):
                medium_priority.append(point)
            else:
                low_priority.append(point)
        
        return {
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority
        }
    
    def _summarize_data_section(self, data: Dict) -> Dict:
        """Summarize a data section"""
        if not data:
            return {'status': 'No data available'}
        
        summary = {
            'keys': list(data.keys())[:10],  # First 10 keys
            'data_points': len(data),
            'has_nested_data': any(isinstance(v, dict) for v in data.values()),
            'sample_values': {}
        }
        
        # Add sample values for first few keys
        for key in list(data.keys())[:5]:
            value = data[key]
            if isinstance(value, (str, int, float)):
                summary['sample_values'][key] = str(value)[:100]
            else:
                summary['sample_values'][key] = f"{type(value).__name__} ({len(str(value))} chars)"
        
        return summary
    
    def _get_calculation_methodology(self) -> Dict:
        """Get calculation methodology descriptions"""
        return {
            'profitability_metrics': {
                'roa': 'Net Income / Total Assets × 100',
                'roe': 'Net Income / Total Equity × 100',
                'efficiency_ratio': 'Operating Expenses / Operating Income × 100'
            },
            'risk_metrics': {
                'credit_risk_score': 'Weighted combination of loss rate and NPL ratio',
                'liquidity_ratio': 'Liquid Assets / Total Deposits × 100',
                'capital_adequacy': 'Average of Tier 1 and Total Capital ratios'
            },
            'growth_metrics': {
                'growth_rate': 'Period-over-period percentage change'
            }
        }
    
    def _assess_data_quality(self, data: Dict) -> Dict:
        """Assess quality of input data"""
        quality_score = 100
        issues = []
        
        # Check for required sections
        required_sections = ['dashboard', 'qc_dashboard', 'income_risk']
        for section in required_sections:
            if section not in data or not data[section]:
                quality_score -= 20
                issues.append(f"Missing or empty {section} section")
        
        # Check for key metrics
        dashboard = data.get('dashboard', {})
        key_metrics = ['total_assets', 'total_equity', 'net_income']
        for metric in key_metrics:
            if metric not in dashboard:
                quality_score -= 10
                issues.append(f"Missing key metric: {metric}")
        
        # Check for time series data
        qc_dashboard = data.get('qc_dashboard', {})
        if not qc_dashboard.get('time_series'):
            quality_score -= 15
            issues.append("Missing time series data for trend analysis")
        
        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'assessment': 'Good' if quality_score >= 80 else 'Fair' if quality_score >= 60 else 'Poor'
        }
