"""Report and insights endpoints."""

import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model

from .authentication import CsrfExemptSessionAuthentication

from ..models import UserSettings

from ..services.report_store import (
    archive_reports,
    delete_reports,
    get_report,
    list_report_ids,
    list_report_records,
    list_reports,
    restore_reports,
    update_report,
)
from ..services.report_prompt_registry import clear_report_prompt_registry_cache, get_report_prompt_registry
from ..services.prompt_settings_store import (
    build_prompt_config_payload,
    get_analysis_prompt,
    list_analysis_prompts,
    reset_all_analysis_prompts,
    reset_analysis_prompt,
    save_report_configuration,
    serialize_analysis_prompt,
    update_analysis_prompt_content,
    ensure_prompt_defaults,
)
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
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_report_prompt_config(request):
    """Return the editable prompt configuration."""
    ensure_prompt_defaults()
    config = build_prompt_config_payload()
    prompts = [serialize_analysis_prompt(prompt) for prompt in list_analysis_prompts()]
    return JsonResponse({
        'success': True,
        'config': config,
        'prompts': prompts,
        'is_admin': bool(request.user.is_staff or request.user.is_superuser),
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def update_report_prompt_config(request):
    """Persist report prompt configuration updates."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({'error': 'Configuration payload must be a JSON object'}, status=400)

    config = save_report_configuration(body, user=request.user)
    clear_report_prompt_registry_cache()
    prompts = [serialize_analysis_prompt(prompt) for prompt in list_analysis_prompts()]
    return JsonResponse({
        'success': True,
        'config': config,
        'prompts': prompts,
    })


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_analysis_prompts(request):
    """Return persisted AI analysis prompts for the Upload page."""
    ensure_prompt_defaults()
    return JsonResponse({
        'success': True,
        'is_admin': bool(request.user.is_staff or request.user.is_superuser),
        'prompts': [serialize_analysis_prompt(prompt) for prompt in list_analysis_prompts()],
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def update_analysis_prompt_view(request):
    """Update a single analysis prompt in the database."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    prompt_id = body.get('prompt_id')
    content = body.get('content', '')
    if not prompt_id:
        return JsonResponse({'error': 'prompt_id is required'}, status=400)
    if not str(content).strip():
        return JsonResponse({'error': 'Prompt content cannot be empty'}, status=400)

    try:
        prompt = update_analysis_prompt_content(prompt_id, str(content), user=request.user)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=404)

    clear_report_prompt_registry_cache()
    return JsonResponse({
        'success': True,
        'prompt': serialize_analysis_prompt(prompt),
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def reset_analysis_prompts_view(request):
    """Reset one or all analysis prompts to their built-in defaults."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    prompt_id = body.get('prompt_id', 'all')
    try:
        if prompt_id == 'all':
            prompts = reset_all_analysis_prompts(user=request.user)
        else:
            prompts = [reset_analysis_prompt(prompt_id, user=request.user)]
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=404)

    clear_report_prompt_registry_cache()
    return JsonResponse({
        'success': True,
        'prompts': [serialize_analysis_prompt(prompt) for prompt in prompts],
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_settings(request):
    """Return persisted settings for the authenticated user."""
    user = request.user
    try:
        us = UserSettings.objects.get(user=user)
        return JsonResponse({'success': True, 'settings': us.settings})
    except UserSettings.DoesNotExist:
        return JsonResponse({'success': True, 'settings': {} })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_user_settings(request):
    """Persist settings for the authenticated user."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({'error': 'Settings payload must be a JSON object'}, status=400)

    retention_days = body.get('retentionDays')
    retention_unit = body.get('retentionUnit')
    if retention_days is not None:
        try:
            retention_days = int(retention_days)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'retentionDays must be an integer'}, status=400)
        if retention_days < 1:
            return JsonResponse({'error': 'retentionDays must be greater than 0'}, status=400)
        body['retentionDays'] = retention_days

    if retention_unit is not None and retention_unit not in {'days', 'weeks', 'months'}:
        return JsonResponse({'error': 'retentionUnit must be days, weeks, or months'}, status=400)

    user = request.user
    us, _ = UserSettings.objects.get_or_create(user=user)
    # accept nested structure; overwrite stored settings
    us.settings = body
    us.save()
    return JsonResponse({'success': True, 'settings': us.settings})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_manageable_reports(request):
    """List reports for management table with filters."""
    search = request.query_params.get('search', '').strip()
    status = request.query_params.get('status', '').strip()
    include_archived = request.query_params.get('include_archived', 'true').lower() == 'true'
    records = list_report_records(
        request=request,
        include_archived=include_archived,
        search=search,
        status=status,
    )
    items = []
    for record in records:
        report = record.report_data or {}
        items.append({
            'id': str(record.id),
            'filename': report.get('filename'),
            'bank_name': report.get('bank_name'),
            'status': report.get('status', 'completed'),
            'ai_enhanced': report.get('ai_enhanced', False),
            'data_period': report.get('data_period'),
            'created_at': record.created_at.isoformat(),
            'updated_at': record.updated_at.isoformat(),
            'is_archived': record.is_archived,
            'archived_at': record.archived_at.isoformat() if record.archived_at else None,
            'title': report.get('metadata', {}).get('title') or report.get('filename') or str(record.id),
            'report_type': report.get('report_type') or report.get('metadata', {}).get('template_name') or 'analysis',
        })
    return JsonResponse({'success': True, 'results': items, 'count': len(items)})


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def bulk_report_action(request):
    """Archive, restore, or delete reports in bulk."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)

    action = str(body.get('action', '')).strip().lower()
    ids = body.get('report_ids') or []
    if action not in {'archive', 'restore', 'delete'}:
        return JsonResponse({'error': 'action must be one of: archive, restore, delete'}, status=400)
    if not isinstance(ids, list) or not ids:
        return JsonResponse({'error': 'report_ids must be a non-empty list'}, status=400)

    try:
        if action == 'archive':
            result = archive_reports(ids, request=request)
        elif action == 'restore':
            result = restore_reports(ids, request=request)
        else:
            result = delete_reports(ids, request=request)
    except ValueError:
        return JsonResponse({'error': 'Invalid report id in report_ids'}, status=400)

    return JsonResponse({'success': True, 'action': action, 'result': result})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_data_cleanup(request):
    """
    Trigger cleanup of old reports and uploads for the authenticated user.
    
    Query Parameters:
        - dry_run: bool (default: True). If true, preview without deleting.
    
    Returns:
        Cleanup results including number of items deleted.
    """
    try:
        from analytics.services.cleanup_service import cleanup_all_old_data
        
        dry_run = request.query_params.get('dry_run', 'true').lower() == 'true'
        
        result = cleanup_all_old_data(user=request.user, dry_run=dry_run)
        
        return JsonResponse({
            'success': True,
            'dry_run': dry_run,
            'result': result,
            'message': f"Cleanup completed: {result['total_deleted']} items processed"
        })
    
    except Exception as e:
        return JsonResponse(
            {'error': str(e), 'success': False},
            status=400
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_cleanup(request):
    """
    Preview what would be deleted based on user's retention settings.
    
    Returns:
        Dry-run cleanup results showing what would be deleted.
    """
    try:
        from analytics.services.cleanup_service import cleanup_all_old_data
        
        result = cleanup_all_old_data(user=request.user, dry_run=True)
        
        return JsonResponse({
            'success': True,
            'preview': True,
            'result': result,
            'message': f"{result['total_deleted']} items would be deleted"
        })
    
    except Exception as e:
        return JsonResponse(
            {'error': str(e), 'success': False},
            status=400
        )


@api_view(['POST'])
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
    'get_analysis_prompts',
    'update_analysis_prompt_view',
    'reset_analysis_prompts_view',
    'preview_report',
    'regenerate_insights',
    'update_report_prompt_config',
    'simple_custom_report_view',
    'simple_export_view',
    'simple_report_detail_view',
    'simple_reports_view',
    'trigger_data_cleanup',
    'preview_cleanup',
    'list_manageable_reports',
    'bulk_report_action',
]
