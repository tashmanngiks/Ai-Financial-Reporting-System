"""Section version history helpers for persisted financial reports."""

from __future__ import annotations

import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any

from django.utils import timezone

from .report_store import get_report, save_report

SECTION_VERSIONS_KEY = 'section_versions'
SECTION_AUDIT_KEY = 'section_audit'


def _section_bucket(report: dict[str, Any], key: str) -> list[dict[str, Any]]:
    versions = report.get(SECTION_VERSIONS_KEY) or {}
    bucket = versions.get(key) or []
    return list(bucket) if isinstance(bucket, list) else []


def _next_version_number(report: dict[str, Any], section_key: str) -> int:
    bucket = _section_bucket(report, section_key)
    if not bucket:
        return 1
    numbers = [int(item.get('version_number') or 0) for item in bucket]
    return max(numbers) + 1 if numbers else 1


def get_section_history(report_id: str, section_key: str) -> list[dict[str, Any]]:
    report = get_report(str(report_id))
    if not report:
        return []
    bucket = _section_bucket(report, section_key)
    bucket.sort(key=lambda item: int(item.get('version_number') or 0), reverse=True)
    return bucket


def ensure_initial_section_version(
    report_id: str,
    section_key: str,
    *,
    section: dict[str, Any] | None = None,
    prompt_version: dict[str, Any] | None = None,
    model_used: str = '',
    generation_reason: str = 'initial generation',
    generated_by: str | None = None,
) -> dict[str, Any] | None:
    report = get_report(str(report_id))
    if not report:
        return None

    section = deepcopy(section or {})
    section_title = section.get('title') or section_key.replace('_', ' ').title()
    current_content = section.get('content', {})
    if isinstance(current_content, dict):
        current_content = deepcopy(current_content)

    bucket = _section_bucket(report, section_key)
    if bucket:
        return bucket[-1]

    version = {
        'id': uuid.uuid4().hex,
        'report_id': str(report_id),
        'section_key': section_key,
        'version_number': 1,
        'section_title': section_title,
        'prompt_version_id': (prompt_version or {}).get('id'),
        'prompt_version_number': (prompt_version or {}).get('version_number'),
        'prompt_text': (prompt_version or {}).get('prompt_text', ''),
        'output': current_content,
        'generated_by': generated_by,
        'generated_at': timezone.now().isoformat(),
        'model_used': model_used,
        'generation_status': 'SUCCESS',
        'generation_reason': generation_reason,
        'request_id': uuid.uuid4().hex,
        'is_current': True,
    }
    bucket.append(version)
    report.setdefault(SECTION_VERSIONS_KEY, {})[section_key] = bucket
    audit = list(report.get(SECTION_AUDIT_KEY) or [])
    audit.append(
        {
            'id': uuid.uuid4().hex,
            'report_id': str(report_id),
            'section_key': section_key,
            'event': 'INITIAL_VERSION',
            'version_number': 1,
            'generated_at': timezone.now().isoformat(),
            'generation_reason': generation_reason,
        }
    )
    report[SECTION_AUDIT_KEY] = audit[-200:]
    save_report(str(report_id), report)
    return version


def append_section_version(
    report_id: str,
    section_key: str,
    *,
    section: dict[str, Any],
    prompt_version: dict[str, Any] | None = None,
    model_used: str = '',
    generation_status: str = 'SUCCESS',
    generation_reason: str = '',
    generated_by: str | None = None,
    request_id: str | None = None,
    duration_ms: int | None = None,
    usage: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    report = get_report(str(report_id))
    if not report:
        return None

    section_key = str(section_key).strip()
    bucket = _section_bucket(report, section_key)
    next_version = _next_version_number(report, section_key)

    if bucket:
        for item in bucket:
            item['is_current'] = False

    version = {
        'id': uuid.uuid4().hex,
        'report_id': str(report_id),
        'section_key': section_key,
        'version_number': next_version,
        'section_title': section.get('title') or section_key.replace('_', ' ').title(),
        'prompt_version_id': (prompt_version or {}).get('id'),
        'prompt_version_number': (prompt_version or {}).get('version_number'),
        'prompt_text': (prompt_version or {}).get('prompt_text', ''),
        'output': deepcopy(section.get('content', {})),
        'generated_by': generated_by,
        'generated_at': timezone.now().isoformat(),
        'model_used': model_used,
        'generation_status': generation_status,
        'generation_reason': generation_reason,
        'request_id': request_id or uuid.uuid4().hex,
        'duration_ms': duration_ms,
        'usage': usage or {},
        'is_current': True,
    }
    bucket.append(version)
    report.setdefault(SECTION_VERSIONS_KEY, {})[section_key] = bucket

    audit = list(report.get(SECTION_AUDIT_KEY) or [])
    audit.append(
        {
            'id': uuid.uuid4().hex,
            'report_id': str(report_id),
            'section_key': section_key,
            'event': 'SECTION_REGENERATED' if generation_status == 'SUCCESS' else 'SECTION_REGENERATION_FAILED',
            'version_number': next_version,
            'generated_at': timezone.now().isoformat(),
            'generation_reason': generation_reason,
            'prompt_version_number': (prompt_version or {}).get('version_number'),
            'generation_status': generation_status,
            'model_used': model_used,
            'request_id': version['request_id'],
        }
    )
    report[SECTION_AUDIT_KEY] = audit[-200:]
    save_report(str(report_id), report)
    return version
