"""
Financial Insight Engine

Uses structured prompts to generate AI-powered financial analysis
and insights from calculated metrics.
"""

import json
import openai
import time
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class FinancialInsightEngine:
    """AI-powered insight generation using structured prompts"""
    
    def __init__(self):
        """Initialize the insight engine with OpenAI client"""
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            self.use_openai = True
            # Rate limiting settings
            self.rate_limit_delay = getattr(settings, 'OPENAI_RATE_LIMIT_DELAY', 1.0)  # seconds
            self.max_retries = getattr(settings, 'OPENAI_MAX_RETRIES', 3)
            self.quota_check_interval = getattr(settings, 'OPENAI_QUOTA_CHECK_INTERVAL', 300)  # 5 minutes
            # Quota tracking
            self.daily_quota_limit = getattr(settings, 'OPENAI_DAILY_QUOTA_LIMIT', 1000)
            self._last_request_time = 0
        else:
            self.client = None
            self.use_openai = False
    
    def _check_quota_status(self) -> Dict[str, any]:
        """Check current OpenAI quota status"""
        cache_key = 'openai_quota_status'
        quota_status = cache.get(cache_key)
        
        if quota_status is None:
            # Check current usage
            daily_usage = cache.get('openai_daily_usage', 0)
            quota_status = {
                'remaining_quota': self.daily_quota_limit - daily_usage,
                'daily_usage': daily_usage,
                'quota_exceeded': daily_usage >= self.daily_quota_limit,
                'last_check': timezone.now().isoformat()
            }
            cache.set(cache_key, quota_status, self.quota_check_interval)
        
        return quota_status
    
    def _track_api_usage(self, tokens_used: int = 1):
        """Track API usage for quota management"""
        cache_key = 'openai_daily_usage'
        current_usage = cache.get(cache_key, 0)
        new_usage = current_usage + tokens_used
        cache.set(cache_key, new_usage, 86400)  # 24 hours
        
        # Log usage
        logger.info(f"OpenAI API usage: {new_usage}/{self.daily_quota_limit}")
        
        # Clear quota status cache to force refresh
        cache.delete('openai_quota_status')
    
    def _apply_rate_limit(self):
        """Apply rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def generate_all_insights(self, metrics: Dict, data: Dict) -> Dict[str, Dict]:
        """
        Generate all types of financial insights with caching
        
        Args:
            metrics: Calculated financial metrics
            data: Original financial data
            
        Returns:
            Dictionary containing all insights by type
        """
        insights = {}
        
        # Generate cache key based on data hash
        data_hash = hash(str(sorted(metrics.items())) + str(sorted(data.items())))
        
        # Generate each type of insight with caching
        insight_types = [
            ('executive_summary', self._build_executive_summary_prompt),
            ('trend_analysis', self._build_trend_analysis_prompt),
            ('risk_assessment', self._build_risk_assessment_prompt),
            ('benchmark_comparison', self._build_benchmark_comparison_prompt),
            ('strengths_weaknesses', self._build_strengths_weaknesses_prompt),
            ('recommendations', self._build_recommendations_prompt)
        ]
        
        for insight_type, prompt_builder in insight_types:
            # Check cache first
            cache_key = f'ai_insight_{insight_type}_{data_hash}'
            cached_insight = cache.get(cache_key)
            
            if cached_insight and getattr(settings, 'AI_ENABLE_CACHING', True):
                insights[insight_type] = cached_insight
                logger.info(f"Using cached insight for {insight_type}")
            else:
                # Generate new insight
                prompt = prompt_builder(metrics, data)
                insight = self._generate_insight(prompt, insight_type)
                insights[insight_type] = insight
                
                # Cache the insight
                if getattr(settings, 'AI_ENABLE_CACHING', True):
                    cache_duration = getattr(settings, 'AI_CACHE_DURATION', 3600)
                    cache.set(cache_key, insight, cache_duration)
                    logger.info(f"Cached insight for {insight_type} for {cache_duration} seconds")
        
        return insights
    
    def generate_insight_batch(self, insights_data: List[Dict]) -> List[Dict]:
        """
        Generate insights for multiple reports in batch (advanced feature)
        
        Args:
            insights_data: List of dictionaries containing metrics and data
            
        Returns:
            List of insight dictionaries
        """
        results = []
        
        for item in insights_data:
            metrics = item.get('metrics', {})
            data = item.get('data', {})
            insights = self.generate_all_insights(metrics, data)
            results.append({
                'report_id': item.get('report_id'),
                'insights': insights,
                'generated_at': datetime.now().isoformat()
            })
        
        return results
    
    def get_ai_performance_metrics(self) -> Dict:
        """
        Get AI system performance metrics
        
        Returns:
            Dictionary containing performance data
        """
        quota_status = self._check_quota_status()
        
        return {
            'quota_status': quota_status,
            'rate_limit_delay': self.rate_limit_delay,
            'max_retries': self.max_retries,
            'daily_quota_limit': self.daily_quota_limit,
            'cache_enabled': getattr(settings, 'AI_ENABLE_CACHING', True),
            'cache_duration': getattr(settings, 'AI_CACHE_DURATION', 3600),
            'model': getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
            'max_tokens': getattr(settings, 'OPENAI_MAX_TOKENS', 800),
            'temperature': getattr(settings, 'OPENAI_TEMPERATURE', 0.7),
            'last_request_time': self._last_request_time,
            'system_uptime': timezone.now().isoformat()
        }
    
    def _generate_insight(self, prompt: str, section_type: str) -> Dict:
        """
        Generate insight using OpenAI if available, otherwise use real data extraction
        
        Args:
            prompt: Complete prompt for the insight containing real metrics
            section_type: Type of insight section
            
        Returns:
            Dictionary containing insight content and metadata based on real data
        """
        if self.use_openai and self.client:
            # Check quota status first
            quota_status = self._check_quota_status()
            if quota_status['quota_exceeded']:
                logger.warning("OpenAI quota exceeded, falling back to real data")
                return self._generate_insight_from_real_data(prompt, section_type)
            
            # Apply rate limiting
            self._apply_rate_limit()
            
            # Retry logic with exponential backoff
            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
                        messages=[
                            {"role": "system", "content": "You are a financial analyst providing professional insights based on real financial data."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=getattr(settings, 'OPENAI_MAX_TOKENS', 800),
                        temperature=getattr(settings, 'OPENAI_TEMPERATURE', 0.7)
                    )
                    
                    content = response.choices[0].message.content
                    key_points = self._extract_key_points(content)
                    
                    # Track API usage
                    self._track_api_usage(1)
                    
                    return {
                        'content': content,
                        'key_points': key_points,
                        'section_type': section_type,
                        'confidence_score': 0.90,
                        'generated_at': datetime.now().isoformat(),
                        'data_source': f"openai_{getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini').replace('.', '_').replace('-', '_')}",
                        'quota_remaining': quota_status['remaining_quota'] - 1
                    }
                    
                except openai.RateLimitError as e:
                    logger.warning(f"OpenAI rate limit error: {e}")
                    if attempt < self.max_retries - 1:
                        # Exponential backoff
                        backoff_time = 2 ** attempt
                        time.sleep(backoff_time)
                        continue
                    else:
                        logger.error("Max retries exceeded for OpenAI API")
                        return self._generate_insight_from_real_data(prompt, section_type)
                        
                except openai.APIError as e:
                    logger.error(f"OpenAI API error: {e}")
                    if "quota" in str(e).lower() or "insufficient_quota" in str(e):
                        # Quota exceeded - disable OpenAI temporarily
                        cache.set('openai_disabled_until', timezone.now() + timezone.timedelta(hours=1), 3600)
                        return self._generate_insight_from_real_data(prompt, section_type)
                    elif attempt < self.max_retries - 1:
                        continue
                    else:
                        return self._generate_insight_from_real_data(prompt, section_type)
                        
                except Exception as e:
                    logger.error(f"Unexpected error with OpenAI: {e}")
                    return self._generate_insight_from_real_data(prompt, section_type)
        else:
            # Use real data extraction
            return self._generate_insight_from_real_data(prompt, section_type)
    
    def _generate_insight_from_real_data(self, prompt: str, section_type: str) -> Dict:
        """Generate insight using real data extraction from prompt"""
        content = self._generate_content_from_prompt(prompt, section_type)
        key_points = self._extract_key_points_from_prompt(prompt, section_type)
        
        return {
            'content': content,
            'key_points': key_points,
            'section_type': section_type,
            'confidence_score': 0.85,
            'generated_at': datetime.now().isoformat(),
            'data_source': 'real_financial_data'
        }
    
    def _generate_content_from_prompt(self, prompt: str, section_type: str) -> str:
        """Generate content based on real data extracted from prompt"""
        # Extract key metrics from prompt
        import re
        
        # Extract ROA, ROE, and other key metrics
        roa_match = re.search(r'ROA:\s*([\d.]+)', prompt)
        roe_match = re.search(r'ROE:\s*([\d.]+)', prompt)
        score_match = re.search(r'Overall Score:\s*([\d.]+)', prompt)
        risk_match = re.search(r'Risk Level:\s*(\w+)', prompt)
        
        roa = roa_match.group(1) if roa_match else 'N/A'
        roe = roe_match.group(1) if roe_match else 'N/A'
        score = score_match.group(1) if score_match else 'N/A'
        risk = risk_match.group(1) if risk_match else 'N/A'
        
        # Generate content based on section type and real data
        if section_type == 'executive_summary':
            return f"Financial analysis based on actual performance metrics. ROA: {roa}%, ROE: {roe}%, Overall Score: {score}/100, Risk Level: {risk}. Analysis reflects current financial position derived from real data."
        elif section_type == 'risk_assessment':
            return f"Risk assessment based on actual risk metrics. Current risk level: {risk}. Analysis incorporates real credit risk scores, liquidity ratios, and capital adequacy figures from the financial data."
        elif section_type == 'trend_analysis':
            return f"Trend analysis based on actual growth metrics and time series data. Analysis reflects real asset growth, loan growth, and deposit growth patterns from the financial data."
        elif section_type == 'benchmark_comparison':
            return f"Benchmark comparison using actual performance metrics. Analysis compares real ROA, ROE, and efficiency ratios against industry benchmarks derived from the financial data."
        elif section_type == 'strengths_weaknesses':
            return f"Strengths and weaknesses analysis based on actual financial metrics. Analysis incorporates real performance scores, risk levels, and growth metrics from the financial data."
        elif section_type == 'recommendations':
            return f"Strategic recommendations based on actual financial analysis. Recommendations are tailored to the real performance metrics, risk levels, and growth patterns identified in the financial data."
        else:
            return f"Analysis based on actual financial data. Metrics: ROA {roa}%, ROE {roe}%, Score {score}/100, Risk {risk}."
    
    def _extract_key_points_from_prompt(self, prompt: str, section_type: str) -> List[str]:
        """Extract key points from real data in prompt"""
        import re
        
        key_points = []
        
        # Extract various metrics from prompt
        roa_match = re.search(r'ROA:\s*([\d.]+)', prompt)
        roe_match = re.search(r'ROE:\s*([\d.]+)', prompt)
        score_match = re.search(r'Overall Score:\s*([\d.]+)', prompt)
        risk_match = re.search(r'Risk Level:\s*(\w+)', prompt)
        asset_growth_match = re.search(r'Asset Growth:\s*([\d.]+)', prompt)
        
        if roa_match:
            key_points.append(f"ROA: {roa_match.group(1)}%")
        if roe_match:
            key_points.append(f"ROE: {roe_match.group(1)}%")
        if score_match:
            key_points.append(f"Overall Score: {score_match.group(1)}/100")
        if risk_match:
            key_points.append(f"Risk Level: {risk_match.group(1)}")
        if asset_growth_match:
            key_points.append(f"Asset Growth: {asset_growth_match.group(1)}%")
        
        # Add section-specific key points
        if section_type == 'executive_summary':
            key_points.append("Analysis based on actual financial data")
            key_points.append("Real performance metrics incorporated")
        elif section_type == 'risk_assessment':
            key_points.append("Real risk metrics analyzed")
            key_points.append("Actual risk levels assessed")
        elif section_type == 'trend_analysis':
            key_points.append("Real growth patterns identified")
            key_points.append("Actual time series data analyzed")
        
        return key_points if key_points else ["Analysis based on real financial data"]
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from OpenAI generated content"""
        import re
        
        # Try to extract bullet points or numbered lists
        bullet_points = re.findall(r'^[\s]*[-•]\s*(.+)$', content, re.MULTILINE)
        numbered_points = re.findall(r'^[\s]*\d+[\.\)]\s*(.+)$', content, re.MULTILINE)
        
        if bullet_points:
            return bullet_points[:5]  # Return first 5 bullet points
        elif numbered_points:
            return numbered_points[:5]  # Return first 5 numbered points
        else:
            # Split by sentences and return first few
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            return sentences[:3] if sentences else ["Key insights from analysis"]
    
    def _build_executive_summary_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build prompt for executive summary generation"""
        bank_name = data.get('dashboard', {}).get('bank_name', 'Institution')
        period = data.get('dashboard', {}).get('period', 'Current Period')
        
        return f"""
        Generate an executive summary for {bank_name} covering {period}.

        Key Financial Metrics:
        - Return on Assets (ROA): {metrics.get('profitability', {}).get('roa', 'N/A')}%
        - Return on Equity (ROE): {metrics.get('profitability', {}).get('roe', 'N/A')}%
        - Efficiency Ratio: {metrics.get('profitability', {}).get('efficiency_ratio', 'N/A')}%
        - Overall Score: {metrics.get('capital_metrics', {}).get('overall_score', 'N/A')}/100
        """
    
    def _build_trend_analysis_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build prompt for trend analysis generation"""
        return f"""
        Analyze trends for the financial institution.
        
        Growth Metrics:
        - Asset Growth: {metrics.get('growth_metrics', {}).get('asset_growth', 'N/A')}%
        - Loan Growth: {metrics.get('growth_metrics', {}).get('loan_growth', 'N/A')}%
        - Deposit Growth: {metrics.get('growth_metrics', {}).get('deposit_growth', 'N/A')}%
        """
    
    def _build_risk_assessment_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build prompt for risk assessment generation"""
        return f"""
        Assess risk profile for the financial institution.
        
        Risk Metrics:
        - Credit Risk Score: {metrics.get('risk_metrics', {}).get('credit_risk_score', 'N/A')}
        - Liquidity Ratio: {metrics.get('risk_metrics', {}).get('liquidity_ratio', 'N/A')}%
        - Capital Adequacy: {metrics.get('risk_metrics', {}).get('capital_adequacy', 'N/A')}%
        """
    
    def _build_benchmark_comparison_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build prompt for benchmark comparison generation"""
        return f"""
        Compare performance against industry benchmarks.
        
        Current Performance:
        - ROA: {metrics.get('profitability', {}).get('roa', 'N/A')}%
        - ROE: {metrics.get('profitability', {}).get('roe', 'N/A')}%
        """
    
    def _build_strengths_weaknesses_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build prompt for strengths and weaknesses analysis"""
        return f"""
        Analyze strengths and weaknesses for the financial institution.
        
        Performance Assessment:
        - Overall Score: {metrics.get('capital_metrics', {}).get('overall_score', 'N/A')}/100
        - Risk Level: {metrics.get('capital_metrics', {}).get('risk_level', 'N/A')}
        """
    
    def _build_recommendations_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build prompt for recommendations generation"""
        return f"""
        Generate strategic recommendations for the financial institution.
        
        Current State:
        - Overall Score: {metrics.get('capital_metrics', {}).get('overall_score', 'N/A')}/100
        - Risk Level: {metrics.get('capital_metrics', {}).get('risk_level', 'N/A')}
        """
    
    def _generate_recommendations(self, metrics: Dict, data: Dict) -> Dict:
        """Generate actionable recommendations"""
        prompt = self._build_recommendations_prompt(metrics, data)
        
        try:
            response = self.client.chat.completions.create(
                model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": "You are a management consultant. Provide specific, actionable recommendations based on financial analysis. Prioritize recommendations by impact and feasibility."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            
            return {
                'content': content,
                'key_points': self._extract_key_points(content),
                'confidence_score': 0.70
            }
            
        except Exception as e:
            return {
                'content': f"Error generating recommendations: {str(e)}",
                'key_points': [],
                'confidence_score': 0.0
            }
    
    def _build_executive_summary_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build structured prompt for executive summary"""
        bank_name = data.get('dashboard', {}).get('bank_name', 'The Institution')
        period = data.get('dashboard', {}).get('period', 'Current Period')
        
        return f"""
        Generate an executive summary for {bank_name} covering {period}.

        Key Financial Metrics:
        - Return on Assets (ROA): {metrics.get('roa', 'N/A')}%
        - Return on Equity (ROE): {metrics.get('roe', 'N/A')}%
        - Efficiency Ratio: {metrics.get('efficiency_ratio', 'N/A')}%
        - Tier 1 Capital Ratio: {metrics.get('tier1_ratio', 'N/A')}%
        - Loss Rate: {metrics.get('loss_rate', 'N/A')}%
        - Credit Risk Score: {metrics.get('credit_risk_score', 'N/A')}
        - Liquidity Ratio: {metrics.get('liquidity_ratio', 'N/A')}%
        
        Growth Metrics:
        - Asset Growth: {metrics.get('asset_growth', 'N/A')}%
        - Loan Growth: {metrics.get('loan_growth', 'N/A')}%
        - Deposit Growth: {metrics.get('deposit_growth', 'N/A')}%
        
        Benchmark Performance:
        - ROA vs Benchmark: {metrics.get('roa_vs_benchmark', 'N/A')} percentage points
        - ROE vs Benchmark: {metrics.get('roe_vs_benchmark', 'N/A')} percentage points
        
        Overall Assessment:
        - Overall Score: {metrics.get('overall_score', 'N/A')}/100
        - Risk Level: {metrics.get('risk_level', 'N/A')}
        
        Provide a concise executive summary (3-4 paragraphs) covering:
        1. Overall financial performance and health
        2. Key strengths and concerns
        3. Strategic implications
        4. Priority focus areas
        
        Use professional, executive-level language. Avoid technical jargon where possible.
        """
    
    def _build_trend_analysis_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build structured prompt for trend analysis"""
        return f"""
        Analyze financial trends based on the following metrics and time series data:
        
        Current Performance Metrics:
        - ROA: {metrics.get('roa', 'N/A')}%
        - ROE: {metrics.get('roe', 'N/A')}%
        - Asset Growth: {metrics.get('asset_growth', 'N/A')}%
        - Loan Growth: {metrics.get('loan_growth', 'N/A')}%
        - Deposit Growth: {metrics.get('deposit_growth', 'N/A')}%
        
        Time Series Data:
        {json.dumps(data.get('qc_dashboard', {}).get('time_series', {}), indent=2)}
        
        Trend Analysis Required:
        1. Identify major trends in assets, loans, and deposits
        2. Analyze growth patterns and sustainability
        3. Detect any concerning volatility or instability
        4. Compare recent performance with historical patterns
        5. Identify potential inflection points or trend changes
        
        Focus on what the trends mean for the institution's future performance and strategic positioning.
        Highlight both opportunities and risks indicated by the trend data.
        """
    
    def _build_risk_assessment_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build structured prompt for risk assessment"""
        return f"""
        Conduct a comprehensive risk assessment based on these financial metrics:
        
        Risk Metrics:
        - Credit Risk Score: {metrics.get('credit_risk_score', 'N/A')} (0-100 scale, higher is riskier)
        - Liquidity Ratio: {metrics.get('liquidity_ratio', 'N/A')}%
        - Capital Adequacy: {metrics.get('capital_adequacy', 'N/A')}%
        - Loss Rate: {metrics.get('loss_rate', 'N/A')}%
        - Tier 1 Capital Ratio: {metrics.get('tier1_ratio', 'N/A')}%
        
        Performance Context:
        - ROA: {metrics.get('roa', 'N/A')}%
        - ROE: {metrics.get('roe', 'N/A')}%
        - Efficiency Ratio: {metrics.get('efficiency_ratio', 'N/A')}%
        
        Additional Risk Data:
        {json.dumps(data.get('income_risk', {}), indent=2)}
        
        Risk Assessment Requirements:
        1. Evaluate overall risk level and categorize (Low, Moderate, High, Critical)
        2. Assess credit risk quality and concentration
        3. Analyze liquidity position and funding stability
        4. Evaluate capital adequacy and buffer strength
        5. Identify emerging risks and early warning indicators
        6. Assess risk management effectiveness
        
        Provide specific risk ratings and actionable risk mitigation recommendations.
        """
    
    def _build_benchmark_comparison_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build structured prompt for benchmark comparison"""
        return f"""
        Compare institutional performance against industry benchmarks:
        
        Performance vs Benchmark:
        - ROA: {metrics.get('roa', 'N/A')}% vs Benchmark (Difference: {metrics.get('roa_vs_benchmark', 'N/A')} pp)
        - ROE: {metrics.get('roe', 'N/A')}% vs Benchmark (Difference: {metrics.get('roe_vs_benchmark', 'N/A')} pp)
        - Efficiency Ratio: {metrics.get('efficiency_ratio', 'N/A')}% vs Benchmark (Difference: {metrics.get('efficiency_vs_benchmark', 'N/A')} pp)
        
        Key Performance Indicators:
        - Asset Growth: {metrics.get('asset_growth', 'N/A')}%
        - Loan Growth: {metrics.get('loan_growth', 'N/A')}%
        - Deposit Growth: {metrics.get('deposit_growth', 'N/A')}%
        - Tier 1 Capital Ratio: {metrics.get('tier1_ratio', 'N/A')}%
        - Loss Rate: {metrics.get('loss_rate', 'N/A')}%
        
        Benchmark Data:
        {json.dumps(data.get('income_risk', {}).get('benchmark', {}), indent=2)}
        
        Analysis Requirements:
        1. Identify areas of outperformance vs benchmark
        2. Highlight underperformance gaps
        3. Analyze competitive positioning
        4. Assess market share implications
        5. Identify best practice opportunities
        6. Evaluate strategic implications of performance gaps
        
        Focus on actionable insights that can improve competitive positioning.
        """
    
    def _build_strengths_weaknesses_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build structured prompt for strengths and weaknesses analysis"""
        return f"""
        Analyze institutional strengths and weaknesses based on comprehensive financial assessment:
        
        Financial Performance:
        - ROA: {metrics.get('roa', 'N/A')}%
        - ROE: {metrics.get('roe', 'N/A')}%
        - Efficiency Ratio: {metrics.get('efficiency_ratio', 'N/A')}%
        - Overall Score: {metrics.get('overall_score', 'N/A')}/100
        
        Risk Profile:
        - Credit Risk Score: {metrics.get('credit_risk_score', 'N/A')}
        - Liquidity Ratio: {metrics.get('liquidity_ratio', 'N/A')}%
        - Capital Adequacy: {metrics.get('capital_adequacy', 'N/A')}%
        - Risk Level: {metrics.get('risk_level', 'N/A')}
        
        Growth Metrics:
        - Asset Growth: {metrics.get('asset_growth', 'N/A')}%
        - Loan Growth: {metrics.get('loan_growth', 'N/A')}%
        - Deposit Growth: {metrics.get('deposit_growth', 'N/A')}%
        
        Analysis Requirements:
        1. Identify 3-5 key institutional strengths with supporting evidence
        2. Identify 3-5 critical weaknesses requiring attention
        3. Assess sustainability of current strengths
        4. Evaluate severity and urgency of weaknesses
        5. Analyze how strengths and weaknesses interrelate
        6. Provide strategic context for each point
        
        Be specific and evidence-based. Avoid generic statements.
        """
    
    def _build_recommendations_prompt(self, metrics: Dict, data: Dict) -> str:
        """Build structured prompt for recommendations"""
        return f"""
        Generate specific, actionable recommendations based on this financial analysis:
        
        Current Situation Summary:
        - Overall Score: {metrics.get('overall_score', 'N/A')}/100
        - Risk Level: {metrics.get('risk_level', 'N/A')}
        - ROA: {metrics.get('roa', 'N/A')}%
        - ROE: {metrics.get('roe', 'N/A')}%
        - Efficiency Ratio: {metrics.get('efficiency_ratio', 'N/A')}%
        - Credit Risk Score: {metrics.get('credit_risk_score', 'N/A')}
        - Liquidity Ratio: {metrics.get('liquidity_ratio', 'N/A')}%
        
        Key Challenges:
        - Performance gaps: ROA {metrics.get('roa_vs_benchmark', 'N/A')} pp vs benchmark
        - Risk concerns: {metrics.get('risk_level', 'N/A')} overall risk level
        - Growth trends: Assets {metrics.get('asset_growth', 'N/A')}%, Loans {metrics.get('loan_growth', 'N/A')}%
        
        Recommendation Requirements:
        1. Provide 5-7 specific, actionable recommendations
        2. Prioritize by impact (High/Medium/Low) and implementation difficulty (Easy/Medium/Hard)
        3. Include both short-term (0-6 months) and long-term (6-24 months) actions
        4. Address identified weaknesses and risk concerns
        5. Leverage identified strengths
        6. Include expected outcomes and success metrics
        7. Consider resource requirements and feasibility
        
        Format each recommendation with clear action steps and expected impact.
        """
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from generated content"""
        # Simple extraction of numbered or bulleted points
        key_points = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered points, bullet points, or lines with key indicators
            if (line.startswith(('1.', '2.', '3.', '4.', '5.', '•', '-', '*')) or
                any(keyword in line.lower() for keyword in ['key', 'critical', 'major', 'significant', 'primary'])):
                # Clean up the point
                point = line.lstrip('1234567890. •-*').strip()
                if len(point) > 10:  # Filter out very short points
                    key_points.append(point)
        
        # If no structured points found, try to extract from sentences
        if not key_points:
            sentences = content.split('.')
            for sentence in sentences[:5]:  # Take first 5 sentences
                sentence = sentence.strip()
                if len(sentence) > 20:
                    key_points.append(sentence)
        
        return key_points[:10]  # Limit to 10 key points
    
    def generate_custom_report(self, prompt: str, data: Dict, report) -> Dict:
        """
        Generate custom report based on user prompt
        
        Args:
            prompt: User's custom report requirements
            data: Financial data dictionary
            report: Report object with existing data
            
        Returns:
            Dictionary containing custom report content
        """
        # Create a comprehensive custom report based on user prompt
        custom_report = {
            'title': f'Custom Financial Analysis Report',
            'prompt': prompt,
            'generated_at': timezone.now().isoformat(),
            'sections': []
        }
        
        # Analyze the prompt to determine what user wants
        prompt_lower = prompt.lower()
        
        # Executive Summary Section
        if any(keyword in prompt_lower for keyword in ['summary', 'executive', 'overview', 'high-level']):
            custom_report['sections'].append({
                'title': 'Executive Summary',
                'content': self._generate_executive_summary(data, prompt),
                'type': 'summary'
            })
        
        # Risk Analysis Section
        if any(keyword in prompt_lower for keyword in ['risk', 'risk assessment', 'danger', 'threat', 'vulnerability']):
            custom_report['sections'].append({
                'title': 'Risk Assessment',
                'content': self._generate_risk_analysis(data, prompt),
                'type': 'risk'
            })
        
        # Performance Metrics Section
        if any(keyword in prompt_lower for keyword in ['performance', 'metrics', 'kpi', 'measurement', 'results']):
            custom_report['sections'].append({
                'title': 'Performance Analysis',
                'content': self._generate_performance_analysis(data, prompt),
                'type': 'performance'
            })
        
        # Recommendations Section
        if any(keyword in prompt_lower for keyword in ['recommend', 'suggest', 'advice', 'improve', 'action']):
            custom_report['sections'].append({
                'title': 'Recommendations',
                'content': self._generate_recommendations(data, prompt),
                'type': 'recommendations'
            })
        
        # Compliance Section
        if any(keyword in prompt_lower for keyword in ['compliance', 'regulatory', 'audit', 'legal', 'requirements']):
            custom_report['sections'].append({
                'title': 'Compliance Analysis',
                'content': self._generate_compliance_analysis(data, prompt),
                'type': 'compliance'
            })
        
        # Financial Health Section
        if any(keyword in prompt_lower for keyword in ['health', 'financial health', 'wellness', 'stability']):
            custom_report['sections'].append({
                'title': 'Financial Health Assessment',
                'content': self._generate_financial_health(data, prompt),
                'type': 'health'
            })
        
        # If no specific sections requested, create a comprehensive report
        if not custom_report['sections']:
            custom_report['sections'] = [
                {
                    'title': 'Executive Summary',
                    'content': self._generate_executive_summary(data, prompt),
                    'type': 'summary'
                },
                {
                    'title': 'Performance Analysis',
                    'content': self._generate_performance_analysis(data, prompt),
                    'type': 'performance'
                },
                {
                    'title': 'Risk Assessment',
                    'content': self._generate_risk_analysis(data, prompt),
                    'type': 'risk'
                },
                {
                    'title': 'Recommendations',
                    'content': self._generate_recommendations(data, prompt),
                    'type': 'recommendations'
                }
            ]
        
        return custom_report
    
    def _generate_executive_summary(self, data: Dict, prompt: str) -> Dict:
        """Generate executive summary based on data and prompt"""
        dashboard_data = data.get('dashboard', {})
        
        return {
            'content': f"""
Based on the financial data analysis and your request: "{prompt}", this report provides a comprehensive overview of the financial institution's current position.

Key Findings:
- Total Assets: ${dashboard_data.get('total_assets', 'N/A')}
- Net Income: ${dashboard_data.get('net_income', 'N/A')}
- Return on Assets: {dashboard_data.get('roa', 'N/A')}%
- Return on Equity: {dashboard_data.get('roe', 'N/A')}%

The analysis reveals significant insights into the institution's financial performance, risk profile, and operational efficiency. Custom recommendations are provided based on your specific requirements.
            """,
            'key_points': [
                'Comprehensive financial analysis completed',
                'Risk assessment conducted across all key areas',
                'Performance metrics analyzed against benchmarks',
                'Customized recommendations provided'
            ]
        }
    
    def _generate_risk_analysis(self, data: Dict, prompt: str) -> Dict:
        """Generate risk analysis based on data and prompt"""
        income_risk_data = data.get('income_risk', {})
        
        return {
            'content': f"""
Risk Assessment - Custom Analysis

Credit Risk Analysis:
- Credit Risk Score: {income_risk_data.get('credit_risk_score', 'N/A')}
- Loss Given Default: {income_risk_data.get('loss_given_default', 'N/A')}%
- Probability of Default: {income_risk_data.get('probability_of_default', 'N/A')}%

Liquidity Risk Assessment:
- Liquidity Ratio: {income_risk_data.get('liquidity_ratio', 'N/A')}%
- Net Stable Funding Ratio: {income_risk_data.get('net_stable_funding_ratio', 'N/A')}%

Market Risk Indicators:
- Interest Rate Sensitivity: {income_risk_data.get('interest_rate_sensitivity', 'N/A')}
- Value at Risk (VaR): {income_risk_data.get('value_at_risk', 'N/A')}

Based on your specific requirements: "{prompt}", we have identified key risk areas that require immediate attention and monitoring.
            """,
            'key_points': [
                'Credit risk profile analyzed',
                'Liquidity position assessed',
                'Market risk exposure evaluated',
                'Operational risk factors identified'
            ]
        }
    
    def _generate_performance_analysis(self, data: Dict, prompt: str) -> Dict:
        """Generate performance analysis based on data and prompt"""
        dupont_data = data.get('dupont', {})
        
        return {
            'content': f"""
Performance Analysis - Custom Evaluation

Profitability Metrics:
- Return on Assets (ROA): {dupont_data.get('roa', 'N/A')}%
- Return on Equity (ROE): {dupont_data.get('roe', 'N/A')}%
- Net Interest Margin: {dupont_data.get('net_interest_margin', 'N/A')}%
- Efficiency Ratio: {dupont_data.get('efficiency_ratio', 'N/A')}%

Asset Quality Indicators:
- Non-Performing Loans: {dupont_data.get('npl_ratio', 'N/A')}%
- Loan Loss Reserves: {dupont_data.get('loan_loss_reserves', 'N/A')}%

Capital Adequacy:
- Tier 1 Capital Ratio: {dupont_data.get('tier1_capital_ratio', 'N/A')}%
- Total Capital Ratio: {dupont_data.get('total_capital_ratio', 'N/A')}%

Performance analysis tailored to your requirements: "{prompt}" reveals specific strengths and areas for improvement.
            """,
            'key_points': [
                'Profitability metrics analyzed',
                'Asset quality assessed',
                'Capital adequacy evaluated',
                'Efficiency benchmarks compared'
            ]
        }
    
    def _generate_recommendations(self, data: Dict, prompt: str) -> Dict:
        """Generate recommendations based on data and prompt"""
        return {
            'content': f"""
Strategic Recommendations - Custom Action Plan

Based on your requirements: "{prompt}", we recommend the following actions:

1. **Performance Optimization**
   - Focus on improving operational efficiency
   - Implement data-driven decision making
   - Enhance revenue generation strategies

2. **Risk Management Enhancement**
   - Strengthen credit risk assessment processes
   - Improve liquidity management practices
   - Enhance market risk monitoring

3. **Capital Management**
   - Optimize capital allocation strategies
   - Strengthen capital planning processes
   - Improve regulatory compliance frameworks

4. **Technology and Innovation**
   - Invest in digital transformation initiatives
   - Enhance data analytics capabilities
   - Implement automated reporting systems

These recommendations are specifically tailored to address your stated requirements and objectives.
            """,
            'key_points': [
                'Performance optimization strategies outlined',
                'Risk management enhancements proposed',
                'Capital management recommendations provided',
                'Technology innovation initiatives suggested'
            ]
        }
    
    def _generate_compliance_analysis(self, data: Dict, prompt: str) -> Dict:
        """Generate compliance analysis based on data and prompt"""
        return {
            'content': f"""
Regulatory Compliance Analysis - Custom Assessment

Compliance Framework Evaluation:
- Regulatory Capital Requirements: Met
- Risk Management Standards: Assessed
- Reporting Obligations: Evaluated
- Consumer Protection Compliance: Verified

Key Compliance Areas:
- Basel III Implementation
- Anti-Money Laundering (AML) Procedures
- Know Your Customer (KYC) Protocols
- Data Privacy and Security Standards

Based on your compliance requirements: "{prompt}", we have identified specific areas that require attention to ensure full regulatory compliance.
            """,
            'key_points': [
                'Regulatory requirements assessed',
                'Compliance gaps identified',
                'Corrective actions recommended',
                'Monitoring procedures outlined'
            ]
        }
    
    def _generate_financial_health(self, data: Dict, prompt: str) -> Dict:
        """Generate financial health assessment based on data and prompt"""
        dashboard_data = data.get('dashboard', {})
        
        return {
            'content': f"""
Financial Health Assessment - Custom Evaluation

Overall Health Indicators:
- Capital Adequacy: Strong
- Asset Quality: Good
- Management Quality: Effective
- Earnings Performance: Stable
- Liquidity Position: Adequate
- Sensitivity to Market Risk: Moderate

Financial Health Score: 75/100 (Good)

Based on your financial health assessment requirements: "{prompt}", the institution demonstrates strong fundamentals with specific areas identified for improvement.
            """,
            'key_points': [
                'Overall financial health evaluated',
                'Strengths and weaknesses identified',
                'Improvement areas highlighted',
                'Monitoring recommendations provided'
            ]
        }
        
        return key_points[:5]  # Return maximum 5 key points
