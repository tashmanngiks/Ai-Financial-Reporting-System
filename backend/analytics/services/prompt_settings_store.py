"""Database-backed storage for editable AI analysis prompts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from django.contrib.auth.models import User
from django.db import transaction

from ..models import AnalysisPrompt, ReportConfiguration
from .analysis_prompt_defaults import (
    CAPITAL_ADEQUACY_CRIPE_ID,
    FINANCIAL_DASHBOARD_ID,
    get_default_analysis_prompt_definitions,
)
from .report_prompt_registry import DEFAULT_REPORT_PROMPT_CONFIG


def _default_report_configuration() -> dict[str, Any]:
    return {
        "section_library": deepcopy(DEFAULT_REPORT_PROMPT_CONFIG.get("section_library", {})),
        "templates": deepcopy(DEFAULT_REPORT_PROMPT_CONFIG.get("templates", {})),
        "default_length": DEFAULT_REPORT_PROMPT_CONFIG.get("default_length", "standard"),
        "default_detail_level": DEFAULT_REPORT_PROMPT_CONFIG.get("default_detail_level", "balanced"),
    }


def ensure_prompt_defaults() -> None:
    """Create default prompt rows and configuration if missing."""
    for definition in get_default_analysis_prompt_definitions():
        AnalysisPrompt.objects.get_or_create(
            prompt_id=definition["prompt_id"],
            defaults={
                "title": definition["title"],
                "content": definition["content"],
                "default_content": definition["content"],
                "recommended_sections": definition["recommended_sections"],
            },
        )

    defaults = _default_report_configuration()
    ReportConfiguration.objects.get_or_create(
        id=1,
        defaults=defaults,
    )


def get_analysis_prompt(prompt_id: str) -> AnalysisPrompt | None:
    ensure_prompt_defaults()
    return AnalysisPrompt.objects.filter(prompt_id=prompt_id).first()


def list_analysis_prompts() -> list[AnalysisPrompt]:
    ensure_prompt_defaults()
    return list(AnalysisPrompt.objects.order_by("prompt_id"))


def serialize_analysis_prompt(prompt: AnalysisPrompt) -> dict[str, Any]:
    return {
        "id": prompt.prompt_id,
        "title": prompt.title,
        "content": prompt.content,
        "default_content": prompt.default_content,
        "recommended_sections": prompt.recommended_sections,
        "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
        "updated_by": prompt.updated_by.username if prompt.updated_by else None,
    }


def get_report_configuration() -> ReportConfiguration:
    ensure_prompt_defaults()
    config, _ = ReportConfiguration.objects.get_or_create(id=1, defaults=_default_report_configuration())
    return config


def build_prompt_config_payload() -> dict[str, Any]:
    """Build the full prompt configuration consumed by the registry and API."""
    ensure_prompt_defaults()
    report_config = get_report_configuration()
    prompts = list_analysis_prompts()
    prompt_map = {prompt.prompt_id: prompt for prompt in prompts}

    config = deepcopy(DEFAULT_REPORT_PROMPT_CONFIG)
    config["section_library"] = deepcopy(report_config.section_library or {})
    config["templates"] = deepcopy(report_config.templates or {})
    config["default_length"] = report_config.default_length
    config["default_detail_level"] = report_config.default_detail_level

    financial = prompt_map.get(FINANCIAL_DASHBOARD_ID)
    if financial:
        config["system_prompt_template"] = financial.content

    config["analysis_prompts"] = {
        prompt.prompt_id: serialize_analysis_prompt(prompt) for prompt in prompts
    }
    return config


@transaction.atomic
def update_analysis_prompt_content(
    prompt_id: str,
    content: str,
    user: User | None = None,
) -> AnalysisPrompt:
    ensure_prompt_defaults()
    prompt = AnalysisPrompt.objects.get(prompt_id=prompt_id)
    prompt.content = content.strip()
    if user and getattr(user, "is_authenticated", False):
        prompt.updated_by = user
    prompt.save(update_fields=["content", "updated_by", "updated_at"])
    return prompt


@transaction.atomic
def reset_analysis_prompt(prompt_id: str, user: User | None = None) -> AnalysisPrompt:
    ensure_prompt_defaults()
    prompt = AnalysisPrompt.objects.get(prompt_id=prompt_id)
    prompt.content = prompt.default_content
    if user and getattr(user, "is_authenticated", False):
        prompt.updated_by = user
    prompt.save(update_fields=["content", "updated_by", "updated_at"])
    return prompt


@transaction.atomic
def reset_all_analysis_prompts(user: User | None = None) -> list[AnalysisPrompt]:
    return [reset_analysis_prompt(prompt.prompt_id, user=user) for prompt in list_analysis_prompts()]


@transaction.atomic
def save_report_configuration(updates: dict[str, Any], user: User | None = None) -> dict[str, Any]:
    """Persist section library, templates, and optional prompt updates."""
    ensure_prompt_defaults()
    report_config = get_report_configuration()

    if "section_library" in updates and isinstance(updates["section_library"], dict):
        report_config.section_library = deepcopy(updates["section_library"])
    if "templates" in updates and isinstance(updates["templates"], dict):
        report_config.templates = deepcopy(updates["templates"])
    if updates.get("default_length"):
        report_config.default_length = str(updates["default_length"])
    if updates.get("default_detail_level"):
        report_config.default_detail_level = str(updates["default_detail_level"])
    report_config.save()

    if isinstance(updates.get("system_prompt_template"), str) and updates["system_prompt_template"].strip():
        update_analysis_prompt_content(
            FINANCIAL_DASHBOARD_ID,
            updates["system_prompt_template"],
            user=user,
        )

    analysis_prompts = updates.get("analysis_prompts")
    if isinstance(analysis_prompts, dict):
        for prompt_id, payload in analysis_prompts.items():
            if isinstance(payload, str) and payload.strip():
                update_analysis_prompt_content(prompt_id, payload, user=user)
            elif isinstance(payload, dict) and payload.get("content", "").strip():
                update_analysis_prompt_content(prompt_id, payload["content"], user=user)

    return build_prompt_config_payload()
