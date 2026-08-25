"""Prompt module storage, versioning, and traceability helpers."""

from __future__ import annotations

import hashlib
import re
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.utils import timezone

from ..models import (
    PersistedReport,
    PromptModule,
    PromptModuleVersion,
    ReportSectionMapping,
)
from .analysis_prompt_defaults import get_default_analysis_prompt_definitions
from .report_prompt_registry import get_report_prompt_registry


def _slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or uuid.uuid4().hex[:8]


def _now_iso() -> str:
    return timezone.now().isoformat()


def _default_prompt_modules() -> list[dict[str, Any]]:
    registry = get_report_prompt_registry()
    section_library = registry.get_section_library()

    base_modules = [
        {
            'name': 'Executive Summary Prompt',
            'slug': 'executive-summary',
            'category': 'Financial',
            'description': 'Creates the executive overview for a report.',
            'prompt_text': 'Write a concise executive summary using the available financial data and highlight the most important findings.',
            'related_sections': ['executive_summary'],
            'order_index': 1,
        },
        {
            'name': 'Statistical Highlights Prompt',
            'slug': 'statistical-highlights',
            'category': 'Financial',
            'description': 'Summarizes the most important numeric patterns and extremes.',
            'prompt_text': 'Summarize minimum, maximum, average, and trend values for the available metrics.',
            'related_sections': ['statistical_highlights'],
            'order_index': 2,
        },
        {
            'name': 'Financial Ratios Prompt',
            'slug': 'financial-ratios',
            'category': 'Financial',
            'description': 'Evaluates profitability, liquidity, leverage, and efficiency ratios.',
            'prompt_text': 'Analyze profitability, liquidity, leverage, and efficiency ratios using only the available data.',
            'related_sections': ['financial_ratios'],
            'order_index': 3,
        },
        {
            'name': 'Trend Analysis Prompt',
            'slug': 'trend-analysis',
            'category': 'Financial',
            'description': 'Explains directional changes and time-series movement.',
            'prompt_text': 'Analyze the current trends, compare time periods, and explain what is improving or deteriorating.',
            'related_sections': ['trend_analysis', 'market_trends'],
            'order_index': 4,
        },
        {
            'name': 'Risk Prompt',
            'slug': 'risk-assessment',
            'category': 'Risk',
            'description': 'Assesses financial risk posture and key exposures.',
            'prompt_text': 'Assess the main financial risks, explain the drivers, and describe the mitigation priorities.',
            'related_sections': ['risk_assessment'],
            'order_index': 5,
        },
        {
            'name': 'Benchmark Comparison Prompt',
            'slug': 'benchmark-comparison',
            'category': 'Financial',
            'description': 'Compares performance with benchmarks or peer values.',
            'prompt_text': 'Compare the available metrics against benchmarks and explain the performance gaps.',
            'related_sections': ['benchmark_comparison'],
            'order_index': 6,
        },
        {
            'name': 'Recommendations Prompt',
            'slug': 'recommendations',
            'category': 'Board',
            'description': 'Generates practical recommendations and action items.',
            'prompt_text': 'Provide prioritized recommendations tied directly to the financial evidence in the dataset.',
            'related_sections': ['recommendations'],
            'order_index': 7,
        },
    ]

    section_defaults = {
        'wacc_analysis': {
            'name': 'WACC Prompt',
            'category': 'WACC',
            'description': 'Focuses on cost of capital and financing mix.',
            'prompt_text': 'Analyze weighted average cost of capital, capital structure, and financing efficiency.',
        },
        'money_market_analysis': {
            'name': 'Money Market Prompt',
            'category': 'Money Market',
            'description': 'Focuses on short-term funding and market conditions.',
            'prompt_text': 'Analyze money market conditions, short-term rates, liquidity, and funding pressure.',
        },
        'investment_analysis': {
            'name': 'Financial Instruments Prompt',
            'category': 'Treasury',
            'description': 'Reviews valuation and market exposure across investable instruments.',
            'prompt_text': 'Assess investment performance, valuation, volatility, and portfolio risk exposure.',
        },
        'macroeconomic_indicators': {
            'name': 'Macro Indicators Prompt',
            'category': 'Governance',
            'description': 'Explains macroeconomic context and external drivers.',
            'prompt_text': 'Analyze macroeconomic indicators and explain how they influence the financial outlook.',
        },
        'country_risk_analysis': {
            'name': 'Country Risk Prompt',
            'category': 'Risk',
            'description': 'Assesses country-level political, currency, and sovereign risk.',
            'prompt_text': 'Compare country risk levels and explain the drivers of political, currency, and sovereign exposure.',
        },
    }

    modules = list(base_modules)
    for section_key, payload in section_defaults.items():
        if section_key not in section_library:
            continue
        modules.append(
            {
                'name': payload['name'],
                'slug': _slugify(section_key),
                'category': payload['category'],
                'description': payload['description'],
                'prompt_text': payload['prompt_text'],
                'related_sections': [section_key],
                'order_index': len(modules) + 1,
            }
        )

    for definition in get_default_analysis_prompt_definitions():
        modules.append(
            {
                'name': definition['title'],
                'slug': _slugify(definition['prompt_id']),
                'category': 'System',
                'description': f"Seeded from {definition['title']} default analysis prompt.",
                'prompt_text': definition['content'],
                'related_sections': definition.get('recommended_sections', []),
                'order_index': len(modules) + 1,
            }
        )

    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for module in modules:
        if module['slug'] in seen:
            continue
        seen.add(module['slug'])
        deduped.append(module)
    return deduped


def ensure_prompt_modules() -> list[PromptModule]:
    """Seed default prompt modules when the database is empty."""
    if PromptModule.objects.exists():
        return list(PromptModule.objects.order_by('order_index', 'name'))

    created_modules: list[PromptModule] = []
    for defaults in _default_prompt_modules():
        module = PromptModule.objects.create(
            name=defaults['name'],
            slug=defaults['slug'],
            description=defaults['description'],
            category=defaults['category'],
            prompt_text=defaults['prompt_text'],
            order_index=defaults['order_index'],
            tags=[defaults['category'], 'seeded'],
            related_sections=defaults.get('related_sections', []),
            status='active',
            ai_settings={'temperature': 0.4, 'max_tokens': 1200},
        )
        PromptModuleVersion.objects.create(
            prompt_module=module,
            version_number=1,
            prompt_text=module.prompt_text,
            change_comment='Initial seeded version',
            ai_settings_snapshot=deepcopy(module.ai_settings),
            tags_snapshot=deepcopy(module.tags),
            status_snapshot=module.status,
        )
        created_modules.append(module)
    return created_modules


def list_prompt_modules(include_archived: bool = True) -> list[PromptModule]:
    ensure_prompt_modules()
    queryset = PromptModule.objects.all()
    if not include_archived:
        queryset = queryset.exclude(status='archived')
    return list(queryset.order_by('order_index', 'name'))


def get_prompt_module(module_id: int | str) -> PromptModule | None:
    ensure_prompt_modules()
    try:
        return PromptModule.objects.get(pk=module_id)
    except PromptModule.DoesNotExist:
        return None


def get_prompt_module_for_section(section_key: str) -> PromptModule | None:
    ensure_prompt_modules()
    section_key = str(section_key).strip()
    if not section_key:
        return None

    slug_candidates = [
        _slugify(section_key),
        _slugify(section_key.replace('_', ' ')),
    ]

    module = PromptModule.objects.filter(slug__in=slug_candidates).first()
    if module:
        return module

    for candidate in PromptModule.objects.all().order_by('order_index', 'name'):
        related_sections = candidate.related_sections or []
        if section_key in related_sections:
            return candidate

    # Do not fall back to the Executive Summary prompt for every unmapped section.
    # That causes unrelated report sections to reuse the wrong prompt text in the
    # left-hand split-pane editor, which is the duplicate/misassigned behavior we saw.
    return None


def list_prompt_module_versions(module: PromptModule) -> list[PromptModuleVersion]:
    return list(module.versions.all().order_by('-version_number', '-created_at'))


def serialize_prompt_module(module: PromptModule, include_versions: bool = False) -> dict[str, Any]:
    payload = {
        'id': module.id,
        'name': module.name,
        'slug': module.slug,
        'description': module.description,
        'category': module.category,
        'prompt_text': module.prompt_text,
        'order_index': module.order_index,
        'version_current': module.version_current,
        'tags': module.tags,
        'related_sections': module.related_sections,
        'status': module.status,
        'ai_settings': module.ai_settings,
        'is_favorite': module.is_favorite,
        'created_by': module.created_by.username if module.created_by else None,
        'updated_by': module.updated_by.username if module.updated_by else None,
        'created_at': module.created_at.isoformat() if module.created_at else None,
        'updated_at': module.updated_at.isoformat() if module.updated_at else None,
    }
    if include_versions:
        payload['versions'] = [serialize_prompt_module_version(version) for version in list_prompt_module_versions(module)]
    return payload


def serialize_prompt_module_version(version: PromptModuleVersion) -> dict[str, Any]:
    return {
        'id': version.id,
        'prompt_module_id': version.prompt_module_id,
        'version_number': version.version_number,
        'prompt_text': version.prompt_text,
        'change_comment': version.change_comment,
        'ai_settings_snapshot': version.ai_settings_snapshot,
        'tags_snapshot': version.tags_snapshot,
        'status_snapshot': version.status_snapshot,
        'created_by': version.created_by.username if version.created_by else None,
        'created_at': version.created_at.isoformat() if version.created_at else None,
    }


def _next_version_number(module: PromptModule) -> int:
    latest = module.versions.order_by('-version_number').first()
    return (latest.version_number + 1) if latest else 1


@transaction.atomic
def create_prompt_module(payload: dict[str, Any], user=None) -> PromptModule:
    ensure_prompt_modules()
    slug = payload.get('slug') or _slugify(payload.get('name', 'prompt-module'))
    if PromptModule.objects.filter(slug=slug).exists():
        raise ValueError('A prompt module with that slug already exists.')

    module = PromptModule.objects.create(
        name=payload.get('name', 'Untitled Prompt Module'),
        slug=slug,
        description=payload.get('description', ''),
        category=payload.get('category', 'Custom'),
        prompt_text=payload.get('prompt_text', ''),
        order_index=int(payload.get('order_index') or 0),
        tags=payload.get('tags') or [],
        related_sections=payload.get('related_sections') or [],
        status=payload.get('status') or 'draft',
        ai_settings=payload.get('ai_settings') or {},
        created_by=user if getattr(user, 'is_authenticated', False) else None,
        updated_by=user if getattr(user, 'is_authenticated', False) else None,
    )
    PromptModuleVersion.objects.create(
        prompt_module=module,
        version_number=1,
        prompt_text=module.prompt_text,
        change_comment='Initial version',
        ai_settings_snapshot=deepcopy(module.ai_settings),
        tags_snapshot=deepcopy(module.tags),
        status_snapshot=module.status,
        created_by=user if getattr(user, 'is_authenticated', False) else None,
    )
    return module


@transaction.atomic
def update_prompt_module(module: PromptModule, payload: dict[str, Any], user=None, change_comment: str = '') -> PromptModule:
    ensure_prompt_modules()
    if 'name' in payload and payload['name']:
        module.name = payload['name']
    if 'description' in payload:
        module.description = payload['description'] or ''
    if 'category' in payload and payload['category']:
        module.category = payload['category']
    if 'prompt_text' in payload and payload['prompt_text'] is not None:
        module.prompt_text = payload['prompt_text']
    if 'order_index' in payload and payload['order_index'] is not None:
        module.order_index = int(payload['order_index'])
    if 'tags' in payload and isinstance(payload['tags'], list):
        module.tags = payload['tags']
    if 'related_sections' in payload and isinstance(payload['related_sections'], list):
        module.related_sections = payload['related_sections']
    if 'status' in payload and payload['status']:
        module.status = payload['status']
    if 'ai_settings' in payload and isinstance(payload['ai_settings'], dict):
        module.ai_settings = payload['ai_settings']
    if 'is_favorite' in payload:
        module.is_favorite = bool(payload['is_favorite'])

    module.updated_by = user if getattr(user, 'is_authenticated', False) else module.updated_by
    module.save()

    next_version = _next_version_number(module)
    PromptModuleVersion.objects.create(
        prompt_module=module,
        version_number=next_version,
        prompt_text=module.prompt_text,
        change_comment=change_comment or 'Prompt module updated',
        ai_settings_snapshot=deepcopy(module.ai_settings),
        tags_snapshot=deepcopy(module.tags),
        status_snapshot=module.status,
        created_by=user if getattr(user, 'is_authenticated', False) else None,
    )
    module.version_current = next_version
    module.save(update_fields=['version_current', 'updated_at'])
    return module


@transaction.atomic
def restore_prompt_module_version(module: PromptModule, version_number: int, user=None) -> PromptModule:
    ensure_prompt_modules()
    version = module.versions.filter(version_number=version_number).first()
    if not version:
        raise ValueError('Prompt version not found.')

    module.prompt_text = version.prompt_text
    module.ai_settings = deepcopy(version.ai_settings_snapshot)
    module.tags = deepcopy(version.tags_snapshot)
    module.status = version.status_snapshot
    module.updated_by = user if getattr(user, 'is_authenticated', False) else module.updated_by
    module.save()

    next_version = _next_version_number(module)
    PromptModuleVersion.objects.create(
        prompt_module=module,
        version_number=next_version,
        prompt_text=module.prompt_text,
        change_comment=f'Restored from version {version_number}',
        ai_settings_snapshot=deepcopy(module.ai_settings),
        tags_snapshot=deepcopy(module.tags),
        status_snapshot=module.status,
        created_by=user if getattr(user, 'is_authenticated', False) else None,
    )
    module.version_current = next_version
    module.save(update_fields=['version_current', 'updated_at'])
    return module


def _hash_payload(payload: Any) -> str:
    serialized = str(payload).encode('utf-8', errors='ignore')
    return hashlib.sha256(serialized).hexdigest()


def _normalize_section_key(section: dict[str, Any], fallback_key: str | None = None) -> str:
    if fallback_key:
        return fallback_key
    title = str(section.get('title', '')).strip().lower()
    candidates = {
        'executive summary': 'executive_summary',
        'statistical highlights': 'statistical_highlights',
        'financial ratios': 'financial_ratios',
        'trend analysis': 'trend_analysis',
        'risk assessment': 'risk_assessment',
        'benchmark comparison': 'benchmark_comparison',
        'recommendations': 'recommendations',
        'wacc analysis': 'wacc_analysis',
        'money market analysis': 'money_market_analysis',
        'investment analysis': 'investment_analysis',
        'macroeconomic indicators': 'macroeconomic_indicators',
        'country risk analysis': 'country_risk_analysis',
        'market trends': 'market_trends',
    }
    return candidates.get(title, _slugify(title or 'section'))


def annotate_report_sections(
    report_id: str,
    sections: list[dict[str, Any]],
    report_options: dict[str, Any] | None = None,
    *,
    ai_model: str | None = None,
    confidence_score: float | None = None,
    regeneration_reason: str = 'initial generation',
    user=None,
) -> dict[str, Any]:
    """Attach prompt provenance to sections and persist the mapping."""
    ensure_prompt_modules()
    report_options = report_options or {}
    section_keys = list(report_options.get('sections') or [])
    annotated_sections: list[dict[str, Any]] = []
    mappings: list[dict[str, Any]] = []

    try:
        report = PersistedReport.objects.get(pk=str(report_id))
    except PersistedReport.DoesNotExist:
        report = None

    for index, section in enumerate(sections):
        section = dict(section)
        section_key = section.get('section_key') or section.get('key')
        if not section_key and index < len(section_keys):
            section_key = section_keys[index]
        section_key = _normalize_section_key(section, section_key)
        module = get_prompt_module_for_section(section_key)
        module_version = None
        if module:
            module_version = module.versions.order_by('-version_number').first()

        section_title = section.get('title') or (module.name if module else section_key.replace('_', ' ').title())
        section_content = section.get('content', {})
        content_hash = _hash_payload(section_content)
        section_hash = _hash_payload({'key': section_key, 'title': section_title})
        mapping_payload = {
            'section_key': section_key,
            'section_title': section_title,
            'prompt_module': serialize_prompt_module(module) if module else None,
            'prompt_module_version': serialize_prompt_module_version(module_version) if module_version else None,
            'ai_model': ai_model or report_options.get('ai_model') or '',
            'generation_timestamp': _now_iso(),
            'confidence_score': confidence_score,
            'generation_run_id': uuid.uuid4().hex,
            'section_content': section_content,
            'section_hash': section_hash,
            'content_hash': content_hash,
            'regeneration_reason': regeneration_reason,
        }
        section['section_key'] = section_key
        section['trace'] = {
            'prompt_module_id': module.id if module else None,
            'prompt_module_name': module.name if module else None,
            'prompt_module_slug': module.slug if module else None,
            'prompt_module_version': module_version.version_number if module_version else None,
            'ai_model': mapping_payload['ai_model'],
            'confidence_score': confidence_score,
            'generated_at': mapping_payload['generation_timestamp'],
        }
        annotated_sections.append(section)
        mappings.append(mapping_payload)

        if report is not None and module is not None:
            ReportSectionMapping.objects.update_or_create(
                report=report,
                section_key=section_key,
                defaults={
                    'section_title': section_title,
                    'prompt_module': module,
                    'prompt_module_version': module_version,
                    'ai_model': mapping_payload['ai_model'],
                    'confidence_score': confidence_score,
                    'generation_timestamp': timezone.now(),
                    'generation_run_id': mapping_payload['generation_run_id'],
                    'section_content': section_content,
                    'section_hash': section_hash,
                    'content_hash': content_hash,
                    'regeneration_reason': regeneration_reason,
                },
            )

    return {
        'sections': annotated_sections,
        'section_mappings': mappings,
    }


def build_prompt_module_payload(include_versions: bool = False) -> dict[str, Any]:
    modules = [serialize_prompt_module(module, include_versions=include_versions) for module in list_prompt_modules()]
    return {
        'prompt_modules': modules,
        'count': len(modules),
        'updated_at': _now_iso(),
    }


def get_report_section_mappings(report_id: str) -> list[dict[str, Any]]:
    try:
        report = PersistedReport.objects.get(pk=str(report_id))
    except PersistedReport.DoesNotExist:
        return []
    return [
        {
            'id': mapping.id,
            'report_id': str(mapping.report_id),
            'section_key': mapping.section_key,
            'section_title': mapping.section_title,
            'prompt_module': serialize_prompt_module(mapping.prompt_module) if mapping.prompt_module else None,
            'prompt_module_version': serialize_prompt_module_version(mapping.prompt_module_version) if mapping.prompt_module_version else None,
            'ai_model': mapping.ai_model,
            'generation_timestamp': mapping.generation_timestamp.isoformat() if mapping.generation_timestamp else None,
            'confidence_score': float(mapping.confidence_score) if mapping.confidence_score is not None else None,
            'generation_run_id': mapping.generation_run_id,
            'section_content': mapping.section_content,
            'section_hash': mapping.section_hash,
            'content_hash': mapping.content_hash,
            'regeneration_reason': mapping.regeneration_reason,
        }
        for mapping in report.section_mappings.all().order_by('section_key', '-generation_timestamp')
    ]


def apply_section_traceability(
    report_id: str,
    sections: list[dict[str, Any]],
    report_options: dict[str, Any] | None = None,
    *,
    ai_model: str | None = None,
    confidence_score: float | None = None,
    regeneration_reason: str = 'initial generation',
) -> list[dict[str, Any]]:
    result = annotate_report_sections(
        report_id,
        sections,
        report_options=report_options,
        ai_model=ai_model,
        confidence_score=confidence_score,
        regeneration_reason=regeneration_reason,
    )
    return result.get('sections') or []


def get_section_prompt_text(section_key: str, report_context: dict[str, Any] | None = None) -> str | None:
    module = get_prompt_module_for_section(section_key)
    if not module or module.status != 'active':
        return None
    text = (module.prompt_text or '').strip()
    if not text:
        return None
    report_context = report_context or {}
    return (
        text.replace('{bank_name}', str(report_context.get('bank_name', 'Financial Dataset')))
        .replace('{data_period}', str(report_context.get('data_period', 'Unknown Period')))
    )


def compose_master_prompt(
    section_keys: list[str],
    report_context: dict[str, Any] | None = None,
) -> str:
    """
    Compose a deterministic master prompt document that contains every section
    prompt wrapped in markers. The frontend decomposes this master prompt into
    per-section editors and regenerates using only the edited section prompt.
    """
    report_context = report_context or {}
    parts: list[str] = []
    for key in section_keys or []:
        section_key = str(key).strip()
        if not section_key:
            continue
        prompt_text = get_section_prompt_text(section_key, report_context) or ''
        parts.append(f"[SECTION:{section_key}]\n{prompt_text}\n[/SECTION]")
    return "\n\n".join(parts)


def decompose_master_prompt_to_section_prompts(
    master_prompt: str | None,
    section_keys: list[str] | None,
) -> dict[str, str]:
    """
    Decompose a single master prompt into per-section prompt texts.

    Strategy:
    1) If the master prompt already contains `[SECTION:<key>]...[/SECTION]`
       blocks, extract directly.
    2) Otherwise, attempt a best-effort heading-based split by searching for
       common section title variants and slicing until the next section match.
    """
    master_prompt = master_prompt or ''
    keys = section_keys or []
    if not master_prompt or not keys:
        return {}

    # 1) Marker-based extraction
    extracted: dict[str, str] = {}
    for key in keys:
        section_key = str(key).strip()
        if not section_key:
            continue
        re_marker = re.compile(
            rf"\[SECTION:{re.escape(section_key)}\]([\s\S]*?)\[/SECTION\]",
            flags=re.IGNORECASE,
        )
        m = re_marker.search(master_prompt)
        if m:
            val = (m.group(1) or '').strip()
            if val:
                extracted[section_key] = val

    if extracted:
        return extracted

    # 2) Heading-based extraction (best effort)
    title_variants: dict[str, list[str]] = {
        'executive_summary': ['Executive Summary'],
        'statistical_highlights': ['Statistical Highlights'],
        'financial_ratios': ['Financial Ratios', 'Ratio Analysis'],
        'wacc_analysis': ['WACC', 'Weighted Average Cost of Capital'],
        'money_market_analysis': ['Money Market', 'Money Market Analysis'],
        'investment_analysis': ['Financial Instruments', 'Investment Analysis'],
        'macroeconomic_indicators': ['Macroeconomic Indicators', 'Macro Indicators'],
        'country_risk_analysis': ['Country Risk', 'Sovereign Risk'],
        'market_trends': ['Market Trends'],
        'trend_analysis': ['Trend Analysis'],
        'risk_assessment': ['Risk Analysis', 'Risk Assessment'],
        'benchmark_comparison': ['Benchmark Comparison'],
        'recommendations': ['Recommendations'],
    }

    key_matches: list[tuple[int, str]] = []
    for key in keys:
        section_key = str(key).strip()
        if not section_key:
            continue
        variants = title_variants.get(section_key, []) or [section_key.replace('_', ' ').title()]
        best_idx: int | None = None
        for v in variants:
            m = re.search(re.escape(v), master_prompt, flags=re.IGNORECASE)
            if m:
                idx = m.start()
                if best_idx is None or idx < best_idx:
                    best_idx = idx
        if best_idx is not None:
            key_matches.append((best_idx, section_key))

    key_matches.sort(key=lambda x: x[0])
    if not key_matches:
        return {}

    for i, (start_idx, section_key) in enumerate(key_matches):
        end_idx = key_matches[i + 1][0] if i + 1 < len(key_matches) else len(master_prompt)
        chunk = master_prompt[start_idx:end_idx].strip()
        if chunk:
            extracted[section_key] = chunk

    return extracted


def compare_prompt_versions(module: PromptModule, from_version: int, to_version: int) -> dict[str, Any]:
    left = module.versions.filter(version_number=from_version).first()
    right = module.versions.filter(version_number=to_version).first()
    if not left or not right:
        raise ValueError('One or both versions were not found.')
    return {
        'module': serialize_prompt_module(module),
        'from_version': serialize_prompt_module_version(left),
        'to_version': serialize_prompt_module_version(right),
        'prompt_changed': left.prompt_text != right.prompt_text,
    }


@transaction.atomic
def duplicate_prompt_module(module: PromptModule, user=None) -> PromptModule:
    base_slug = f'{module.slug}-copy'
    slug = base_slug
    suffix = 2
    while PromptModule.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{suffix}'
        suffix += 1
    return create_prompt_module(
        {
            'name': f'{module.name} (Copy)',
            'slug': slug,
            'description': module.description,
            'category': module.category,
            'prompt_text': module.prompt_text,
            'order_index': module.order_index + 1,
            'tags': list(module.tags or []),
            'related_sections': list(module.related_sections or []),
            'status': 'draft',
            'ai_settings': deepcopy(module.ai_settings or {}),
        },
        user=user,
    )

