import json
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


class FinancialDataUpload(models.Model):
    """Store uploaded financial data files"""
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='financial_data/',
        validators=[FileExtensionValidator(allowed_extensions=['json'])]
    )
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']


class FinancialDataSet(models.Model):
    """Store parsed financial data structure"""
    upload = models.OneToOneField(FinancialDataUpload, on_delete=models.CASCADE)
    
    # Raw JSON data
    dashboard_data = models.JSONField(null=True, blank=True)
    qc_dashboard_data = models.JSONField(null=True, blank=True)
    income_risk_data = models.JSONField(null=True, blank=True)
    dupont_data = models.JSONField(null=True, blank=True)
    
    # Metadata
    data_period = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bank_name} - {self.data_period}"


class FinancialMetrics(models.Model):
    """Store calculated financial metrics"""
    data_set = models.OneToOneField(FinancialDataSet, on_delete=models.CASCADE)
    
    # Key Performance Indicators
    roa = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Return on Assets
    roe = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)  # Return on Equity
    tier1_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    loss_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    efficiency_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Growth rates
    asset_growth = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    loan_growth = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    deposit_growth = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Risk metrics
    credit_risk_score = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    liquidity_ratio = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    capital_adequacy = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # Benchmark comparisons
    roa_vs_benchmark = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    roe_vs_benchmark = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    efficiency_vs_benchmark = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-calculated_at']


class FinancialInsight(models.Model):
    """Store AI-generated insights"""
    data_set = models.ForeignKey(FinancialDataSet, on_delete=models.CASCADE, related_name='insights')
    
    INSIGHT_TYPES = [
        ('executive_summary', 'Executive Summary'),
        ('trend_analysis', 'Trend Analysis'),
        ('risk_assessment', 'Risk Assessment'),
        ('benchmark_comparison', 'Benchmark Comparison'),
        ('recommendations', 'Recommendations'),
        ('strengths_weaknesses', 'Strengths and Weaknesses'),
    ]
    
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    content = models.TextField()
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    key_points = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['insight_type', '-created_at']
        unique_together = ['data_set', 'insight_type']


class FinancialReport(models.Model):
    """Complete financial analysis report"""
    data_set = models.OneToOneField(FinancialDataSet, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=200)
    executive_summary = models.TextField()
    trend_analysis = models.TextField()
    financial_performance = models.TextField()
    risk_assessment = models.TextField()
    benchmark_comparison = models.TextField()
    recommendations = models.TextField()
    
    # Report metadata
    overall_score = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('moderate', 'Moderate'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        null=True, blank=True
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Report structure as JSON for API consumption
    structured_data = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Report: {self.title}"
    
    class Meta:
        ordering = ['-generated_at']


class PersistedReport(models.Model):
    """Persist uploaded AI reports across sessions and server restarts."""
    id = models.UUIDField(primary_key=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='persisted_reports')
    owner_username = models.CharField(max_length=150, blank=True, default='')
    report_data = models.JSONField(default=dict)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        title = self.report_data.get('metadata', {}).get('title', self.report_data.get('filename', str(self.id)))
        return f"Report: {title}"


class DataRetentionAuditLog(models.Model):
    """Audit log for report retention and management actions."""

    ACTION_CHOICES = [
        ('cleanup', 'Cleanup'),
        ('delete', 'Delete'),
        ('archive', 'Archive'),
        ('restore', 'Restore'),
        ('settings_update', 'Settings Update'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='retention_audit_logs')
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    report_ids = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        actor = self.user.username if self.user else 'system'
        return f'{self.action} by {actor} at {self.created_at}'


class AnalysisTask(models.Model):
    """Track async analysis tasks"""
    upload = models.OneToOneField(FinancialDataUpload, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    progress = models.IntegerField(default=0)
    result_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']


class UserSettings(models.Model):
    """Per-user persisted settings stored as JSON."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_settings')
    settings = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"


class AnalysisPrompt(models.Model):
    """Persisted AI analysis prompt editable from the Upload page."""
    prompt_id = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    default_content = models.TextField()
    recommended_sections = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_analysis_prompts',
    )

    class Meta:
        ordering = ['prompt_id']

    def __str__(self):
        return self.title


class ReportConfiguration(models.Model):
    """Singleton report template and section configuration."""
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    section_library = models.JSONField(default=dict, blank=True)
    templates = models.JSONField(default=dict, blank=True)
    default_length = models.CharField(max_length=20, default='standard')
    default_detail_level = models.CharField(max_length=20, default='balanced')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Report configurations'

    def __str__(self):
        return 'Report configuration'
