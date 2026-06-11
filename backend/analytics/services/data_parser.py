"""
Financial Data Parser

Parses and validates structured JSON financial data
into standardized format for analysis.
"""

import json
from typing import Dict, Any, List
from decimal import Decimal, InvalidOperation


class FinancialDataParser:
    """Parse and validate financial JSON data"""
    
    def __init__(self):
        self.required_fields = {
            'dashboard': ['bank_name', 'period'],
            'qc_dashboard': [],
            'income_risk': [],
            'dupont': []
        }
        
        self.numeric_fields = {
            'dashboard': [
                'total_assets', 'total_equity', 'net_income', 'operating_income',
                'operating_expenses', 'total_loans', 'total_deposits', 'liquid_assets',
                'loan_losses', 'non_performing_loans', 'tier1_capital', 'risk_weighted_assets'
            ]
        }
    
    def parse_financial_data(self, data: Dict) -> Dict[str, Any]:
        """
        Parse and validate complete financial data structure
        
        Args:
            data: Raw JSON financial data
            
        Returns:
            Parsed and validated financial data
            
        Raises:
            ValueError: If data is invalid
        """
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        
        parsed_data = {}
        
        # Parse each section
        for section in ['dashboard', 'qc_dashboard', 'income_risk', 'dupont']:
            section_data = data.get(section, {})
            if section_data:
                parsed_data[section] = self._parse_section(section, section_data)
            else:
                parsed_data[section] = {}
        
        # Validate required fields
        self._validate_required_fields(parsed_data)
        
        # Clean and standardize data
        parsed_data = self._clean_and_standardize(parsed_data)
        
        return parsed_data
    
    def _parse_section(self, section_name: str, section_data: Dict) -> Dict:
        """Parse individual data section"""
        if not isinstance(section_data, dict):
            raise ValueError(f"Section {section_name} must be a dictionary")
        
        parsed_section = {}
        
        # Handle different section types
        if section_name == 'dashboard':
            parsed_section = self._parse_dashboard_data(section_data)
        elif section_name == 'qc_dashboard':
            parsed_section = self._parse_qc_dashboard_data(section_data)
        elif section_name == 'income_risk':
            parsed_section = self._parse_income_risk_data(section_data)
        elif section_name == 'dupont':
            parsed_section = self._parse_dupont_data(section_data)
        else:
            parsed_section = section_data
        
        return parsed_section
    
    def _parse_dashboard_data(self, data: Dict) -> Dict:
        """Parse dashboard financial metrics"""
        parsed = {}
        
        # Copy string fields
        for field in ['bank_name', 'period']:
            if field in data:
                parsed[field] = str(data[field]).strip()
        
        # Parse numeric fields
        for field in self.numeric_fields['dashboard']:
            if field in data:
                parsed[field] = self._parse_numeric_value(data[field])
        
        # Handle nested structures
        if 'breakdowns' in data and isinstance(data['breakdowns'], dict):
            parsed['breakdowns'] = self._parse_nested_numeric(data['breakdowns'])
        
        if 'ratios' in data and isinstance(data['ratios'], dict):
            parsed['ratios'] = self._parse_nested_numeric(data['ratios'])
        
        return parsed
    
    def _parse_qc_dashboard_data(self, data: Dict) -> Dict:
        """Parse QC dashboard with time series data"""
        parsed = {}
        
        # Handle time series data
        if 'time_series' in data and isinstance(data['time_series'], dict):
            parsed['time_series'] = self._parse_time_series(data['time_series'])
        
        # Handle quarterly comparisons
        if 'quarterly_comparison' in data and isinstance(data['quarterly_comparison'], dict):
            parsed['quarterly_comparison'] = self._parse_nested_numeric(data['quarterly_comparison'])
        
        # Handle year-over-year data
        if 'yoy_comparison' in data and isinstance(data['yoy_comparison'], dict):
            parsed['yoy_comparison'] = self._parse_nested_numeric(data['yoy_comparison'])
        
        return parsed
    
    def _parse_income_risk_data(self, data: Dict) -> Dict:
        """Parse income and risk data with benchmarks"""
        parsed = {}
        
        # Parse bank data
        if 'bank' in data and isinstance(data['bank'], dict):
            parsed['bank'] = self._parse_nested_numeric(data['bank'])
        
        # Parse benchmark data
        if 'benchmark' in data and isinstance(data['benchmark'], dict):
            parsed['benchmark'] = self._parse_nested_numeric(data['benchmark'])
        
        # Parse risk metrics
        if 'risk_metrics' in data and isinstance(data['risk_metrics'], dict):
            parsed['risk_metrics'] = self._parse_nested_numeric(data['risk_metrics'])
        
        return parsed
    
    def _parse_dupont_data(self, data: Dict) -> Dict:
        """Parse DuPont analysis data"""
        parsed = {}
        
        # Parse DuPont components
        if 'components' in data and isinstance(data['components'], dict):
            parsed['components'] = self._parse_nested_numeric(data['components'])
        
        # Parse analysis results
        if 'analysis' in data and isinstance(data['analysis'], dict):
            parsed['analysis'] = self._parse_nested_numeric(data['analysis'])
        
        # Parse trend data
        if 'trends' in data and isinstance(data['trends'], dict):
            parsed['trends'] = self._parse_nested_numeric(data['trends'])
        
        return parsed
    
    def _parse_time_series(self, time_series_data: Dict) -> Dict:
        """Parse time series data"""
        parsed = {}
        
        for metric, values in time_series_data.items():
            if isinstance(values, list):
                parsed[metric] = [self._parse_numeric_value(v) for v in values]
            elif isinstance(values, dict):
                # Handle structured time series with dates
                parsed[metric] = {
                    'dates': values.get('dates', []),
                    'values': [self._parse_numeric_value(v) for v in values.get('values', [])]
                }
            else:
                parsed[metric] = values
        
        return parsed
    
    def _parse_nested_numeric(self, data: Dict) -> Dict:
        """Parse nested dictionary with numeric values"""
        parsed = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                parsed[key] = self._parse_nested_numeric(value)
            elif isinstance(value, list):
                parsed[key] = [self._parse_numeric_value(v) for v in value]
            else:
                parsed[key] = self._parse_numeric_value(value)
        
        return parsed
    
    def _parse_numeric_value(self, value) -> float:
        """Parse and validate numeric value"""
        if value is None:
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Clean string value
            cleaned = value.replace(',', '').replace('$', '').replace('%', '').strip()
            
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _validate_required_fields(self, data: Dict) -> None:
        """Validate that required fields are present"""
        for section, required_fields in self.required_fields.items():
            section_data = data.get(section, {})
            
            for field in required_fields:
                if field not in section_data or not section_data[field]:
                    raise ValueError(f"Required field '{field}' missing from {section}")
    
    def _clean_and_standardize(self, data: Dict) -> Dict:
        """Clean and standardize data format"""
        cleaned = {}
        
        for section_name, section_data in data.items():
            cleaned[section_name] = self._standardize_section(section_name, section_data)
        
        return cleaned
    
    def _standardize_section(self, section_name: str, section_data: Dict) -> Dict:
        """Standardize individual section format"""
        standardized = {}
        
        # Standardize field names and formats
        if section_name == 'dashboard':
            standardized = self._standardize_dashboard(section_data)
        elif section_name == 'qc_dashboard':
            standardized = self._standardize_qc_dashboard(section_data)
        elif section_name == 'income_risk':
            standardized = self._standardize_income_risk(section_data)
        elif section_name == 'dupont':
            standardized = self._standardize_dupont(section_data)
        else:
            standardized = section_data
        
        return standardized
    
    def _standardize_dashboard(self, data: Dict) -> Dict:
        """Standardize dashboard section"""
        standardized = data.copy()
        
        # Ensure bank name is properly formatted
        if 'bank_name' in standardized:
            standardized['bank_name'] = standardized['bank_name'].title()
        
        # Standardize period format
        if 'period' in standardized:
            period = standardized['period']
            # Try to standardize common period formats
            if 'Q' in period:
                # Quarterly format
                standardized['period'] = period.upper()
            elif len(period) == 4 and period.isdigit():
                # Year only
                standardized['period'] = f"FY {period}"
        
        # Ensure all numeric fields are float
        for field in self.numeric_fields['dashboard']:
            if field in standardized:
                standardized[field] = float(standardized[field])
        
        return standardized
    
    def _standardize_qc_dashboard(self, data: Dict) -> Dict:
        """Standardize QC dashboard section"""
        standardized = data.copy()
        
        # Ensure time series data is properly formatted
        if 'time_series' in standardized:
            standardized['time_series'] = self._standardize_time_series(standardized['time_series'])
        
        return standardized
    
    def _standardize_income_risk(self, data: Dict) -> Dict:
        """Standardize income and risk section"""
        standardized = data.copy()
        
        # Ensure bank and benchmark data have consistent structure
        for key in ['bank', 'benchmark']:
            if key in standardized:
                standardized[key] = self._ensure_numeric_fields(standardized[key])
        
        return standardized
    
    def _standardize_dupont(self, data: Dict) -> Dict:
        """Standardize DuPont analysis section"""
        standardized = data.copy()
        
        # Ensure all components are numeric
        for key in ['components', 'analysis', 'trends']:
            if key in standardized:
                standardized[key] = self._ensure_numeric_fields(standardized[key])
        
        return standardized
    
    def _standardize_time_series(self, time_series: Dict) -> Dict:
        """Standardize time series data"""
        standardized = {}
        
        for metric, values in time_series.items():
            if isinstance(values, list):
                # Ensure all values are numeric
                standardized[metric] = [float(v) if v is not None else 0.0 for v in values]
            elif isinstance(values, dict) and 'values' in values:
                # Handle structured time series
                standardized[metric] = {
                    'dates': values.get('dates', []),
                    'values': [float(v) if v is not None else 0.0 for v in values.get('values', [])]
                }
            else:
                standardized[metric] = values
        
        return standardized
    
    def _ensure_numeric_fields(self, data: Any) -> Any:
        """Ensure all numeric fields in nested structure are properly typed"""
        if isinstance(data, dict):
            return {k: self._ensure_numeric_fields(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._ensure_numeric_fields(item) for item in data]
        elif isinstance(data, (int, float, Decimal)):
            return float(data)
        elif isinstance(data, str):
            try:
                return float(data.replace(',', '').replace('$', '').replace('%', '').strip())
            except ValueError:
                return data
        else:
            return data
    
    def validate_data_quality(self, data: Dict) -> Dict:
        """
        Validate data quality and return quality metrics
        
        Args:
            data: Parsed financial data
            
        Returns:
            Quality assessment metrics
        """
        quality_score = 100
        issues = []
        warnings = []
        
        # Check dashboard completeness
        dashboard = data.get('dashboard', {})
        required_metrics = ['total_assets', 'total_equity', 'net_income']
        
        for metric in required_metrics:
            if metric not in dashboard or dashboard[metric] == 0:
                quality_score -= 15
                issues.append(f"Missing or zero value for {metric}")
        
        # Check for reasonable values
        if 'total_assets' in dashboard:
            if dashboard['total_assets'] <= 0:
                quality_score -= 20
                issues.append("Total assets should be positive")
            elif dashboard['total_assets'] < 1000000:  # Less than $1M
                warnings.append("Total assets seem unusually low")
        
        # Check time series data quality
        qc_dashboard = data.get('qc_dashboard', {})
        time_series = qc_dashboard.get('time_series', {})
        
        if not time_series:
            quality_score -= 10
            warnings.append("No time series data available for trend analysis")
        else:
            # Check time series length
            for metric, values in time_series.items():
                if isinstance(values, list) and len(values) < 3:
                    warnings.append(f"Time series for {metric} has limited data points")
        
        # Check benchmark data
        income_risk = data.get('income_risk', {})
        if not income_risk.get('benchmark'):
            quality_score -= 5
            warnings.append("No benchmark data available for comparison")
        
        # Check for data consistency
        if dashboard and income_risk.get('bank'):
            bank_metrics = income_risk['bank']
            # Check if key metrics are consistent between sections
            for metric in ['roa', 'roe']:
                if metric in dashboard and metric in bank_metrics:
                    diff = abs(float(dashboard[metric]) - float(bank_metrics[metric]))
                    if diff > 0.1:  # More than 0.1% difference
                        warnings.append(f"Inconsistent {metric} values between sections")
        
        return {
            'quality_score': max(0, quality_score),
            'issues': issues,
            'warnings': warnings,
            'completeness': self._calculate_completeness(data),
            'consistency': self._calculate_consistency(data)
        }
    
    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate data completeness percentage"""
        total_fields = 0
        populated_fields = 0
        
        # Dashboard completeness
        dashboard = data.get('dashboard', {})
        expected_dashboard_fields = len(self.numeric_fields['dashboard']) + 2  # + bank_name, period
        populated_dashboard = sum(1 for field in dashboard if field in dashboard and dashboard[field] is not None)
        
        total_fields += expected_dashboard_fields
        populated_fields += min(populated_dashboard, expected_dashboard_fields)
        
        # Time series completeness
        qc_dashboard = data.get('qc_dashboard', {})
        if qc_dashboard.get('time_series'):
            total_fields += 1
            populated_fields += 1
        
        # Benchmark completeness
        income_risk = data.get('income_risk', {})
        if income_risk.get('benchmark'):
            total_fields += 1
            populated_fields += 1
        
        return (populated_fields / total_fields * 100) if total_fields > 0 else 0
    
    def _calculate_consistency(self, data: Dict) -> float:
        """Calculate data consistency score"""
        consistency_score = 100
        
        dashboard = data.get('dashboard', {})
        income_risk = data.get('income_risk', {})
        
        # Check consistency between dashboard and income_risk bank data
        if income_risk.get('bank'):
            bank_data = income_risk['bank']
            
            # Check key metrics consistency
            for metric in ['roa', 'roe', 'efficiency_ratio']:
                if metric in dashboard and metric in bank_data:
                    try:
                        diff = abs(float(dashboard[metric]) - float(bank_data[metric]))
                        if diff > 0.5:  # More than 0.5% difference
                            consistency_score -= 10
                    except (ValueError, TypeError):
                        consistency_score -= 5
        
        return max(0, consistency_score)
