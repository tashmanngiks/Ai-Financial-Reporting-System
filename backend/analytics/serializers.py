"""
Serializers for the Financial Analytics API

Defines the data serialization format for all API endpoints.
"""

import json
from rest_framework import serializers
from .models import (
    FinancialDataUpload, FinancialDataSet, FinancialMetrics,
    FinancialInsight, FinancialReport, AnalysisTask
)


class FinancialDataUploadSerializer(serializers.ModelSerializer):
    """Serializer for financial data uploads"""
    
    class Meta:
        model = FinancialDataUpload
        fields = [
            'id', 'user', 'file', 'original_filename', 'status',
            'uploaded_at', 'processed_at', 'error_message'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'uploaded_at', 'processed_at', 'error_message'
        ]
    
    def validate_file(self, value):
        """Validate uploaded file"""
        if not value.name.endswith('.json'):
            raise serializers.ValidationError("Only JSON files are allowed.")
        
        # Check file size (50MB limit)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 50MB.")
        
        return value


class FinancialDataSetSerializer(serializers.ModelSerializer):
    """Serializer for parsed financial data sets"""
    
    class Meta:
        model = FinancialDataSet
        fields = [
            'id', 'upload', 'dashboard_data', 'qc_dashboard_data',
            'income_risk_data', 'dupont_data', 'data_period', 'bank_name',
            'created_at'
        ]
        read_only_fields = ['id', 'upload', 'created_at']


class FinancialMetricsSerializer(serializers.ModelSerializer):
    """Serializer for calculated financial metrics"""
    
    class Meta:
        model = FinancialMetrics
        fields = [
            'id', 'data_set', 'roa', 'roe', 'tier1_ratio', 'loss_rate',
            'efficiency_ratio', 'asset_growth', 'loan_growth', 'deposit_growth',
            'credit_risk_score', 'liquidity_ratio', 'capital_adequacy',
            'roa_vs_benchmark', 'roe_vs_benchmark', 'efficiency_vs_benchmark',
            'calculated_at'
        ]
        read_only_fields = ['id', 'data_set', 'calculated_at']


class FinancialInsightSerializer(serializers.ModelSerializer):
    """Serializer for AI-generated insights"""
    
    class Meta:
        model = FinancialInsight
        fields = [
            'id', 'data_set', 'insight_type', 'content', 'confidence_score',
            'key_points', 'created_at'
        ]
        read_only_fields = ['id', 'data_set', 'created_at']


class FinancialReportSerializer(serializers.ModelSerializer):
    """Serializer for complete financial reports"""
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'data_set', 'title', 'executive_summary', 'trend_analysis',
            'financial_performance', 'risk_assessment', 'benchmark_comparison',
            'recommendations', 'overall_score', 'risk_level',
            'generated_at', 'updated_at', 'structured_data'
        ]
        read_only_fields = [
            'id', 'data_set', 'generated_at', 'updated_at', 'structured_data'
        ]


class AnalysisTaskSerializer(serializers.ModelSerializer):
    """Serializer for analysis task tracking"""
    
    class Meta:
        model = AnalysisTask
        fields = [
            'id', 'upload', 'task_id', 'status', 'progress',
            'result_data', 'error_message', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'upload', 'task_id', 'status', 'progress',
            'created_at', 'completed_at'
        ]


class ReportSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for report listings"""
    
    bank_name = serializers.CharField(source='data_set.bank_name', read_only=True)
    data_period = serializers.CharField(source='data_set.data_period', read_only=True)
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'title', 'bank_name', 'data_period', 'overall_score',
            'risk_level', 'generated_at'
        ]


class UploadResponseSerializer(serializers.Serializer):
    """Response serializer for file upload endpoint"""
    
    upload_id = serializers.UUIDField()
    task_id = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()


class AnalysisRequestSerializer(serializers.Serializer):
    """Request serializer for analysis trigger"""
    
    upload_id = serializers.UUIDField()
    include_ai_insights = serializers.BooleanField(default=True)
    custom_benchmarks = serializers.JSONField(required=False)


class TaskStatusSerializer(serializers.Serializer):
    """Response serializer for task status"""
    
    task_id = serializers.CharField()
    status = serializers.CharField()
    progress = serializers.IntegerField()
    result_data = serializers.JSONField(required=False)
    error_message = serializers.CharField(required=False)
    estimated_completion = serializers.DateTimeField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response serializer"""
    
    error = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    timestamp = serializers.DateTimeField()


class SuccessResponseSerializer(serializers.Serializer):
    """Standard success response serializer"""
    
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(required=False)


# Detailed serializers for API responses

class DetailedReportSerializer(serializers.ModelSerializer):
    """Detailed report serializer with nested data"""
    
    insights = FinancialInsightSerializer(many=True, read_only=True, source='data_set.insights')
    metrics = FinancialMetricsSerializer(read_only=True, source='data_set.financialmetrics')
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'title', 'executive_summary', 'trend_analysis',
            'financial_performance', 'risk_assessment', 'benchmark_comparison',
            'recommendations', 'overall_score', 'risk_level',
            'structured_data', 'insights', 'metrics', 'generated_at', 'updated_at'
        ]


class MetricsSummarySerializer(serializers.Serializer):
    """Serializer for metrics summary"""
    
    profitability = serializers.DictField()
    risk_metrics = serializers.DictField()
    growth_metrics = serializers.DictField()
    capital_metrics = serializers.DictField()
    overall_assessment = serializers.DictField()


class TrendDataSerializer(serializers.Serializer):
    """Serializer for trend analysis data"""
    
    metric_name = serializers.CharField()
    values = serializers.ListField(child=serializers.FloatField())
    trend_direction = serializers.CharField()
    volatility = serializers.FloatField()
    recent_change = serializers.FloatField()


class BenchmarkComparisonSerializer(serializers.Serializer):
    """Serializer for benchmark comparison data"""
    
    metric_name = serializers.CharField()
    bank_value = serializers.FloatField()
    benchmark_value = serializers.FloatField()
    difference = serializers.FloatField()
    assessment = serializers.CharField()


class ExportRequestSerializer(serializers.Serializer):
    """Request serializer for report export"""
    
    report_id = serializers.UUIDField()
    format = serializers.ChoiceField(choices=['pdf', 'excel', 'json'])
    include_raw_data = serializers.BooleanField(default=False)
    include_charts = serializers.BooleanField(default=True)


class ValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation errors"""
    
    field = serializers.CharField()
    message = serializers.CharField()
    code = serializers.CharField(required=False)


class PaginatedResponseSerializer(serializers.Serializer):
    """Base serializer for paginated responses"""
    
    count = serializers.IntegerField()
    next = serializers.URLField(required=False)
    previous = serializers.URLField(required=False)
    results = serializers.ListField()


# Custom field serializers

class JSONField(serializers.JSONField):
    """Custom JSON field with better validation"""
    
    def to_internal_value(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format.")
        
        return super().to_internal_value(data)


class PercentageField(serializers.DecimalField):
    """Field for percentage values"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_digits', 10)
        kwargs.setdefault('decimal_places', 4)
        kwargs.setdefault('min_value', -999.9999)
        kwargs.setdefault('max_value', 999.9999)
        super().__init__(**kwargs)
    
    def to_representation(self, value):
        if value is not None:
            return float(value)
        return None


class ScoreField(serializers.DecimalField):
    """Field for scores (0-100)"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('max_digits', 5)
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('min_value', 0)
        kwargs.setdefault('max_value', 100)
        super().__init__(**kwargs)


# Utility serializers for nested data

class DashboardDataSerializer(serializers.Serializer):
    """Serializer for dashboard data validation"""
    
    bank_name = serializers.CharField(max_length=200)
    period = serializers.CharField(max_length=50)
    total_assets = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_equity = serializers.DecimalField(max_digits=20, decimal_places=2)
    net_income = serializers.DecimalField(max_digits=20, decimal_places=2)
    operating_income = serializers.DecimalField(max_digits=20, decimal_places=2)
    operating_expenses = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_loans = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_deposits = serializers.DecimalField(max_digits=20, decimal_places=2)
    liquid_assets = serializers.DecimalField(max_digits=20, decimal_places=2)
    loan_losses = serializers.DecimalField(max_digits=20, decimal_places=2)
    non_performing_loans = serializers.DecimalField(max_digits=20, decimal_places=2)
    tier1_capital = serializers.DecimalField(max_digits=20, decimal_places=2)
    risk_weighted_assets = serializers.DecimalField(max_digits=20, decimal_places=2)


class TimeSeriesDataSerializer(serializers.Serializer):
    """Serializer for time series data"""
    
    period = serializers.CharField()
    value = serializers.DecimalField(max_digits=20, decimal_places=2)


class QCDashboardSerializer(serializers.Serializer):
    """Serializer for QC dashboard data"""
    
    time_series = serializers.DictField(
        child=TimeSeriesDataSerializer(many=True)
    )


class BenchmarkDataSerializer(serializers.Serializer):
    """Serializer for benchmark data"""
    
    roa = serializers.DecimalField(max_digits=10, decimal_places=4)
    roe = serializers.DecimalField(max_digits=10, decimal_places=4)
    efficiency_ratio = serializers.DecimalField(max_digits=10, decimal_places=4)
    tier1_ratio = serializers.DecimalField(max_digits=10, decimal_places=4)


class IncomeRiskSerializer(serializers.Serializer):
    """Serializer for income and risk data"""
    
    bank = BenchmarkDataSerializer()
    benchmark = BenchmarkDataSerializer()


class DupontSerializer(serializers.Serializer):
    """Serializer for DuPont analysis data"""
    
    components = serializers.DictField()
    analysis = serializers.DictField()


# Request/Response serializers for specific endpoints

class FileUploadRequestSerializer(serializers.Serializer):
    """Request serializer for file upload"""
    
    file = serializers.FileField()
    description = serializers.CharField(max_length=500, required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class AnalysisOptionsSerializer(serializers.Serializer):
    """Serializer for analysis options"""
    
    include_benchmarks = serializers.BooleanField(default=True)
    include_trends = serializers.BooleanField(default=True)
    include_ai_insights = serializers.BooleanField(default=True)
    custom_prompts = serializers.DictField(required=False)
    analysis_depth = serializers.ChoiceField(
        choices=['basic', 'standard', 'comprehensive'],
        default='standard'
    )


class ReportFilterSerializer(serializers.Serializer):
    """Serializer for report filtering"""
    
    bank_name = serializers.CharField(required=False)
    risk_level = serializers.ChoiceField(
        choices=['low', 'moderate', 'high', 'critical'],
        required=False
    )
    min_score = serializers.IntegerField(min_value=0, max_value=100, required=False)
    max_score = serializers.IntegerField(min_value=0, max_value=100, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    ordering = serializers.ChoiceField(
        choices=['-generated_at', 'generated_at', '-overall_score', 'overall_score'],
        default='-generated_at'
    )
