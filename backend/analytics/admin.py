from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import (
    FinancialDataUpload, FinancialDataSet, FinancialMetrics,
    FinancialInsight, FinancialReport, AnalysisTask
)


@admin.register(FinancialDataUpload)
class FinancialDataUploadAdmin(admin.ModelAdmin):
    """Admin interface for financial data uploads"""
    
    list_display = [
        'original_filename', 'user', 'status', 'uploaded_at', 
        'processed_at', 'file_size_display'
    ]
    list_filter = ['status', 'uploaded_at', 'user']
    search_fields = ['original_filename', 'user__username']
    readonly_fields = ['uploaded_at', 'processed_at', 'file_size_display']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Upload Information', {
            'fields': ('user', 'file', 'original_filename', 'status')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    
    def file_size_display(self, obj):
        """Display file size in human readable format"""
        if obj.file:
            size = obj.file.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "No file"
    file_size_display.short_description = "File Size"


@admin.register(FinancialDataSet)
class FinancialDataSetAdmin(admin.ModelAdmin):
    """Admin interface for financial data sets"""
    
    list_display = [
        'bank_name', 'data_period', 'upload', 'created_at', 
        'data_quality_display', 'report_link'
    ]
    list_filter = ['data_period', 'created_at', 'upload__user']
    search_fields = ['bank_name', 'data_period', 'upload__user__username']
    readonly_fields = ['created_at', 'data_preview']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('upload', 'bank_name', 'data_period')
        }),
        ('Data Preview', {
            'fields': ('data_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def data_quality_display(self, obj):
        """Display data quality assessment"""
        # Simple quality check based on data completeness
        quality_score = 100
        if not obj.dashboard_data:
            quality_score -= 30
        if not obj.qc_dashboard_data:
            quality_score -= 25
        if not obj.income_risk_data:
            quality_score -= 25
        if not obj.dupont_data:
            quality_score -= 20
        
        color = 'green' if quality_score >= 80 else 'orange' if quality_score >= 60 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}/100</span>',
            color, quality_score
        )
    data_quality_display.short_description = "Data Quality"
    
    def data_preview(self, obj):
        """Display preview of data structure"""
        preview = {}
        
        if obj.dashboard_data:
            preview['dashboard'] = list(obj.dashboard_data.keys())[:5]
        if obj.qc_dashboard_data:
            preview['qc_dashboard'] = list(obj.qc_dashboard_data.keys())[:5]
        if obj.income_risk_data:
            preview['income_risk'] = list(obj.income_risk_data.keys())[:5]
        if obj.dupont_data:
            preview['dupont'] = list(obj.dupont_data.keys())[:5]
        
        return format_html(
            '<pre>{}</pre>',
            json.dumps(preview, indent=2)
        )
    data_preview.short_description = "Data Structure Preview"
    
    def report_link(self, obj):
        """Link to associated report if exists"""
        try:
            report = FinancialReport.objects.get(data_set=obj)
            url = reverse('admin:analytics_financialreport_change', args=[report.id])
            return format_html('<a href="{}">View Report</a>', url)
        except FinancialReport.DoesNotExist:
            return "No Report"
    report_link.short_description = "Report"


@admin.register(FinancialMetrics)
class FinancialMetricsAdmin(admin.ModelAdmin):
    """Admin interface for financial metrics"""
    
    list_display = [
        'data_set_link', 'roa_display', 'roe_display', 'efficiency_ratio',
        'credit_risk_score', 'calculated_at'
    ]
    list_filter = ['calculated_at', 'data_set__data_period']
    search_fields = ['data_set__bank_name', 'data_set__data_period']
    readonly_fields = ['calculated_at']
    ordering = ['-calculated_at']
    
    fieldsets = (
        ('Data Set', {
            'fields': ('data_set',)
        }),
        ('Profitability Metrics', {
            'fields': ('roa', 'roe', 'efficiency_ratio')
        }),
        ('Capital Metrics', {
            'fields': ('tier1_ratio', 'capital_adequacy')
        }),
        ('Risk Metrics', {
            'fields': ('credit_risk_score', 'liquidity_ratio', 'loss_rate')
        }),
        ('Growth Metrics', {
            'fields': ('asset_growth', 'loan_growth', 'deposit_growth')
        }),
        ('Benchmark Comparisons', {
            'fields': ('roa_vs_benchmark', 'roe_vs_benchmark', 'efficiency_vs_benchmark')
        }),
        ('Timestamp', {
            'fields': ('calculated_at',)
        })
    )
    
    def data_set_link(self, obj):
        """Link to data set"""
        url = reverse('admin:analytics_financialdataset_change', args=[obj.data_set.id])
        return format_html('<a href="{}">{} - {}</a>', url, 
                          obj.data_set.bank_name, obj.data_set.data_period)
    data_set_link.short_description = "Data Set"
    
    def roa_display(self, obj):
        """Display ROA with color coding"""
        if obj.roa is None:
            return "N/A"
        color = 'green' if obj.roa > 1.0 else 'orange' if obj.roa > 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, obj.roa
        )
    roa_display.short_description = "ROA"
    
    def roe_display(self, obj):
        """Display ROE with color coding"""
        if obj.roe is None:
            return "N/A"
        color = 'green' if obj.roe > 10 else 'orange' if obj.roe > 5 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}%</span>',
            color, obj.roe
        )
    roe_display.short_description = "ROE"


@admin.register(FinancialInsight)
class FinancialInsightAdmin(admin.ModelAdmin):
    """Admin interface for financial insights"""
    
    list_display = [
        'data_set_link', 'insight_type', 'confidence_score_display', 
        'key_points_count', 'created_at'
    ]
    list_filter = ['insight_type', 'created_at', 'confidence_score']
    search_fields = ['data_set__bank_name', 'content']
    readonly_fields = ['created_at', 'content_preview']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Insight Information', {
            'fields': ('data_set', 'insight_type', 'confidence_score')
        }),
        ('Content', {
            'fields': ('content_preview', 'content'),
            'classes': ('collapse',)
        }),
        ('Key Points', {
            'fields': ('key_points',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )
    
    def data_set_link(self, obj):
        """Link to data set"""
        url = reverse('admin:analytics_financialdataset_change', args=[obj.data_set.id])
        return format_html('<a href="{}">{} - {}</a>', url, 
                          obj.data_set.bank_name, obj.data_set.data_period)
    data_set_link.short_description = "Data Set"
    
    def confidence_score_display(self, obj):
        """Display confidence score with color coding"""
        if obj.confidence_score is None:
            return "N/A"
        color = 'green' if obj.confidence_score > 0.8 else 'orange' if obj.confidence_score > 0.6 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            color, obj.confidence_score
        )
    confidence_score_display.short_description = "Confidence"
    
    def key_points_count(self, obj):
        """Count of key points"""
        return len(obj.key_points) if obj.key_points else 0
    key_points_count.short_description = "Key Points"
    
    def content_preview(self, obj):
        """Preview of content"""
        if obj.content:
            preview = obj.content[:200]
            if len(obj.content) > 200:
                preview += "..."
            return format_html('<div style="max-height: 100px; overflow-y: auto;">{}</div>', 
                             preview.replace('\n', '<br>'))
        return "No content"
    content_preview.short_description = "Content Preview"


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    """Admin interface for financial reports"""
    
    list_display = [
        'title', 'bank_name', 'data_period', 'overall_score_display',
        'risk_level_display', 'generated_at'
    ]
    list_filter = ['risk_level', 'generated_at', 'data_set__data_period']
    search_fields = ['title', 'data_set__bank_name']
    readonly_fields = ['generated_at', 'updated_at', 'report_summary']
    ordering = ['-generated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('data_set', 'title', 'overall_score', 'risk_level')
        }),
        ('Report Sections', {
            'fields': (
                'executive_summary', 'trend_analysis', 'financial_performance',
                'risk_assessment', 'benchmark_comparison', 'recommendations'
            ),
            'classes': ('collapse',)
        }),
        ('Report Summary', {
            'fields': ('report_summary',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('generated_at', 'updated_at')
        })
    )
    
    def bank_name(self, obj):
        """Display bank name"""
        return obj.data_set.bank_name if obj.data_set else "N/A"
    bank_name.short_description = "Bank"
    
    def data_period(self, obj):
        """Display data period"""
        return obj.data_set.data_period if obj.data_set else "N/A"
    data_period.short_description = "Period"
    
    def overall_score_display(self, obj):
        """Display overall score with color coding"""
        if obj.overall_score is None:
            return "N/A"
        color = 'green' if obj.overall_score >= 70 else 'orange' if obj.overall_score >= 50 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}/100</span>',
            color, obj.overall_score
        )
    overall_score_display.short_description = "Score"
    
    def risk_level_display(self, obj):
        """Display risk level with color coding"""
        colors = {
            'low': 'green',
            'moderate': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.risk_level, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.risk_level.title() if obj.risk_level else "N/A"
        )
    risk_level_display.short_description = "Risk Level"
    
    def report_summary(self, obj):
        """Display report summary"""
        if not obj.structured_data:
            return "No structured data"
        
        summary = {
            'sections': list(obj.structured_data.keys()),
            'metadata': obj.structured_data.get('metadata', {}),
            'key_metrics_count': len(obj.structured_data.get('key_metrics', {})),
            'insights_count': len(obj.data_set.insights.all()) if obj.data_set else 0
        }
        
        return format_html(
            '<pre>{}</pre>',
            json.dumps(summary, indent=2)
        )
    report_summary.short_description = "Report Summary"


@admin.register(AnalysisTask)
class AnalysisTaskAdmin(admin.ModelAdmin):
    """Admin interface for analysis tasks"""
    
    list_display = [
        'task_id', 'upload_link', 'status_display', 'progress_bar',
        'created_at', 'completed_at', 'result_summary'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['task_id', 'upload__original_filename', 'upload__user__username']
    readonly_fields = ['task_id', 'created_at', 'completed_at', 'result_data_display']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('upload', 'task_id', 'status', 'progress')
        }),
        ('Results', {
            'fields': ('result_data_display', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        })
    )
    
    def upload_link(self, obj):
        """Link to upload"""
        url = reverse('admin:analytics_financialdataupload_change', args=[obj.upload.id])
        return format_html('<a href="{}">{}</a>', url, obj.upload.original_filename)
    upload_link.short_description = "Upload"
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.status.title()
        )
    status_display.short_description = "Status"
    
    def progress_bar(self, obj):
        """Display progress as a bar"""
        if obj.progress is None:
            return "N/A"
        
        color = 'green' if obj.progress >= 80 else 'orange' if obj.progress >= 40 else 'red'
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 3px; '
            'display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">'
            '{}%</div></div>',
            obj.progress, color, obj.progress
        )
    progress_bar.short_description = "Progress"
    
    def result_data_display(self, obj):
        """Display result data"""
        if obj.result_data:
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.result_data, indent=2)
            )
        return "No result data"
    result_data_display.short_description = "Result Data"
    
    def result_summary(self, obj):
        """Display summary of results"""
        if obj.status == 'completed' and obj.result_data:
            return format_html(
                'Report ID: {}, Score: {}, Risk: {}',
                obj.result_data.get('report_id', 'N/A'),
                obj.result_data.get('overall_score', 'N/A'),
                obj.result_data.get('risk_level', 'N/A')
            )
        elif obj.status == 'failed':
            return format_html(
                '<span style="color: red;">{}</span>',
                obj.error_message[:50] + "..." if len(obj.error_message) > 50 else obj.error_message
            )
        else:
            return "In Progress"
    result_summary.short_description = "Result Summary"


# Customize admin site
admin.site.site_header = "AI Financial Analytics Administration"
admin.site.site_title = "Analytics Admin"
admin.site.index_title = "Welcome to AI Financial Analytics Administration"
