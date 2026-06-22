"""Report and insights endpoints."""

import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from ..services.report_store import get_report, list_report_ids, list_reports, update_report
from ..services.report_prompt_registry import get_report_prompt_registry
from ..views import (
    BenchmarkComparisonView,
    CustomReportView,
    ExportReportView,
    FinancialReportViewSet,
    MetricsSummaryView,
    ReportDetailView,
    TrendAnalysisView,
    get_insights,
    regenerate_insights,
    count_report_words,
    generate_analysis_from_prompt,
    generate_csv_report,
    generate_excel_report,
    generate_pdf_report,
    generate_report_sections,
    generate_word_report,
)


@csrf_exempt
@require_http_methods(["GET"])
def simple_reports_view(request):
    """Return stored reports from the shared report store."""
    reports = list_reports(request)
    return JsonResponse({
        'results': reports,
        'count': len(reports),
        'debug': {
            'report_ids': list_report_ids(),
            'source': 'database',
        },
    })


@csrf_exempt
@require_http_methods(["GET"])
def simple_report_detail_view(request, report_id):
    """Return a single report from the shared report store."""
    report = get_report(str(report_id))
    if not report:
        return JsonResponse({
            'error': 'Report not found',
            'report_id': str(report_id),
            'message': 'No matching report is available. Please upload a financial data file first.',
            'debug': {
                'available_ids': list_report_ids(),
            },
        }, status=404)

    return JsonResponse(report)


def _resolve_export_format(request):
    """Read export format from query string, form body, or JSON body."""
    format_type = request.GET.get('format')
    if format_type:
        return format_type

    if request.POST.get('format'):
        return request.POST.get('format')

    try:
        body = json.loads(request.body or b'{}')
        if isinstance(body, dict) and body.get('format'):
            return body.get('format')
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass

    return 'json'


def _normalize_export_format(format_type):
    """Map URL aliases to canonical export format names."""
    if not format_type:
        return 'json'

    normalized = str(format_type).lower().strip()
    aliases = {
        'docx': 'word',
        'doc': 'word',
        'xlsx': 'excel',
        'print': 'pdf',
        'editable': 'word',
    }
    return aliases.get(normalized, normalized)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def simple_export_view(request, report_id, file_type=None):
    """Download a stored report in the requested format."""
    report = get_report(str(report_id))
    if not report:
        return JsonResponse({
            'error': 'Report not found',
            'report_id': str(report_id),
            'available_ids': list_report_ids(),
        }, status=404)

    export_data = {
        'report_id': report.get('id'),
        'filename': report.get('filename'),
        'bank_name': report.get('bank_name'),
        'data_period': report.get('data_period'),
        'generated_at': report.get('uploaded_at') or report.get('metadata', {}).get('generated_at'),
        'user_prompt': report.get('user_prompt') or report.get('metadata', {}).get('user_prompt'),
        'ai_enhanced': report.get('ai_enhanced', False),
        'data_summary': report.get('data_summary'),
        'ai_analysis': report.get('ai_analysis'),
        'comprehensive_analysis': report.get('comprehensive_analysis', []),
        'metadata': report.get('metadata'),
        'export_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    format_type = _normalize_export_format(file_type or _resolve_export_format(request))

    if format_type == 'json':
        response = JsonResponse(export_data)
        response['Content-Disposition'] = f'attachment; filename="financial_report_{report_id}.json"'
        response['Content-Type'] = 'application/json'
        return response

    if format_type == 'pdf':
        content = generate_pdf_report(report)
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="financial_report_{report_id}.pdf"'
        return response

    if format_type == 'csv':
        content = generate_csv_report(report)
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="financial_report_{report_id}.csv"'
        return response

    if format_type == 'word':
        content = generate_word_report(report)
        response = HttpResponse(
            content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        response['Content-Disposition'] = f'attachment; filename="financial_report_{report_id}.docx"'
        return response

    if format_type == 'excel':
        content = generate_excel_report(report)
        response = HttpResponse(
            content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="financial_report_{report_id}.xlsx"'
        return response

    return JsonResponse({'error': f'Unsupported format: {format_type}'}, status=400)


@api_view(['GET'])
@permission_classes([])
def get_report_templates(request):
    """Get available report templates."""
    registry = get_report_prompt_registry()
    return JsonResponse({
        'success': True,
        'templates': registry.get_templates(),
        'section_library': registry.get_section_library(),
    })


@api_view(['GET'])
@permission_classes([])
def get_report_prompt_config(request):
    """Return the editable prompt configuration."""
    registry = get_report_prompt_registry()
    return JsonResponse({
        'success': True,
        'config': registry.load(),
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_report_prompt_config(request):
    """Persist report prompt configuration updates."""
    registry = get_report_prompt_registry()
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({'error': 'Configuration payload must be a JSON object'}, status=400)

    return JsonResponse({
        'success': True,
        'config': registry.save(body),
    })


@api_view(['POST'])
@permission_classes([])
def generate_comprehensive_report(request, report_id):
    """Generate comprehensive financial report."""
    try:
        body = json.loads(request.body) if request.method == 'POST' else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    registry = get_report_prompt_registry()
    report_options = registry.build_report_options({
        'template': body.get('template', 'standard'),
        'sections': body.get('sections') or body.get('selected_sections') or [],
        'include_sections': body.get('include_sections') or [],
        'exclude_sections': body.get('exclude_sections') or [],
        'length': body.get('length'),
        'detail_level': body.get('detail_level'),
        'output_format': body.get('format', 'json'),
    })
    template_type = report_options.get('template', 'custom')
    format_type = report_options.get('output_format', 'json')
    report = get_report(str(report_id))

    if not report:
        return JsonResponse({'error': 'Report not found'}, status=404)

    templates = registry.get_templates()
    template = templates.get(template_type, templates.get('custom', {}))
    sections = report_options['sections'] or template.get('sections', [])
    generated_report = {
        'report_id': str(report_id),
        'template_used': template_type,
        'sections': generate_report_sections(sections, report),
        'metadata': {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'template_version': '1.0',
            'word_count': count_report_words(report),
            'report_options': report_options,
        },
    }

    if format_type == 'json':
        return JsonResponse(generated_report)

    if format_type == 'pdf':
        content = generate_pdf_report(generated_report)
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="comprehensive_report_{report_id}.pdf"'
        return response

    if format_type == 'word':
        content = generate_word_report(generated_report)
        response = HttpResponse(
            content,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        response['Content-Disposition'] = f'attachment; filename="comprehensive_report_{report_id}.docx"'
        return response

    return JsonResponse({'error': f'Unsupported format: {format_type}'}, status=400)


@api_view(['GET'])
@permission_classes([])
def preview_report(request, report_id):
    """Preview report before generation."""
    report = get_report(str(report_id))
    if not report:
        return JsonResponse({'error': 'Report not found'}, status=404)
    registry = get_report_prompt_registry()

    preview_data = {
        'report_id': str(report_id),
        'bank_name': report.get('bank_name'),
        'data_period': report.get('data_period'),
        'preview_sections': generate_report_sections(['executive_summary', 'statistical_highlights'], report),
        'available_templates': registry.get_templates(),
    }
    return JsonResponse(preview_data)


@csrf_exempt
@require_http_methods(["POST"])
def simple_custom_report_view(request, report_id=None):
    """AI-powered custom report view using stored report data."""
    try:
        data = json.loads(request.body) if request.body else {}
        prompt = data.get('prompt', '')
        report_options = data.get('report_options') or {
            'template': data.get('template'),
            'sections': data.get('sections') or data.get('selected_sections') or [],
            'include_sections': data.get('include_sections') or [],
            'exclude_sections': data.get('exclude_sections') or [],
            'length': data.get('length'),
            'detail_level': data.get('detail_level'),
            'output_format': data.get('format'),
        }
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    if not prompt:
        return JsonResponse({'error': 'Prompt is required'}, status=400)

    if not report_id:
        return JsonResponse({'error': 'Report ID is required'}, status=400)

    report = get_report(str(report_id))
    if not report:
        return JsonResponse({'error': 'Report not found'}, status=404)

    original_json = report.get('metadata', {}).get('original_json')
    if not original_json:
        return JsonResponse({'error': 'Original JSON data not found in report'}, status=400)

    sections, error_msg, ai_enhanced = generate_analysis_from_prompt(
        prompt,
        original_json,
        report.get('ai_analysis', {}),
        report_options=report_options,
    )

    if sections and ai_enhanced:
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        metadata = dict(report.get('metadata', {}))
        metadata.update({
            'user_prompt': prompt,
            'comprehensive_generated': True,
            'generated_at': generated_at,
        })
        update_report(str(report_id), {
            'comprehensive_analysis': sections,
            'user_prompt': prompt,
            'ai_enhanced': True,
            'status': 'completed',
            'metadata': metadata,
        }, request=request)
        return JsonResponse({
            'success': True,
            'report_id': str(report_id),
            'comprehensive_analysis': sections,
            'generated_at': generated_at,
            'prompt': prompt,
        })

    return JsonResponse({
        'success': False,
        'error': error_msg or 'AI analysis failed',
    }, status=500)

__all__ = [
    'BenchmarkComparisonView',
    'CustomReportView',
    'ExportReportView',
    'FinancialReportViewSet',
    'MetricsSummaryView',
    'ReportDetailView',
    'TrendAnalysisView',
    'generate_comprehensive_report',
    'get_insights',
    'get_report_templates',
    'get_report_prompt_config',
    'preview_report',
    'regenerate_insights',
    'update_report_prompt_config',
    'simple_custom_report_view',
    'simple_export_view',
    'simple_report_detail_view',
    'simple_reports_view',
]
