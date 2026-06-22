"""Persistent registry for dynamic report prompts and templates."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PROMPT_CONFIG: dict[str, Any] = {
    "version": "1.0",
    "system_prompt_template": """
You are a senior financial analyst and report writer. Analyze the provided JSON financial dashboard data and generate a comprehensive, professional financial report suitable for management, investors, and decision-makers.

### Instructions

Interpret all available financial metrics, ratios, trends, balances, durations, and performance indicators contained in the JSON. Adapt to the structure and naming of the data, even if some fields vary between datasets. Do not simply restate values—provide meaningful financial interpretation and business insights.

### Report Structure

## 1. Executive Summary

Provide a concise overview of the organization's financial condition, highlighting major strengths, weaknesses, opportunities, and key developments. Summarize the most important findings and overall financial outlook.

## 2. Financial Position Analysis

Evaluate:

* Assets, liabilities, equity, loans, and capital structure.
* Asset growth and composition.
* Loan portfolio quality and concentration.
* Leverage and solvency indicators.
* Trends and comparisons where historical data exists.

Explain implications for financial stability and long-term sustainability.

## 3. Profitability and Performance Analysis

Analyze:

* Revenue, income, expenses, margins, and earnings.
* Return on Assets (ROA), Return on Equity (ROE), Net Interest Margin (NIM), Cost-to-Income Ratio, and any profitability ratios available.
* Growth patterns and operational performance.

Explain whether profitability is improving or deteriorating and identify drivers of performance.

## 4. Liquidity Assessment

Assess:

* Liquidity ratios and cash position.
* Funding sources and obligations.
* Short-term solvency.
* Ability to meet operational and debt commitments.

Discuss liquidity strengths, weaknesses, and potential concerns.

## 5. Risk and Duration Analysis

Evaluate:

* Interest rate risk.
* Duration gap and sensitivity measures.
* Credit risk indicators.
* Asset and liability maturity mismatches.
* Concentration risks and exposure levels.

Explain how these factors affect financial stability and risk management.

## 6. Efficiency and Cost Analysis

Analyze:

* Operating expenses and cost structure.
* Efficiency ratios and utilization measures.
* Cost-to-income ratio and productivity indicators.
* Resource allocation and operational effectiveness.

Identify areas where efficiency can be improved.

## 7. Trend and Comparative Analysis

Where historical or benchmark data exists:

* Identify increasing or decreasing trends.
* Highlight significant changes.
* Compare current performance with previous periods or industry benchmarks.
* Discuss implications of observed patterns.

## 8. Ratio Interpretation

Interpret all ratios and KPIs found in the JSON, including:

* Liquidity ratios.
* Profitability ratios.
* Leverage ratios.
* Efficiency ratios.
* Asset quality indicators.
* Risk measures.

For each metric:

* Explain what it measures.
* State whether the value is favorable or unfavorable.
* Discuss its impact on profitability, liquidity, risk, and operational performance.

## 9. Key Findings

Present the most important observations as bullet points. Highlight:

* Major strengths.
* Areas of concern.
* Emerging risks.
* Opportunities for improvement.

## 10. Strategic Recommendations

Provide practical recommendations based on industry best practices. Include:

* Risk mitigation strategies.
* Cost optimization measures.
* Liquidity management improvements.
* Profitability enhancement opportunities.
* Asset-liability management recommendations.
* Operational efficiency initiatives.

Prioritize recommendations according to their potential impact.

## 11. Conclusion

Summarize the overall financial health and outlook of the organization. State whether the institution appears financially strong, stable, improving, deteriorating, or exposed to significant risks.

### Reporting Guidelines

* Use a professional management-report style.
* Provide analytical commentary rather than merely listing figures.
* Highlight minimum, maximum, average, and extreme values where applicable.
* Quantify trends and percentage changes whenever possible.
* Explain financial implications and business significance.
* Use tables where appropriate.
* Include concise bullet-point summaries after each section.
* Flag unusual values, inconsistencies, or warning signs.
* If some metrics are missing, analyze available information without making unsupported assumptions.
* Base conclusions solely on the provided data and established financial analysis principles.
* Ensure recommendations are actionable, evidence-based, and aligned with industry best practices.
""",
    "default_length": "standard",
    "default_detail_level": "balanced",
    "section_library": {
        "executive_summary": {
            "title": "Executive Summary",
            "description": "Concise summary of key findings, anomalies, highlights, and recommendations.",
        },
        "statistical_highlights": {
            "title": "Statistical Highlights",
            "description": "Minimum, maximum, average, trend, and best/worst indicator review.",
        },
        "money_market_analysis": {
            "title": "Money Market Analysis",
            "description": "Short-term liquidity, rates, and money market conditions.",
        },
        "wacc_analysis": {
            "title": "WACC Analysis",
            "description": "Cost of capital, capital structure, and weighted average cost of capital review.",
        },
        "financial_ratios": {
            "title": "Financial Ratios",
            "description": "Profitability, liquidity, leverage, and efficiency ratio assessment.",
        },
        "investment_analysis": {
            "title": "Investment Analysis",
            "description": "Return, valuation, allocation, and investment opportunity review.",
        },
        "macroeconomic_indicators": {
            "title": "Macroeconomic Indicators",
            "description": "Inflation, GDP, rates, exchange rates, and market-wide indicators.",
        },
        "country_risk_analysis": {
            "title": "Country Risk Analysis",
            "description": "Political, economic, currency, inflation, sovereign, and regional risk comparison.",
        },
        "market_trends": {
            "title": "Market Trends",
            "description": "Directional market movements, volatility, outliers, and outlook commentary.",
        },
        "risk_assessment": {
            "title": "Risk Assessment",
            "description": "Overall risk posture and key risk drivers.",
        },
        "benchmark_comparison": {
            "title": "Benchmark Comparison",
            "description": "Comparison against benchmarks and peer positioning.",
        },
        "recommendations": {
            "title": "Recommendations",
            "description": "Priority actions and implementation guidance.",
        },
    },
    "templates": {
        "one_page_summary": {
            "name": "One-Page Summary Report",
            "length": "short",
            "detail_level": "brief",
            "sections": [
                "executive_summary",
                "statistical_highlights",
                "recommendations",
            ],
        },
        "three_page_standard": {
            "name": "Three-Page Standard Report",
            "length": "standard",
            "detail_level": "balanced",
            "sections": [
                "executive_summary",
                "statistical_highlights",
                "financial_ratios",
                "trend_analysis",
                "risk_assessment",
                "recommendations",
            ],
        },
        "comprehensive_multi_page": {
            "name": "Comprehensive Multi-Page Report",
            "length": "long",
            "detail_level": "detailed",
            "sections": [
                "executive_summary",
                "statistical_highlights",
                "money_market_analysis",
                "wacc_analysis",
                "financial_ratios",
                "investment_analysis",
                "macroeconomic_indicators",
                "country_risk_analysis",
                "market_trends",
                "trend_analysis",
                "risk_assessment",
                "benchmark_comparison",
                "recommendations",
            ],
        },
        "custom": {
            "name": "Custom Report",
            "length": "custom",
            "detail_level": "custom",
            "sections": [],
        },
    },
}


class ReportPromptRegistry:
    """Load and persist report prompt definitions."""

    def __init__(self, config_path: str | Path | None = None):
        self.config_path = Path(config_path) if config_path else self._default_config_path()
        self._config: dict[str, Any] | None = None

    def _default_config_path(self) -> Path:
        return Path(__file__).resolve().parents[2] / "report_prompt_config.json"

    def load(self) -> dict[str, Any]:
        if self._config is not None:
            return self._config

        config = deepcopy(DEFAULT_REPORT_PROMPT_CONFIG)
        if self.config_path.exists():
            try:
                loaded = json.loads(self.config_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    config = self._merge(config, loaded)
            except (OSError, json.JSONDecodeError):
                pass

        self._config = config
        return config

    def save(self, config: dict[str, Any]) -> dict[str, Any]:
        merged = self._merge(deepcopy(DEFAULT_REPORT_PROMPT_CONFIG), config)
        self.config_path.write_text(
            json.dumps(merged, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        self._config = merged
        return merged

    def get_section_library(self) -> dict[str, Any]:
        return deepcopy(self.load().get("section_library", {}))

    def get_templates(self) -> dict[str, Any]:
        return deepcopy(self.load().get("templates", {}))

    def get_template(self, template_name: str) -> dict[str, Any]:
        templates = self.get_templates()
        template = templates.get(template_name) or templates.get("custom") or {}
        return deepcopy(template)

    def normalize_sections(
        self,
        template_name: str | None = None,
        selected_sections: list[str] | None = None,
        include_sections: list[str] | None = None,
        exclude_sections: list[str] | None = None,
        available_sections: list[str] | None = None,
        output_format: str | None = None,
        length: str | None = None,
        detail_level: str | None = None,
    ) -> list[str]:
        template = self.get_template(template_name or "custom")
        template_sections = list(template.get("sections", []))

        resolved = []
        for section in selected_sections or []:
            if section not in resolved:
                resolved.append(section)

        for section in include_sections or []:
            if section not in resolved:
                resolved.append(section)

        if not resolved:
            resolved.extend(template_sections)

        if not resolved and (template_name in {None, '', 'custom'}):
            resolved = ['executive_summary', 'statistical_highlights', 'recommendations']

        if not resolved:
            resolved = list(self.get_section_library().keys())

        if available_sections:
            resolved = [section for section in resolved if section in available_sections]

        if exclude_sections:
            excluded = set(exclude_sections)
            resolved = [section for section in resolved if section not in excluded]

        if length == "short":
            short_sections = ["executive_summary", "statistical_highlights", "recommendations"]
            resolved = [section for section in resolved if section in short_sections]
        elif length == "standard":
            standard_sections = [
                "executive_summary",
                "statistical_highlights",
                "financial_ratios",
                "trend_analysis",
                "risk_assessment",
                "recommendations",
            ]
            resolved = [section for section in resolved if section in standard_sections]

        if not resolved:
            resolved = ["executive_summary", "statistical_highlights", "recommendations"]

        return self._dedupe(resolved)

    def build_report_options(self, options: dict[str, Any] | None = None) -> dict[str, Any]:
        options = options or {}
        template_name = options.get("template") or options.get("template_type") or "custom"
        selected_sections = options.get("sections") or options.get("selected_sections") or []
        include_sections = options.get("include_sections") or []
        exclude_sections = options.get("exclude_sections") or []
        length = options.get("length") or self.load().get("default_length", "standard")
        detail_level = options.get("detail_level") or self.load().get("default_detail_level", "balanced")
        output_format = options.get("output_format") or options.get("format") or "json"

        if template_name in {"one_page", "summary"}:
            template_name = "one_page_summary"
        elif template_name in {"three_page", "standard"}:
            template_name = "three_page_standard"
        elif template_name in {"comprehensive", "long"}:
            template_name = "comprehensive_multi_page"

        template = self.get_template(template_name)
        available_sections = list(self.get_section_library().keys())
        sections = self.normalize_sections(
            template_name=template_name,
            selected_sections=selected_sections,
            include_sections=include_sections,
            exclude_sections=exclude_sections,
            available_sections=available_sections,
            output_format=output_format,
            length=length,
            detail_level=detail_level,
        )

        return {
            "template": template_name,
            "template_name": template.get("name", template_name),
            "length": length,
            "detail_level": detail_level,
            "output_format": output_format,
            "sections": sections,
            "include_sections": include_sections,
            "exclude_sections": exclude_sections,
        }

    def build_system_prompt(self, report_context: dict[str, Any], options: dict[str, Any] | None = None) -> str:
        options = self.build_report_options(options)
        section_library = self.get_section_library()

        ordered_sections = []
        for section_key in options["sections"]:
            section = section_library.get(section_key, {})
            ordered_sections.append(f"- {section.get('title', section_key)}: {section.get('description', '')}")

        available_data = report_context.get("available_data_sections", [])
        # Use editable template from config when present so it can be persisted and refined
        config = self.load()
        template = config.get("system_prompt_template")
        selected_sections_block = "\n".join(ordered_sections)
        fmt = {
            "template_name": options.get("template_name", options.get("template", "custom")),
            "length": options.get("length", "standard"),
            "detail_level": options.get("detail_level", "balanced"),
            "output_format": options.get("output_format", "json"),
            "bank_name": report_context.get("bank_name", "Financial Dataset"),
            "data_period": report_context.get("data_period", "Unknown Period"),
            "available_data": ", ".join(available_data) if available_data else "unknown",
            "selected_sections_block": selected_sections_block,
        }

        if template and isinstance(template, str):
            try:
                return template.format(**fmt)
            except Exception:
                # Fall back to generated prompt if formatting fails
                pass

        # Fallback (legacy) prompt
        return (
            "You are a senior financial analyst. Build a professional report that adapts to the selected sections and available data.\n"
            f"Report template: {options['template_name']}.\n"
            f"Report length: {options['length']}.\n"
            f"Detail level: {options['detail_level']}.\n"
            f"Output format: {options['output_format']}.\n"
            f"Bank or entity: {report_context.get('bank_name', 'Financial Dataset')}.\n"
            f"Period: {report_context.get('data_period', 'Unknown Period')}.\n"
            f"Available data areas: {', '.join(available_data) if available_data else 'unknown'}.\n"
            "Selected report sections:\n"
            + "\n".join(ordered_sections)
            + "\nReturn valid JSON with a sections array. Each section should include a title and a content object with content, key_points, recommendations, charts, tables, and statistical_highlights where relevant."
        )

    def get_section_definition(self, section_key: str) -> dict[str, Any]:
        return deepcopy(self.get_section_library().get(section_key, {}))

    def get_section_prompt(self, section_key: str, report_context: dict[str, Any]) -> str:
        bank_name = report_context.get("bank_name", "Financial Dataset")
        data_period = report_context.get("data_period", "Unknown Period")
        section_title = self.get_section_definition(section_key).get("title", section_key.replace("_", " ").title())
        available_data = ", ".join(report_context.get("available_data_sections", []) or ["unknown"])

        prompt_map = {
            "executive_summary": (
                f"Write a concise executive summary for {bank_name} for {data_period}. "
                "Include key findings, important trends and anomalies, short bullet highlights for the entire report, and major recommendations. "
                "Keep it executive-ready and concise."
            ),
            "statistical_highlights": (
                "Summarize minimum, maximum, average, and trend values for all relevant metrics. "
                "Call out best-performing and worst-performing indicators. "
                "Use tables or bullets where useful."
            ),
            "money_market_analysis": (
                "Analyze money market conditions, short-term rates, liquidity conditions, and funding pressure. "
                "Highlight rate movements, liquidity signals, and implications for near-term funding costs."
            ),
            "wacc_analysis": (
                "Assess weighted average cost of capital using available debt, equity, and capital structure data. "
                "Estimate the cost drivers, compare capital mix, and explain valuation and hurdle-rate implications."
            ),
            "financial_ratios": (
                "Evaluate key financial ratios including profitability, liquidity, leverage, and efficiency. "
                "Identify strong and weak ratio areas and explain what they mean for performance."
            ),
            "investment_analysis": (
                "Assess investment attractiveness, expected return, capital allocation, valuation, and opportunity/risk tradeoffs. "
                "Provide a clear investment view with supporting evidence."
            ),
            "macroeconomic_indicators": (
                "Analyze macroeconomic indicators such as inflation, GDP, interest rates, unemployment, FX, and policy signals. "
                "Connect macro conditions to financial performance and outlook."
            ),
            "country_risk_analysis": (
                "Compare country investment risk across political, economic, currency, inflation, and sovereign dimensions. "
                "Rank countries by risk level (Low, Medium, High), explain the drivers, and include regional and global outlooks."
            ),
            "market_trends": (
                "Describe market trends, outliers, major shifts, and directional changes. "
                "Highlight the biggest movements and give a forward-looking outlook."
            ),
            "risk_assessment": (
                "Assess overall financial risk, key risk drivers, and mitigation priorities. "
                "Summarize the main exposures and provide a clear risk rating."
            ),
            "benchmark_comparison": (
                "Compare the entity against benchmarks or peers, explain performance gaps, and highlight competitive positioning."
            ),
            "recommendations": (
                "Provide prioritized recommendations with expected impact, urgency, and feasibility. "
                "Keep the list practical and action-oriented."
            ),
        }

        prompt = prompt_map.get(
            section_key,
            f"Write the {section_title} section using the available data for {bank_name} ({data_period}). "
            f"Use only the information available in these data areas: {available_data}.",
        )
        return prompt

    def _merge(self, base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
        for key, value in updates.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                base[key] = self._merge(base[key], value)
            else:
                base[key] = deepcopy(value)
        return base

    def _dedupe(self, values: list[str]) -> list[str]:
        deduped: list[str] = []
        for value in values:
            if value not in deduped:
                deduped.append(value)
        return deduped


_REGISTRY: ReportPromptRegistry | None = None


def get_report_prompt_registry() -> ReportPromptRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = ReportPromptRegistry()
    return _REGISTRY
