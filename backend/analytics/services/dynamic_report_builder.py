"""Dynamic report section generation helpers."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from .report_prompt_registry import get_report_prompt_registry


def build_dynamic_report_sections(
    sections: list[str],
    report_data: dict[str, Any],
    options: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    registry = get_report_prompt_registry()
    options = registry.build_report_options(options)
    selected_sections = registry.normalize_sections(
        template_name=options.get("template"),
        selected_sections=sections,
        include_sections=options.get("include_sections"),
        exclude_sections=options.get("exclude_sections"),
        available_sections=list(registry.get_section_library().keys()),
        length=options.get("length"),
        detail_level=options.get("detail_level"),
        output_format=options.get("output_format"),
    )

    built_sections = []
    for section_key in selected_sections:
        built_sections.append(build_section(section_key, report_data, options))
    return built_sections


def build_section(
    section_key: str,
    report_data: dict[str, Any],
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = get_report_prompt_registry()
    section_title = registry.get_section_definition(section_key).get(
        "title",
        section_key.replace("_", " ").title(),
    )
    builders = {
        "executive_summary": _build_executive_summary,
        "statistical_highlights": _build_statistical_highlights,
        "money_market_analysis": _build_money_market_analysis,
        "wacc_analysis": _build_wacc_analysis,
        "financial_ratios": _build_financial_ratios,
        "investment_analysis": _build_investment_analysis,
        "macroeconomic_indicators": _build_macroeconomic_indicators,
        "country_risk_analysis": _build_country_risk_analysis,
        "market_trends": _build_market_trends,
        "trend_analysis": _build_market_trends,
        "risk_assessment": _build_risk_assessment,
        "benchmark_comparison": _build_benchmark_comparison,
        "recommendations": _build_recommendations,
    }

    content_builder = builders.get(section_key, _build_generic_section)
    content = content_builder(report_data, options or {})

    return {
        "title": section_title,
        "content": content,
        "section_key": section_key,
    }


def build_report_context(report_data: dict[str, Any]) -> dict[str, Any]:
    bank_name = report_data.get("bank_name") or report_data.get("metadata", {}).get("bank_name") or "Financial Dataset"
    data_period = report_data.get("data_period") or report_data.get("metadata", {}).get("period") or "Unknown Period"
    available_data_sections = _detect_available_data_sections(report_data)
    return {
        "bank_name": bank_name,
        "data_period": data_period,
        "available_data_sections": available_data_sections,
        "metrics": _extract_numeric_metrics(report_data),
    }


def _detect_available_data_sections(report_data: dict[str, Any]) -> list[str]:
    sections = []
    if not isinstance(report_data, dict):
        return sections

    preferred_keys = [
        "dashboard",
        "qc_dashboard",
        "income_risk",
        "dupont",
        "country_risk",
        "country_risk_analysis",
        "money_market",
        "wacc",
        "market_trends",
        "macro",
        "macroeconomic_indicators",
        "investment",
        "financial_ratios",
    ]

    for key in preferred_keys:
        if key in report_data and report_data.get(key):
            sections.append(key)

    metadata = report_data.get("metadata", {})
    if isinstance(metadata, dict):
        for key in ("sections", "selected_sections"):
            values = metadata.get(key)
            if isinstance(values, list):
                for value in values:
                    if value not in sections:
                        sections.append(value)

    return sections


def build_statistics_bundle(report_data: dict[str, Any]) -> dict[str, Any]:
    metrics = _extract_numeric_metrics(report_data)
    if not metrics:
        return {
            "summary": "No numeric metrics available for statistical analysis.",
            "highlights": [],
            "best_performing": [],
            "worst_performing": [],
            "statistics": [],
        }

    entries = list(metrics.items())
    values = [payload["value"] for _, payload in entries]
    statistics = {
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "average": round(mean(values), 4),
    }

    ranked = sorted(entries, key=lambda item: _performance_score(item[0], item[1]["value"]), reverse=True)
    best = ranked[:3]
    worst = list(reversed(ranked[-3:])) if len(ranked) > 3 else ranked[-3:]

    highlights = []
    for name, payload in entries[:8]:
        highlights.append(
            {
                "metric": name,
                "value": payload["value"],
                "trend": payload["trend"],
            }
        )

    return {
        "summary": (
            f"Across {len(values)} numeric indicators, the minimum value is {statistics['min']}, "
            f"the maximum is {statistics['max']}, and the average is {statistics['average']}."
        ),
        "statistics": statistics,
        "highlights": highlights,
        "best_performing": [
            {"metric": name, "value": payload["value"], "label": payload["label"]}
            for name, payload in best
        ],
        "worst_performing": [
            {"metric": name, "value": payload["value"], "label": payload["label"]}
            for name, payload in worst
        ],
    }


def _build_executive_summary(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    context = build_report_context(report_data)
    stats = build_statistics_bundle(report_data)
    key_points = [
        f"Bank or entity: {context['bank_name']}",
        f"Period: {context['data_period']}",
    ]
    if stats["best_performing"]:
        key_points.append(f"Best indicator: {stats['best_performing'][0]['metric']}")
    if stats["worst_performing"]:
        key_points.append(f"Needs attention: {stats['worst_performing'][0]['metric']}")

    recommendations = [
        "Prioritize the weakest indicators and track them in the next reporting cycle.",
        "Use the strongest indicators as anchors for strategic planning and investor communication.",
    ]

    return {
        "content": (
            f"{context['bank_name']} shows a dynamic financial profile across {len(context['available_data_sections'])} data areas. "
            f"{stats['summary']} The report adapts to the selected sections and available data, so the narrative reflects only relevant components."
        ),
        "key_points": key_points,
        "recommendations": recommendations,
        "statistical_highlights": stats,
        "charts": _suggest_charts(context["available_data_sections"]),
        "tables": [
            {"name": "Selected Sections", "rows": context["available_data_sections"]},
        ],
    }


def _build_statistical_highlights(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    stats = build_statistics_bundle(report_data)
    return {
        "content": stats["summary"],
        "key_points": [
            f"Minimum value: {stats['statistics']['min']}" if stats["statistics"] else "Minimum value unavailable",
            f"Maximum value: {stats['statistics']['max']}" if stats["statistics"] else "Maximum value unavailable",
            f"Average value: {stats['statistics']['average']}" if stats["statistics"] else "Average value unavailable",
        ],
        "statistics": stats.get("statistics", {}),
        "best_performing": stats.get("best_performing", []),
        "worst_performing": stats.get("worst_performing", []),
        "statistical_highlights": stats,
    }


def _build_money_market_analysis(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    values = _extract_values_by_keywords(report_data, ["money_market", "interest_rate", "short_term", "liquidity", "funding"])
    return {
        "content": (
            "Money market analysis reviews short-term funding, rate sensitivity, and liquidity signals. "
            + _values_to_text(values)
        ),
        "key_points": _values_to_key_points(values, "Money market"),
        "tables": _values_to_tables(values),
    }


def _build_wacc_analysis(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    values = _extract_values_by_keywords(report_data, ["wacc", "cost_of_debt", "cost_of_equity", "capital_structure", "equity", "debt"])
    return {
        "content": (
            "WACC analysis assesses capital cost, funding mix, and valuation hurdles. "
            + _values_to_text(values)
        ),
        "key_points": _values_to_key_points(values, "WACC"),
        "tables": _values_to_tables(values),
    }


def _build_financial_ratios(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    metrics = _extract_numeric_metrics(report_data)
    ratios = _filter_metrics(metrics, ["roa", "roe", "margin", "ratio", "efficiency", "liquidity", "leverage", "capital"])
    return {
        "content": "Financial ratios summarize profitability, liquidity, leverage, and efficiency across the available dataset.",
        "key_points": [f"{name}: {payload['value']}" for name, payload in ratios[:8]] or ["No ratio metrics were detected in the selected data."],
        "tables": [
            {"name": "Financial Ratios", "rows": [{"metric": name, **payload} for name, payload in ratios[:10]]},
        ],
    }


def _build_investment_analysis(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    values = _extract_values_by_keywords(report_data, ["investment", "return", "valuation", "portfolio", "allocation", "yield"])
    return {
        "content": "Investment analysis combines returns, valuation, allocation, and risk tradeoffs into a decision-ready view.",
        "key_points": _values_to_key_points(values, "Investment"),
        "recommendations": [
            "Rebalance toward the strongest return-to-risk opportunities.",
            "Reduce exposure where downside risks exceed expected gains.",
        ],
        "tables": _values_to_tables(values),
    }


def _build_macroeconomic_indicators(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    values = _extract_values_by_keywords(report_data, ["gdp", "inflation", "cpi", "interest_rate", "fx", "exchange", "unemployment", "policy"])
    return {
        "content": "Macroeconomic indicators frame the external environment influencing financial performance and risk appetite.",
        "key_points": _values_to_key_points(values, "Macro"),
        "tables": _values_to_tables(values),
    }


def _build_country_risk_analysis(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    country_rows = _extract_country_risk_rows(report_data)
    if not country_rows:
        return {
            "content": "No country-specific risk dataset was found. The analysis is ready for country-level inputs when provided.",
            "key_points": ["Add a country risk dataset to enable cross-country ranking."],
        }

    ranked = sorted(country_rows, key=lambda row: row["risk_score"], reverse=True)
    return {
        "content": "Country risk analysis compares political, economic, currency, inflation, and sovereign exposure across markets.",
        "key_points": [
            f"Highest risk country: {ranked[0]['country']} ({ranked[0]['risk_level']})",
            f"Lowest risk country: {ranked[-1]['country']} ({ranked[-1]['risk_level']})",
        ],
        "tables": [
            {
                "name": "Country Risk Ranking",
                "rows": ranked,
            }
        ],
        "recommendations": [
            "Favour lower-risk markets for near-term capital deployment.",
            "Use higher-risk markets only with tighter pricing and governance controls.",
        ],
        "regional_outlook": _extract_regional_outlook(report_data),
    }


def _build_market_trends(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    trend_values = _extract_trend_series(report_data)
    return {
        "content": "Market trends highlight direction, volatility, and outliers across the available time series and market observations.",
        "key_points": [
            f"Trend series detected: {len(trend_values)}",
            "Review outliers, reversals, and large shifts in the selected dataset.",
        ],
        "charts": _suggest_charts(list(trend_values.keys())),
        "tables": [
            {"name": "Trend Series", "rows": [{"metric": key, "latest_change": value} for key, value in trend_values.items()]},
        ],
    }


def _build_risk_assessment(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    stats = build_statistics_bundle(report_data)
    return {
        "content": "Risk assessment combines financial risk drivers, country exposure, and abnormal movements in the selected data.",
        "key_points": [
            f"Best indicator: {stats['best_performing'][0]['metric']}" if stats["best_performing"] else "Best indicator unavailable",
            f"Worst indicator: {stats['worst_performing'][0]['metric']}" if stats["worst_performing"] else "Worst indicator unavailable",
        ],
        "risk_level": "dynamic",
    }


def _build_benchmark_comparison(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    values = _extract_values_by_keywords(report_data, ["benchmark", "peer", "comparison", "vs"])
    return {
        "content": "Benchmark comparison places the selected metrics next to benchmarks and peer signals.",
        "key_points": _values_to_key_points(values, "Benchmark"),
    }


def _build_recommendations(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    stats = build_statistics_bundle(report_data)
    recommendations = [
        "Focus execution on the worst-performing indicators first.",
        "Expand reporting depth in areas with high volatility or outliers.",
    ]
    if stats["best_performing"]:
        recommendations.append(f"Protect and scale the strengths behind {stats['best_performing'][0]['metric']}.")
    return {
        "content": "Recommendations are prioritized around performance gaps, volatility, and strategic opportunities.",
        "key_points": recommendations,
        "recommendations": recommendations,
    }


def _build_generic_section(report_data: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": "This section is generated dynamically from the available data and prompt configuration.",
        "key_points": ["Dynamic content was generated from the selected section registry."],
    }


def _extract_numeric_metrics(report_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    excluded_terms = {"period", "year", "date", "name", "bank_name", "data_period"}

    def walk(value: Any, path: list[str]) -> None:
        path_text = ".".join(path).lower()
        if any(term in path_text for term in excluded_terms):
            return
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, path + [str(key)])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + [str(index)])
        else:
            numeric_value = _coerce_number(value)
            if numeric_value is None:
                return
            label = " ".join(segment.replace("_", " ").title() for segment in path[-3:]) or "Metric"
            metrics[".".join(path)] = {
                "label": label,
                "value": numeric_value,
                "trend": _trend_label(numeric_value),
            }

    walk(
        {
            "dashboard": report_data.get("dashboard") or report_data.get("data_summary") or {},
            "qc_dashboard": report_data.get("qc_dashboard") or {},
            "income_risk": report_data.get("income_risk") or {},
            "dupont": report_data.get("dupont") or {},
            "metrics": report_data.get("metrics") or {},
        },
        [],
    )
    return metrics


def _filter_metrics(metrics: dict[str, dict[str, Any]], keywords: list[str]) -> list[tuple[str, dict[str, Any]]]:
    filtered = []
    for key, payload in metrics.items():
        key_lower = key.lower()
        if any(keyword in key_lower for keyword in keywords):
            filtered.append((key, payload))
    return filtered


def _extract_values_by_keywords(report_data: dict[str, Any], keywords: list[str]) -> list[tuple[str, Any]]:
    values: list[tuple[str, Any]] = []

    def walk(value: Any, path: list[str]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                walk(child, path + [str(key)])
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + [str(index)])
        else:
            path_text = " ".join(path).lower()
            if any(keyword in path_text for keyword in keywords):
                values.append((".".join(path), value))

    walk(report_data, [])
    return values[:12]


def _extract_trend_series(report_data: dict[str, Any]) -> dict[str, Any]:
    series = {}
    qc_dashboard = report_data.get("qc_dashboard", {})
    time_series = qc_dashboard.get("time_series", {})
    if isinstance(time_series, dict):
        for metric, values in time_series.items():
            if isinstance(values, list) and len(values) >= 2:
                first = _coerce_number(values[0])
                last = _coerce_number(values[-1])
                if first is not None and last is not None and first != 0:
                    series[metric] = round(((last - first) / abs(first)) * 100, 4)
    return series


def _extract_country_risk_rows(report_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    source = report_data.get("country_risk") or report_data.get("country_risk_analysis") or report_data.get("countries") or []
    if isinstance(source, dict):
        source = [source]
    if not isinstance(source, list):
        return rows

    for item in source:
        if not isinstance(item, dict):
            continue
        country = str(item.get("country") or item.get("name") or item.get("market") or "Unknown").strip()
        political = _coerce_number(item.get("political_risk")) or 0
        economic = _coerce_number(item.get("economic_risk")) or 0
        currency = _coerce_number(item.get("currency_risk")) or 0
        inflation = _coerce_number(item.get("inflation_risk")) or 0
        sovereign = _coerce_number(item.get("sovereign_risk")) or 0
        risk_score = _coerce_number(item.get("risk_score"))
        if risk_score is None:
            risk_score = mean([political, economic, currency, inflation, sovereign])
        rows.append(
            {
                "country": country,
                "political_risk": political,
                "economic_risk": economic,
                "currency_risk": currency,
                "inflation_risk": inflation,
                "sovereign_risk": sovereign,
                "risk_score": round(risk_score, 4),
                "risk_level": _risk_level(risk_score),
            }
        )

    return rows


def _extract_regional_outlook(report_data: dict[str, Any]) -> dict[str, Any]:
    outlook = report_data.get("regional_outlook") or report_data.get("market_outlook") or {}
    if isinstance(outlook, dict):
        return outlook
    return {"summary": str(outlook)}


def _values_to_text(values: list[tuple[str, Any]]) -> str:
    if not values:
        return "No dedicated values were found in the selected data."
    preview = ", ".join(f"{key.split('.')[-1]}={value}" for key, value in values[:5])
    return f"Detected values include {preview}."


def _values_to_key_points(values: list[tuple[str, Any]], label: str) -> list[str]:
    if not values:
        return [f"No {label.lower()} metrics were found in the selected dataset."]
    return [f"{key.split('.')[-1]}: {value}" for key, value in values[:5]]


def _values_to_tables(values: list[tuple[str, Any]]) -> list[dict[str, Any]]:
    if not values:
        return []
    return [
        {
            "name": "Detected Values",
            "rows": [{"metric": key.split(".")[-1], "value": value} for key, value in values[:8]],
        }
    ]


def _suggest_charts(labels: list[str]) -> list[dict[str, Any]]:
    if not labels:
        return []
    return [{"type": "bar", "title": "Selected Data Areas", "labels": labels[:10]}]


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("$", "").replace("%", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _risk_level(score: float) -> str:
    if score < 33:
        return "Low"
    if score < 66:
        return "Medium"
    return "High"


def _trend_label(value: float) -> str:
    if value > 0:
        return "Increasing"
    if value < 0:
        return "Decreasing"
    return "Stable"


def _performance_score(metric_name: str, value: float) -> float:
    metric_name = metric_name.lower()
    if any(keyword in metric_name for keyword in ["cost", "risk", "loss", "efficiency_ratio"]):
        return -value
    return value
