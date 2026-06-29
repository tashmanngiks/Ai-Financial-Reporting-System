"""Persistent report storage backed by the database."""

from __future__ import annotations

import uuid
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.utils import timezone

from ..models import DataRetentionAuditLog, PersistedReport

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


def list_report_records(
    request=None,
    *,
    include_archived: bool = True,
    search: str = '',
    status: str = '',
) -> list[PersistedReport]:
    user, _ = _resolve_owner(request)
    if user is not None:
        queryset = PersistedReport.objects.filter(Q(owner=user) | Q(owner__isnull=True))
    else:
        queryset = PersistedReport.objects.all()

    if not include_archived:
        queryset = queryset.filter(is_archived=False)

    if search:
        search_lower = search.lower()
        queryset = [
            record for record in queryset
            if search_lower in str(record.report_data.get('filename', '')).lower()
            or search_lower in str(record.report_data.get('bank_name', '')).lower()
            or search_lower in str(record.report_data.get('metadata', {}).get('title', '')).lower()
        ]
        if status:
            queryset = [record for record in queryset if str(record.report_data.get('status', '')).lower() == status.lower()]
        return list(queryset)

    records = list(queryset.order_by('-created_at'))
    if status:
        records = [record for record in records if str(record.report_data.get('status', '')).lower() == status.lower()]
    return records


def archive_reports(report_ids: list[str], request=None) -> dict[str, Any]:
    ids = [uuid.UUID(str(report_id)) for report_id in report_ids]
    queryset = PersistedReport.objects.filter(id__in=ids)
    updated = queryset.update(is_archived=True, archived_at=timezone.now())
    _log_retention_action(request, 'archive', report_ids)
    return {'updated_count': updated}


def restore_reports(report_ids: list[str], request=None) -> dict[str, Any]:
    ids = [uuid.UUID(str(report_id)) for report_id in report_ids]
    queryset = PersistedReport.objects.filter(id__in=ids)
    updated = queryset.update(is_archived=False, archived_at=None)
    _log_retention_action(request, 'restore', report_ids)
    return {'updated_count': updated}


def delete_reports(report_ids: list[str], request=None) -> dict[str, Any]:
    ids = [uuid.UUID(str(report_id)) for report_id in report_ids]
    queryset = PersistedReport.objects.filter(id__in=ids)
    deleted_count, _ = queryset.delete()
    _log_retention_action(request, 'delete', report_ids)
    return {'deleted_count': deleted_count}


def _log_retention_action(request, action: str, report_ids: list[str], metadata: dict[str, Any] | None = None) -> None:
    user, _ = _resolve_owner(request)
    DataRetentionAuditLog.objects.create(
        user=user,
        action=action,
        report_ids=[str(report_id) for report_id in report_ids],
        metadata=metadata or {},
    )
