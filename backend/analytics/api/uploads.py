"""Upload and analysis endpoints."""

import json
import uuid
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.report_store import get_report, save_report
from ..views import (
    AnalysisStatusView,
    FinancialDataUploadView,
    analyze_direct_data,
    build_data_summary,
    extract_entity_metadata,
    generate_analysis_from_prompt,
    generate_comprehensive_ai_analysis,
    normalize_json_for_analysis,
    perform_initial_ai_analysis,
)


@csrf_exempt
@require_http_methods(["POST"])
def simple_custom_prompt_view(request):
    """Generate analysis using custom prompt on uploaded JSON data."""
    try:
        body = json.loads(request.body)
        report_id = body.get('report_id')
        custom_prompt = body.get('prompt')
        report_options = body.get('report_options') or {}

        if not report_id or not custom_prompt:
            return JsonResponse({'error': 'report_id and prompt are required'}, status=400)

        report = get_report(str(report_id))
        if not report:
            return JsonResponse({'error': 'Report not found'}, status=404)

        original_json = report.get('metadata', {}).get('original_json')
        if not original_json:
            return JsonResponse({'error': 'Original JSON data not found in report'}, status=400)

        analysis_result = generate_comprehensive_ai_analysis({
            'bank_name': report.get('bank_name', 'Unknown Bank'),
            'data_period': report.get('data_period', 'Unknown Period'),
            'financial_data': original_json,
            'existing_analysis': report.get('ai_analysis', {}),
            'data_summary': {
                'keys_found': list(original_json.keys()) if isinstance(original_json, dict) else 'Non-dict JSON',
                'data_size': len(str(original_json)),
                'sample_data': original_json if isinstance(original_json, dict) else {'data': original_json},
            },
            'user_prompt': custom_prompt,
            'report_options': report_options,
        })

        if analysis_result and analysis_result.get('success'):
            return JsonResponse({
                'success': True,
                'analysis': analysis_result.get('sections', []),
                'report_id': report_id,
            })

        error_msg = analysis_result.get('error', 'Unknown error') if analysis_result else 'Unknown error'
        return JsonResponse({'success': False, 'error': error_msg}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def simple_upload_view(request):
    """Simple Django upload view - no DRF."""
    try:
        body = {}
        if request.body:
            try:
                body = json.loads(request.body)
            except json.JSONDecodeError:
                body = {}

        report_options = {}
        raw_report_options = request.POST.get('report_options') or body.get('report_options')
        if raw_report_options:
            try:
                report_options = json.loads(raw_report_options) if isinstance(raw_report_options, str) else raw_report_options
            except json.JSONDecodeError:
                report_options = {}

        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']
        description = request.POST.get('description', '')
        prompt = request.POST.get('prompt', '').strip()

        if not prompt:
            return JsonResponse({
                'error': 'Analysis prompt is required. Describe what you want in the report.',
            }, status=400)

        if not uploaded_file.name.endswith('.json'):
            return JsonResponse({'error': 'Only JSON files are supported'}, status=400)

        file_content = uploaded_file.read().decode('utf-8')
        json_data = json.loads(file_content)

        if json_data is None:
            return JsonResponse({'error': 'JSON file is empty'}, status=400)

        normalized_json, original_json = normalize_json_for_analysis(json_data)
        bank_name, data_period = extract_entity_metadata(json_data)

        report_id = str(uuid.uuid4())
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ai_analysis = perform_initial_ai_analysis(json_data)

        full_ai_analysis, ai_error_msg, ai_enhanced = generate_analysis_from_prompt(
            prompt,
            original_json,
            ai_analysis,
            report_options=report_options or {
                'template': request.POST.get('template') or body.get('template'),
                'sections': body.get('sections') or request.POST.get('sections') or [],
                'include_sections': body.get('include_sections') or request.POST.get('include_sections') or [],
                'exclude_sections': body.get('exclude_sections') or request.POST.get('exclude_sections') or [],
                'length': body.get('length') or request.POST.get('length'),
                'detail_level': body.get('detail_level') or request.POST.get('detail_level'),
                'output_format': body.get('output_format') or request.POST.get('output_format'),
            },
        )
        comprehensive_generated = len(full_ai_analysis) > 0 and ai_enhanced

        prompt_title = prompt.strip().split('\n')[0].strip()
        if prompt_title.startswith('#'):
            prompt_title = prompt_title.lstrip('#').strip()
        prompt_title = prompt_title[:120] or f'{bank_name} Analysis'

        report_data = {
            'id': report_id,
            'filename': uploaded_file.name,
            'size': uploaded_file.size,
            'description': description,
            'user_prompt': prompt,
            'task_id': report_id,
            'uploaded_at': current_time,
            'status': 'completed',
            'data_summary': {
                **build_data_summary(original_json),
                'ai_insights': ai_analysis,
            },
            'bank_name': bank_name,
            'data_period': data_period,
            'ai_analysis': ai_analysis,
            'comprehensive_analysis': full_ai_analysis,
            'ai_enhanced': ai_enhanced,
            'metadata': {
                'title': prompt_title,
                'report_date': current_time,
                'period': data_period,
                'generated_at': current_time,
                'ai_processed': comprehensive_generated,
                'comprehensive_generated': comprehensive_generated,
                'ai_enhanced': ai_enhanced,
                'user_prompt': prompt,
                'original_json': original_json,
                'normalized_json': normalized_json,
            },
        }

        if ai_error_msg:
            report_data['ai_error'] = ai_error_msg

        save_report(report_id, report_data, request=request)

        response_data = {
            'success': True,
            'message': 'Report generated from your analysis prompt'
            if comprehensive_generated
            else 'Report uploaded successfully, but AI-enhanced analysis is currently unavailable.',
            'task_id': report_id,
            'id': report_id,
            'report_id': report_id,
        }
        if ai_error_msg:
            response_data['warning'] = ai_error_msg
            response_data['warning_code'] = (
                'openai_quota_exceeded' if 'quota' in ai_error_msg.lower() else 'ai_unavailable'
            )

        for key, value in report_data.items():
            response_data[key] = value

        return JsonResponse(response_data)
    except UnicodeDecodeError:
        return JsonResponse({'error': 'Uploaded file must be valid UTF-8 JSON'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON file'}, status=400)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def simple_task_status_view(request, task_id):
    """Simple task status view."""
    report_id = str(task_id)
    return JsonResponse({
        'id': task_id,
        'status': 'completed',
        'progress': 100,
        'message': 'Analysis completed successfully',
        'result_data': {
            'report_id': report_id,
        },
    })

__all__ = [
    'AnalysisStatusView',
    'FinancialDataUploadView',
    'analyze_direct_data',
    'simple_custom_prompt_view',
    'simple_task_status_view',
    'simple_upload_view',
]
