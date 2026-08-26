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
    """Create default prompt rows and configuration if missing.

    Also keeps `default_content` aligned with code defaults. Dataset prompts that
    still lack `[SECTION:]` markers are upgraded so the split pane can decompose them.
    """
    for definition in get_default_analysis_prompt_definitions():
        prompt, created = AnalysisPrompt.objects.get_or_create(
            prompt_id=definition["prompt_id"],
            defaults={
                "title": definition["title"],
                "content": definition["content"],
                "default_content": definition["content"],
                "recommended_sections": definition["recommended_sections"],
            },
        )
        if created:
            continue

        update_fields: list[str] = []
        new_default = definition["content"]
        if prompt.default_content != new_default:
            # Upgrade live content when it was never customized, or when it cannot
            # be decomposed into section modules yet.
            uncustomized = (prompt.content or "").strip() == (prompt.default_content or "").strip()
            missing_markers = "[SECTION:" not in (prompt.content or "")
            if uncustomized or (
                missing_markers
                and prompt.prompt_id in {
                    "wacc_analysis",
                    "money_market_analysis",
                    "financial_instruments_analysis",
                }
            ):
                prompt.content = new_default
                update_fields.append("content")
            prompt.default_content = new_default
            update_fields.append("default_content")

        if prompt.recommended_sections != definition["recommended_sections"]:
            prompt.recommended_sections = definition["recommended_sections"]
            update_fields.append("recommended_sections")
        if prompt.title != definition["title"]:
            prompt.title = definition["title"]
            update_fields.append("title")
        if update_fields:
            prompt.save(update_fields=[*update_fields, "updated_at"])

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
    default_section_library = deepcopy(DEFAULT_REPORT_PROMPT_CONFIG.get("section_library", {}))
    default_templates = deepcopy(DEFAULT_REPORT_PROMPT_CONFIG.get("templates", {}))
    config["section_library"] = {**default_section_library, **deepcopy(report_config.section_library or {})}
    config["templates"] = {**default_templates, **deepcopy(report_config.templates or {})}
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
