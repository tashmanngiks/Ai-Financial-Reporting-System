"""Persistent report storage backed by the database."""

from __future__ import annotations

import uuid
from typing import Any

from django.contrib.auth.models import AnonymousUser

from ..models import PersistedReport

try:
    from django.core.cache import cache
except Exception:  # pragma: no cover - cache optional in tests
    cache = None

REPORT_CACHE_PREFIX = 'analytics:report:'
REPORT_CACHE_TIMEOUT = 7 * 24 * 60 * 60


def _report_cache_key(report_id: str) -> str:
    return f'{REPORT_CACHE_PREFIX}{report_id}'


def _cache_get(report_id: str) -> dict[str, Any] | None:
    if cache is None:
        return None
    report = cache.get(_report_cache_key(str(report_id)))
    return report if isinstance(report, dict) else None


def _cache_set(report_id: str, report_data: dict[str, Any]) -> None:
    if cache is None:
        return
    cache.set(_report_cache_key(str(report_id)), report_data, REPORT_CACHE_TIMEOUT)


def _resolve_owner(request) -> tuple[Any | None, str]:
    if request is None:
        return None, ''
    user = getattr(request, 'user', None)
    if user is not None and not isinstance(user, AnonymousUser) and user.is_authenticated:
        return user, user.username
    return None, ''


def list_report_ids() -> list[str]:
    return [str(report_id) for report_id in PersistedReport.objects.values_list('id', flat=True)]


def list_reports(request=None) -> list[dict[str, Any]]:
    from django.db.models import Q

    user, _ = _resolve_owner(request)
    if user is not None:
        queryset = PersistedReport.objects.filter(Q(owner=user) | Q(owner__isnull=True))
    else:
        queryset = PersistedReport.objects.all()
    return [record.report_data for record in queryset]


def get_report(report_id: str) -> dict[str, Any] | None:
    report_id = str(report_id)
    cached = _cache_get(report_id)
    if cached:
        return cached

    try:
        record = PersistedReport.objects.get(pk=report_id)
    except (PersistedReport.DoesNotExist, ValueError):
        return None

    report = record.report_data
    _cache_set(report_id, report)
    return report


def save_report(report_id: str, report_data: dict[str, Any], request=None) -> dict[str, Any]:
    report_id = str(report_id)
    report_data = dict(report_data)
    report_data['id'] = report_id

    owner, owner_username = _resolve_owner(request)
    PersistedReport.objects.update_or_create(
        id=uuid.UUID(report_id),
        defaults={
            'report_data': report_data,
            'owner': owner,
            'owner_username': owner_username,
        },
    )
    _cache_set(report_id, report_data)
    return report_data


def update_report(report_id: str, updates: dict[str, Any], request=None) -> dict[str, Any] | None:
    report = get_report(report_id)
    if not report:
        return None

    report.update(updates)
    return save_report(str(report_id), report, request=request)
