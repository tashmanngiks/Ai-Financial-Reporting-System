"""Default AI analysis prompt definitions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .report_prompt_registry import DEFAULT_REPORT_PROMPT_CONFIG

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

FINANCIAL_DASHBOARD_ID = "financial_dashboard"
CAPITAL_ADEQUACY_CRIPE_ID = "capital_adequacy_cripe"
WACC_ANALYSIS_ID = "wacc_analysis"
MONEY_MARKET_ANALYSIS_ID = "money_market_analysis"
FINANCIAL_INSTRUMENTS_ANALYSIS_ID = "financial_instruments_analysis"


def _load_capital_adequacy_default() -> str:
    path = _DATA_DIR / "capital_adequacy_cripe_prompt.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return "Analyze capital adequacy using the provided financial dataset."


def _section_block(section_key: str, title: str, instruction: str) -> str:
    return (
        f"[SECTION:{section_key}]\n"
        f"## {title}\n"
        f"{instruction.strip()}\n"
        f"[/SECTION]"
    )


def _build_master_prompt(
    *,
    title: str,
    context: str,
    role: str,
    objective: str,
    analysis_focus: list[str],
    calculations: list[str],
    validation_rules: list[str],
    report_sections: list[dict[str, str]],
) -> str:
    focus_block = "\n".join(f"- {item}" for item in analysis_focus)
    calculation_block = "\n".join(f"- {item}" for item in calculations)
    validation_block = "\n".join(f"- {item}" for item in validation_rules)
    section_blocks = "\n\n".join(
        _section_block(
            str(item["key"]).strip(),
            str(item["title"]).strip(),
            str(item["instruction"]).strip(),
        )
        for item in report_sections
        if item.get("key") and item.get("title") and item.get("instruction")
    )

    return f"""
# {title}

## Context
{context}

## Role
{role}

## Objective
{objective}

## Analytical Framework
Use the uploaded dataset as the only source of truth. Do not infer values that are not explicitly present. Where the dataset contains partial information, explain the limitation and continue with the evidence that is available.

## Required Analysis
{focus_block}

## Required Calculations
{calculation_block}

## Validation Rules
{validation_block}

## Writing Rules
- The executive summary is the only section that may contain concise bullet points.
- Every other section must be written as a professional report in full paragraphs.
- Do not create a separate "Key Findings" section.
- If a section needs emphasis, use short subheadings or tables rather than bullet lists.
- Never fabricate missing values or benchmarks.
- State clearly when a required field is missing.
- Keep recommendations practical, prioritized, and tied to the data.

## Report Structure
Generate every section below. Each marked block is the exact prompt module for that report section.

{section_blocks}

## Conclusion Rule
Conclude with a clear overall assessment of the selected dataset type, the major risks, and the highest-priority strategic actions.
""".strip()


WACC_ANALYSIS_PROMPT = _build_master_prompt(
    title="WACC Master Prompt",
    context=(
        "The user has uploaded a dataset selected as WACC. The report must focus exclusively on "
        "weighted average cost of capital, capital structure, financing efficiency, and the "
        "relationship between debt, equity, tax effects, and strategic capital deployment."
    ),
    role=(
        "You are a senior corporate finance analyst and capital structure advisor. Your job is to "
        "translate WACC dataset inputs into a board-ready report that explains the cost of capital, "
        "what is driving it, and how management can improve it."
    ),
    objective=(
        "Assess the cost of equity, cost of debt, tax effects, leverage, and capital structure. "
        "Explain the weighted average cost of capital, identify what is increasing or reducing it, "
        "and recommend actions that improve financing efficiency without understating risk."
    ),
    analysis_focus=[
        "Cost of Equity and the assumptions driving it.",
        "Cost of Debt, interest expense, borrowing mix, and debt pricing.",
        "Capital Structure, including debt-to-equity balance and leverage posture.",
        "Tax Rate impact on after-tax financing cost.",
        "Weighted Average Cost of Capital and whether it is rising or falling.",
        "Financing Efficiency, capital optimization, and risk-return tradeoffs.",
        "Strategic recommendations for capital deployment, refinancing, and hurdle rates.",
    ],
    calculations=[
        "Calculate WACC using only the provided dataset inputs and show the logic used.",
        "If equity or debt weights are available, explain how the mix affects the final WACC.",
        "Compare the implied hurdle rate with the cost of capital and discuss whether projects can clear it.",
        "Highlight sensitivity to tax rate changes, refinancing assumptions, and leverage adjustments.",
        "If benchmark or peer values are available, compare the current WACC to them.",
    ],
    validation_rules=[
        "If the dataset is not about WACC, stop and return a validation message instead of analyzing it.",
        "If cost of equity, cost of debt, tax rate, or capital structure fields are missing, identify the missing items explicitly.",
        "Do not use unrelated sections such as money market or instrument valuation metrics unless they directly support WACC analysis.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Provide a concise board-ready overview of the WACC position, capital structure posture, "
                "key cost drivers, and the most important financing implications from the dataset."
            ),
        },
        {
            "key": "wacc_analysis",
            "title": "WACC Analysis",
            "instruction": (
                "Explain cost of equity, cost of debt, tax effects, capital weights, and the resulting WACC. "
                "Show the calculation logic using only dataset inputs and interpret what is driving the result."
            ),
        },
        {
            "key": "financial_ratios",
            "title": "Financial Ratios",
            "instruction": (
                "Interpret leverage, coverage, profitability, and efficiency ratios that explain the capital "
                "structure and financing cost. Tie each ratio back to WACC implications."
            ),
        },
        {
            "key": "risk_assessment",
            "title": "Risk Assessment",
            "instruction": (
                "Evaluate financing, leverage, refinancing, interest-rate, and tax-related risks that affect "
                "the cost of capital. Rank severity and note early-warning indicators present in the data."
            ),
        },
        {
            "key": "benchmark_comparison",
            "title": "Benchmark Comparison",
            "instruction": (
                "Compare the observed WACC and capital structure signals with any peer, historical, or "
                "hurdle-rate benchmarks available in the dataset. State clearly when benchmarks are missing."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized strategic recommendations for capital deployment, refinancing, leverage "
                "management, and hurdle-rate discipline, each tied to evidence in the dataset."
            ),
        },
    ],
)


MONEY_MARKET_ANALYSIS_PROMPT = _build_master_prompt(
    title="Money Market Master Prompt",
    context=(
        "The uploaded dataset has been selected as Money Market. The report must focus on short-term "
        "funding conditions, money market instruments, liquidity behavior, and near-term rate dynamics."
    ),
    role=(
        "You are a money market strategist and liquidity analyst. Your analysis should explain how short-term "
        "rates, market conditions, and liquidity pressures affect funding cost, market performance, and risk."
    ),
    objective=(
        "Assess the state of the money market using the dataset only. Explain movements in Treasury Bills, "
        "commercial paper, certificates of deposit, interbank rates, repo rates, liquidity conditions, and "
        "short-term investment outcomes."
    ),
    analysis_focus=[
        "Treasury Bills and pricing behavior.",
        "Commercial Paper and short-term corporate funding signals.",
        "Certificates of Deposit and deposit competition.",
        "Interbank Rates and funding market stress.",
        "Repo Rates and secured funding conditions.",
        "Liquidity Conditions, rate trends, and market performance.",
        "Risk assessment and recommendations for short-term funding strategy.",
    ],
    calculations=[
        "Summarize rate movements, spreads, and trend direction from the dataset.",
        "Explain the liquidity implication of each market indicator that is present.",
        "Identify whether conditions are easing, tightening, or stable.",
        "Compare available rates or spreads against any benchmark or historical series in the file.",
    ],
    validation_rules=[
        "If the dataset is not about Money Market activity, stop and return a validation message instead of analyzing it.",
        "If required rate series or liquidity fields are missing, identify them explicitly.",
        "Do not mix in WACC or financial instruments analysis unless the data directly supports a money market conclusion.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Summarize short-term funding conditions, the dominant rate/liquidity signals, and the key "
                "implications for money-market strategy from the dataset."
            ),
        },
        {
            "key": "money_market_analysis",
            "title": "Money Market Analysis",
            "instruction": (
                "Analyze Treasury Bills, commercial paper, certificates of deposit, interbank rates, and repo "
                "rates. Explain what the instruments and spreads say about funding conditions."
            ),
        },
        {
            "key": "market_trends",
            "title": "Market Trends",
            "instruction": (
                "Interpret rate and liquidity trends over the available period. Identify whether conditions "
                "are easing, tightening, or stable and explain the drivers present in the data."
            ),
        },
        {
            "key": "risk_assessment",
            "title": "Risk Assessment",
            "instruction": (
                "Assess short-term funding, liquidity, counterparty, and rate risks. Highlight early-warning "
                "signals and the severity of each risk using only the uploaded evidence."
            ),
        },
        {
            "key": "benchmark_comparison",
            "title": "Benchmark Comparison",
            "instruction": (
                "Compare observed money-market rates and spreads with any historical or reference benchmarks "
                "in the dataset. Call out gaps where benchmark data is unavailable."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized recommendations for short-term funding, liquidity positioning, and "
                "money-market strategy, each linked to dataset evidence."
            ),
        },
    ],
)


FINANCIAL_INSTRUMENTS_ANALYSIS_PROMPT = _build_master_prompt(
    title="Financial Instruments Master Prompt",
    context=(
        "The uploaded dataset has been selected as Financial Instruments. The report must focus on investable "
        "instruments, valuation, portfolio behavior, and risk exposures across markets and asset classes."
    ),
    role=(
        "You are a financial markets analyst and portfolio strategist. Your analysis should translate the "
        "dataset into a professional investment report for decision-makers."
    ),
    objective=(
        "Assess the performance, valuation, and risk profile of bonds, equities, treasury securities, derivatives, "
        "mutual funds, ETFs, commodities, and foreign exchange instruments using only the uploaded data."
    ),
    analysis_focus=[
        "Bond pricing, duration, yield, and credit quality.",
        "Equity performance, returns, volatility, and valuation signals.",
        "Treasury securities and rate sensitivity.",
        "Derivatives and embedded leverage or hedging behavior.",
        "Mutual funds and ETFs, including allocation and performance patterns.",
        "Commodities and foreign exchange exposure.",
        "Portfolio performance, investment risk, and market valuation.",
    ],
    calculations=[
        "Interpret price, return, and risk metrics only from the uploaded dataset.",
        "If multiple instrument classes are present, compare performance and risk across them.",
        "Highlight concentration, diversification, or hedging implications.",
        "Use benchmark values only when they appear in the file and are clearly identified.",
    ],
    validation_rules=[
        "If the dataset is not about Financial Instruments, stop and return a validation message instead of analyzing it.",
        "If key instrument classes or valuation fields are missing, identify the missing information explicitly.",
        "Do not fabricate market prices, returns, or risk measures.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Provide a concise investment overview covering portfolio posture, valuation signals, "
                "material risks, and the highest-priority findings from the instruments dataset."
            ),
        },
        {
            "key": "investment_analysis",
            "title": "Investment Analysis",
            "instruction": (
                "Analyze bonds, equities, treasuries, derivatives, funds/ETFs, commodities, and FX exposures "
                "present in the data. Interpret valuation, return, and portfolio implications."
            ),
        },
        {
            "key": "market_trends",
            "title": "Market Trends",
            "instruction": (
                "Explain performance and market trends across instrument classes. Identify improving or "
                "deteriorating patterns and what they imply for positioning."
            ),
        },
        {
            "key": "financial_ratios",
            "title": "Financial Ratios",
            "instruction": (
                "Interpret available valuation, return, volatility, duration, and efficiency metrics. "
                "Explain what each material ratio means for portfolio quality and risk."
            ),
        },
        {
            "key": "risk_assessment",
            "title": "Risk Assessment",
            "instruction": (
                "Evaluate market, credit, liquidity, concentration, leverage, and FX risks across the "
                "instrument set. Prioritize severity and mitigation implications from the data."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized portfolio and risk-management recommendations tied directly to the "
                "instrument evidence in the dataset."
            ),
        },
    ],
)


def get_default_analysis_prompt_definitions() -> list[dict[str, Any]]:
    """Return the built-in analysis prompts with metadata."""
    return [
        {
            "prompt_id": WACC_ANALYSIS_ID,
            "title": "WACC Analysis",
            "content": WACC_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "wacc_analysis",
                "financial_ratios",
                "risk_assessment",
                "benchmark_comparison",
                "recommendations",
            ],
        },
        {
            "prompt_id": MONEY_MARKET_ANALYSIS_ID,
            "title": "Money Market Analysis",
            "content": MONEY_MARKET_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "money_market_analysis",
                "market_trends",
                "risk_assessment",
                "benchmark_comparison",
                "recommendations",
            ],
        },
        {
            "prompt_id": FINANCIAL_INSTRUMENTS_ANALYSIS_ID,
            "title": "Financial Instruments Analysis",
            "content": FINANCIAL_INSTRUMENTS_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "investment_analysis",
                "market_trends",
                "financial_ratios",
                "risk_assessment",
                "recommendations",
            ],
        },
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
