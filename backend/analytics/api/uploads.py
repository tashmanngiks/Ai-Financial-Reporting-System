"""Upload and analysis endpoints."""

import json
import uuid
from datetime import datetime
from typing import Any

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..services.report_store import get_report, save_report, update_report
from django.conf import settings
from ..services.prompt_module_store import apply_section_traceability
from ..services.analysis_prompt_defaults import (
    FINANCIAL_INSTRUMENTS_ANALYSIS_ID,
    MONEY_MARKET_ANALYSIS_ID,
    WACC_ANALYSIS_ID,
)
from ..services.prompt_settings_store import get_analysis_prompt
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


DATASET_TYPE_RULES: dict[str, dict[str, Any]] = {
    'wacc': {
        'label': 'WACC',
        'prompt_id': WACC_ANALYSIS_ID,
        'template': 'wacc_report',
        'signals': [
            ['wacc', 'weighted average cost of capital'],
            ['cost of equity', 'cost_equity', 'equity cost'],
            ['cost of debt', 'cost_debt', 'debt cost'],
            ['tax rate', 'tax_rate', 'effective tax rate'],
            ['capital structure', 'capital_structure', 'equity ratio', 'debt ratio'],
            ['beta', 'risk free rate', 'risk-free rate', 'market risk premium'],
        ],
        'missing_indicators': ['cost of equity', 'cost of debt', 'tax rate', 'capital structure', 'WACC'],
    },
    'money_market': {
        'label': 'Money Market',
        'prompt_id': MONEY_MARKET_ANALYSIS_ID,
        'template': 'money_market_report',
        'signals': [
            ['treasury bill', 'treasury bills', 'tbill', 't-bill'],
            ['commercial paper'],
            ['certificate of deposit', 'certificates of deposit', 'cd rate', 'cds'],
            ['interbank rate', 'interbank rates'],
            ['repo rate', 'repo rates', 'repurchase agreement'],
            ['liquidity', 'short-term', 'short term'],
        ],
        'missing_indicators': ['treasury bills', 'commercial paper', 'certificates of deposit', 'interbank rates', 'repo rates'],
    },
    'financial_instruments': {
        'label': 'Financial Instruments',
        'prompt_id': FINANCIAL_INSTRUMENTS_ANALYSIS_ID,
        'template': 'financial_instruments_report',
        'signals': [
            ['bond', 'bonds', 'treasury security', 'treasury securities'],
            ['equity', 'equities', 'stock', 'shares'],
            ['derivative', 'derivatives', 'option', 'swap', 'future', 'futures'],
            ['mutual fund', 'mutual funds'],
            ['etf', 'exchange-traded fund', 'exchange traded fund'],
            ['commodity', 'commodities', 'foreign exchange', 'fx'],
        ],
        'missing_indicators': ['bonds', 'equities', 'derivatives', 'mutual funds', 'ETFs'],
    },
}


def _collect_text_tokens(value: Any, parts: list[str], depth: int = 0) -> None:
    if depth > 8:
        return
    if isinstance(value, dict):
        for key, item in value.items():
            parts.append(str(key))
            _collect_text_tokens(item, parts, depth + 1)
    elif isinstance(value, list):
        for item in value[:100]:
            _collect_text_tokens(item, parts, depth + 1)
    elif isinstance(value, str):
        parts.append(value)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        parts.append(str(value))


def _infer_dataset_type(json_data: Any) -> str | None:
    parts: list[str] = []
    _collect_text_tokens(json_data, parts)
    text = ' '.join(parts).lower()

    scores: dict[str, int] = {}
    for dataset_type, rule in DATASET_TYPE_RULES.items():
        score = 0
        for signal_group in rule['signals']:
            if any(signal in text for signal in signal_group):
                score += 1
        scores[dataset_type] = score

    if not scores:
        return None

    best_type = max(scores, key=scores.get)
    if scores[best_type] < 2:
        return None
    return best_type


def _validate_dataset_type(json_data: Any, selected_type: str) -> tuple[bool, str | None, str | None]:
    selected = (selected_type or '').strip().lower()
    if selected not in DATASET_TYPE_RULES:
        return False, None, 'Please select one dataset type before uploading: WACC, Money Market, or Financial Instruments.'

    detected = _infer_dataset_type(json_data)
    if detected == selected:
        return True, detected, None

    selected_label = DATASET_TYPE_RULES[selected]['label']
    if detected:
        detected_label = DATASET_TYPE_RULES[detected]['label']
        return (
            False,
            detected,
            f'The uploaded data appears to contain {detected_label} information, but you selected {selected_label}. Please either upload the correct dataset or change the dataset type.',
        )

    missing = ', '.join(DATASET_TYPE_RULES[selected]['missing_indicators'])
    return (
        False,
        None,
        f'Unable to verify the selected {selected_label} dataset. Required indicators such as {missing} were not found in the uploaded file.',
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

        selected_dataset_type = (
            request.POST.get('dataset_type')
            or body.get('dataset_type')
            or report_options.get('dataset_type')
            or ''
        ).strip().lower()

        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'}, status=400)

        uploaded_file = request.FILES['file']
        description = request.POST.get('description', '')

        if not selected_dataset_type:
            return JsonResponse({
                'error': 'Please select one dataset type before uploading: WACC, Money Market, or Financial Instruments.',
            }, status=400)

        if not uploaded_file.name.endswith('.json'):
            return JsonResponse({'error': 'Only JSON files are supported'}, status=400)

        file_content = uploaded_file.read().decode('utf-8')
        json_data = json.loads(file_content)

        if json_data is None:
            return JsonResponse({'error': 'JSON file is empty'}, status=400)

        is_dataset_validated, detected_dataset_type, validation_error = _validate_dataset_type(
            json_data,
            selected_dataset_type,
        )
        if not is_dataset_validated:
            response = {
                'error': validation_error or 'Uploaded dataset does not match the selected type.',
                'selected_dataset_type': selected_dataset_type,
            }
            if detected_dataset_type:
                response['detected_dataset_type'] = detected_dataset_type
            return JsonResponse(response, status=400)

        normalized_json, original_json = normalize_json_for_analysis(json_data)
        bank_name, data_period = extract_entity_metadata(json_data)

        dataset_rule = DATASET_TYPE_RULES[selected_dataset_type]
        dataset_prompt = get_analysis_prompt(dataset_rule['prompt_id'])
        prompt = (dataset_prompt.content if dataset_prompt else '').strip()
        if not prompt:
            return JsonResponse({'error': 'Selected dataset analysis prompt is unavailable.'}, status=500)

        # Prefer sections from the upload UI; otherwise use the dataset template sections.
        client_sections = report_options.get('sections') or report_options.get('include_sections') or []
        if isinstance(client_sections, str):
            client_sections = [client_sections]
        client_sections = [str(s).strip() for s in client_sections if str(s).strip()]

        resolved_report_options = {
            'template': report_options.get('template') or dataset_rule['template'],
            'sections': client_sections,
            'include_sections': report_options.get('include_sections') or client_sections,
            'exclude_sections': report_options.get('exclude_sections') or [],
            'length': (
                request.POST.get('length')
                or body.get('length')
                or report_options.get('length')
                or 'standard'
            ),
            'detail_level': (
                request.POST.get('detail_level')
                or body.get('detail_level')
                or report_options.get('detail_level')
                or 'balanced'
            ),
            'output_format': (
                request.POST.get('output_format')
                or body.get('output_format')
                or report_options.get('output_format')
                or 'json'
            ),
            'dataset_type': selected_dataset_type,
        }

        report_id = str(uuid.uuid4())
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ai_analysis = perform_initial_ai_analysis(json_data)

        full_ai_analysis, ai_error_msg, ai_enhanced = generate_analysis_from_prompt(
            prompt,
            original_json,
            ai_analysis,
            report_options=resolved_report_options,
        )
        # Capture fully resolved sections (after template/length normalization) for the UI.
        try:
            from ..services.report_prompt_registry import get_report_prompt_registry
            resolved_report_options = get_report_prompt_registry().build_report_options(resolved_report_options)
        except Exception:
            pass
        comprehensive_generated = len(full_ai_analysis) > 0 and ai_enhanced

        prompt_title = dataset_rule['label']

        report_data = {
            'id': report_id,
            'filename': uploaded_file.name,
            'size': uploaded_file.size,
            'description': description,
            'user_prompt': prompt,
            'dataset_type': selected_dataset_type,
            'detected_dataset_type': detected_dataset_type or selected_dataset_type,
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
            'report_options': resolved_report_options,
            'metadata': {
                'title': prompt_title,
                'report_date': current_time,
                'period': data_period,
                'generated_at': current_time,
                'ai_processed': comprehensive_generated,
                'comprehensive_generated': comprehensive_generated,
                'ai_enhanced': ai_enhanced,
                'user_prompt': prompt,
                'dataset_type': selected_dataset_type,
                'detected_dataset_type': detected_dataset_type or selected_dataset_type,
                'original_json': original_json,
                'normalized_json': normalized_json,
                'report_options': resolved_report_options,
            },
        }

        if ai_error_msg:
            report_data['ai_error'] = ai_error_msg

        save_report(report_id, report_data, request=request)

        if full_ai_analysis:
            try:
                annotated = apply_section_traceability(
                    report_id,
                    full_ai_analysis,
                    report_options=resolved_report_options,
                    ai_model=getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini') if ai_enhanced else 'fallback',
                    confidence_score=0.85 if ai_enhanced else 0.5,
                    regeneration_reason='initial generation',
                )
                report_data['comprehensive_analysis'] = annotated
                update_report(report_id, {'comprehensive_analysis': annotated}, request=request)
            except Exception as exc:
                print(f'DEBUG: section traceability skipped: {exc}')

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

        response_data['dataset_type'] = selected_dataset_type
        response_data['detected_dataset_type'] = detected_dataset_type or selected_dataset_type

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
