"""Default AI analysis prompt definitions."""

from __future__ import annotations

from pathlib import Path

from .report_prompt_registry import DEFAULT_REPORT_PROMPT_CONFIG

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

FINANCIAL_DASHBOARD_ID = "financial_dashboard"
CAPITAL_ADEQUACY_CRIPE_ID = "capital_adequacy_cripe"


def _load_capital_adequacy_default() -> str:
    path = _DATA_DIR / "capital_adequacy_cripe_prompt.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "Analyze capital adequacy using the provided financial dataset."


def get_default_analysis_prompt_definitions() -> list[dict]:
    """Return the two built-in analysis prompts with metadata."""
    return [
        {
            "prompt_id": FINANCIAL_DASHBOARD_ID,
            "title": "Financial Dashboard (Management Report)",
            "content": DEFAULT_REPORT_PROMPT_CONFIG["system_prompt_template"].strip(),
            "recommended_sections": [
                "executive_summary",
                "financial_ratios",
                "risk_assessment",
                "recommendations",
            ],
        },
        {
            "prompt_id": CAPITAL_ADEQUACY_CRIPE_ID,
            "title": "Capital Adequacy (CRIPE)",
            "content": _load_capital_adequacy_default(),
            "recommended_sections": [
                "executive_summary",
                "financial_ratios",
                "wacc_analysis",
                "risk_assessment",
                "benchmark_comparison",
                "recommendations",
            ],
        },
    ]
