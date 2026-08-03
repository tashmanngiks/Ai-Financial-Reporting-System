"""Prompt module CRUD and versioning APIs for Prompt Intelligence."""

from __future__ import annotations

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .authentication import CsrfExemptSessionAuthentication
from ..services.prompt_module_store import (
    compare_prompt_versions,
    create_prompt_module,
    duplicate_prompt_module,
    get_prompt_module,
    list_prompt_module_versions,
    list_prompt_modules,
    restore_prompt_module_version,
    serialize_prompt_module,
    serialize_prompt_module_version,
    update_prompt_module,
)


def _body(request) -> dict:
    if isinstance(getattr(request, 'data', None), dict):
        return request.data
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        return {}


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def list_prompt_modules_view(request):
    include_archived = str(request.GET.get('include_archived', 'true')).lower() != 'false'
    category = (request.GET.get('category') or '').strip()
    search = (request.GET.get('q') or '').strip().lower()
    favorites_only = str(request.GET.get('favorites', '')).lower() in ('1', 'true', 'yes')
    include_versions = str(request.GET.get('include_versions', '')).lower() in ('1', 'true', 'yes')

    modules = list_prompt_modules(include_archived=include_archived)
    results = []
    for module in modules:
        if category and module.category.lower() != category.lower():
            continue
        if favorites_only and not module.is_favorite:
            continue
        if search:
            hay = f'{module.name} {module.description} {module.category} {module.prompt_text}'.lower()
            if search not in hay:
                continue
        results.append(serialize_prompt_module(module, include_versions=include_versions))

    return JsonResponse({
        'prompt_modules': results,
        'count': len(results),
        'categories': sorted({m.category for m in modules if m.category}),
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def create_prompt_module_view(request):
    try:
        module = create_prompt_module(_body(request), user=request.user)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse({'prompt_module': serialize_prompt_module(module, include_versions=True)}, status=201)


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def prompt_module_detail_view(request, module_id):
    module = get_prompt_module(module_id)
    if not module:
        return JsonResponse({'error': 'Prompt module not found'}, status=404)
    return JsonResponse({'prompt_module': serialize_prompt_module(module, include_versions=True)})


@csrf_exempt
@api_view(['PATCH', 'PUT', 'POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def update_prompt_module_view(request, module_id):
    module = get_prompt_module(module_id)
    if not module:
        return JsonResponse({'error': 'Prompt module not found'}, status=404)
    body = _body(request)
    module = update_prompt_module(
        module,
        body,
        user=request.user,
        change_comment=body.get('change_comment') or body.get('comment') or '',
    )
    return JsonResponse({'prompt_module': serialize_prompt_module(module, include_versions=True)})


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def prompt_module_versions_view(request, module_id):
    module = get_prompt_module(module_id)
    if not module:
        return JsonResponse({'error': 'Prompt module not found'}, status=404)
    versions = [serialize_prompt_module_version(v) for v in list_prompt_module_versions(module)]
    return JsonResponse({'versions': versions, 'count': len(versions)})


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def compare_prompt_module_versions_view(request, module_id):
    module = get_prompt_module(module_id)
    if not module:
        return JsonResponse({'error': 'Prompt module not found'}, status=404)
    try:
        payload = compare_prompt_versions(module, int(request.GET.get('from')), int(request.GET.get('to')))
    except (TypeError, ValueError) as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse(payload)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def restore_prompt_module_version_view(request, module_id):
    module = get_prompt_module(module_id)
    if not module:
        return JsonResponse({'error': 'Prompt module not found'}, status=404)
    try:
        module = restore_prompt_module_version(module, int(_body(request).get('version_number')), user=request.user)
    except (TypeError, ValueError) as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    return JsonResponse({'prompt_module': serialize_prompt_module(module, include_versions=True)})


@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAdminUser])
def duplicate_prompt_module_view(request, module_id):
    module = get_prompt_module(module_id)
    if not module:
        return JsonResponse({'error': 'Prompt module not found'}, status=404)
    copy = duplicate_prompt_module(module, user=request.user)
    return JsonResponse({'prompt_module': serialize_prompt_module(copy, include_versions=True)}, status=201)
