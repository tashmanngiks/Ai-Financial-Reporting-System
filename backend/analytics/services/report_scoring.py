"""Derive overall_score and risk_level from uploaded report / JSON data."""

from __future__ import annotations

from typing import Any


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(',', '').replace('$', '').replace('%', '').strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _walk_numeric_fields(obj: Any, prefix: str = '', depth: int = 0) -> dict[str, float]:
    if depth > 8 or obj is None:
        return {}
    found: dict[str, float] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f'{prefix}.{key}' if prefix else str(key)
            number = _coerce_number(value)
            if number is not None:
                found[path] = number
            elif isinstance(value, (dict, list)):
                found.update(_walk_numeric_fields(value, path, depth + 1))
    elif isinstance(obj, list):
        for index, item in enumerate(obj[:80]):
            path = f'{prefix}[{index}]' if prefix else f'[{index}]'
            found.update(_walk_numeric_fields(item, path, depth + 1))
    return found


def _first_matching(numerics: dict[str, float], keywords: tuple[str, ...]) -> float | None:
    for path, value in numerics.items():
        lower = path.lower()
        if any(keyword in lower for keyword in keywords):
            return value
    return None


def _score_from_bank_ratios(numerics: dict[str, float]) -> tuple[float, str] | None:
    roa = _first_matching(numerics, ('roa', 'return_on_assets', 'return on assets'))
    roe = _first_matching(numerics, ('roe', 'return_on_equity', 'return on equity'))
    efficiency = _first_matching(numerics, ('efficiency_ratio', 'efficiency ratio', 'cost_to_income', 'cost-to-income'))
    npl = _first_matching(numerics, ('npl', 'non_performing', 'non-performing', 'loss_rate'))
    capital = _first_matching(numerics, ('capital_adequacy', 'tier1', 'tier_1', 'cet1'))
    liquidity = _first_matching(numerics, ('liquidity_ratio', 'liquidity', 'lcr'))

    signals = [v for v in (roa, roe, efficiency, npl, capital, liquidity) if v is not None]
    if len(signals) < 2:
        return None

    score = 55.0
    if roa is not None:
        if roa > 1.5:
            score += 12
        elif roa > 1.0:
            score += 8
        elif roa > 0.5:
            score += 4
        elif roa < 0:
            score -= 12

    if roe is not None:
        if roe > 15:
            score += 12
        elif roe > 10:
            score += 8
        elif roe > 5:
            score += 4
        elif roe < 0:
            score -= 10

    if efficiency is not None:
        # Lower efficiency ratio is better for banks.
        if efficiency < 50:
            score += 10
        elif efficiency < 60:
            score += 6
        elif efficiency > 75:
            score -= 10
        elif efficiency > 65:
            score -= 4

    if npl is not None:
        if npl < 2:
            score += 8
        elif npl < 5:
            score += 3
        elif npl > 10:
            score -= 15
        elif npl > 7:
            score -= 8

    if capital is not None:
        if capital >= 15:
            score += 8
        elif capital >= 12:
            score += 5
        elif capital < 8:
            score -= 15
        elif capital < 10:
            score -= 8

    if liquidity is not None:
        # Treat small decimals (0.0x) as rates; larger values as ratios/percents.
        liq = liquidity * 100 if 0 < liquidity < 1 else liquidity
        if liq >= 30:
            score += 5
        elif liq < 10:
            score -= 10
        elif liq < 20:
            score -= 4

    score = max(0.0, min(100.0, round(score, 1)))
    return score, _risk_from_score(score)


def _score_from_summary_totals(numerics: dict[str, float]) -> tuple[float, str] | None:
    assets = _first_matching(numerics, ('total_assets', 'total assets'))
    if assets is None:
        assets = _first_matching(numerics, ('total_money_market_investments',))
    income = _first_matching(
        numerics,
        ('total_income', 'net_income', 'interest_income', 'revenue'),
    )
    expenses = _first_matching(numerics, ('total_expenses', 'operating_expenses', 'expenses'))
    net_change = _first_matching(numerics, ('net_change', 'net_profit', 'profit'))

    adjustments = 0
    score = 50.0
    if income is not None and assets and assets > 0:
        margin = (income / assets) * 100
        adjustments += 1
        if margin > 5:
            score += 15
        elif margin > 2:
            score += 10
        elif margin > 0.5:
            score += 5
        elif margin < 0:
            score -= 10

    if net_change is not None:
        adjustments += 1
        if net_change > 0:
            score += 12
        elif net_change < 0:
            score -= 12

    if income is not None and expenses is not None and income != 0:
        adjustments += 1
        cost_ratio = (expenses / abs(income)) * 100
        if cost_ratio < 40:
            score += 10
        elif cost_ratio < 70:
            score += 4
        elif cost_ratio > 100:
            score -= 12
        elif cost_ratio > 85:
            score -= 6

    # Need at least one meaningful financial relationship; a lone total is not enough.
    if adjustments == 0:
        return None

    score = max(0.0, min(100.0, round(score, 1)))
    return score, _risk_from_score(score)


def _score_from_ai_analysis(ai_analysis: dict[str, Any] | None) -> tuple[float, str] | None:
    if not isinstance(ai_analysis, dict):
        return None
    key_metrics = ai_analysis.get('key_metrics') or {}
    if not isinstance(key_metrics, dict) or not key_metrics:
        return None

    warning_count = 0
    risk_count = 0
    profit_count = 0
    revenue_count = 0
    for path, payload in key_metrics.items():
        if not isinstance(payload, dict):
            continue
        metric_type = str(payload.get('type') or '').lower()
        status = str(payload.get('status') or '').lower()
        if status == 'warning' or metric_type == 'risk':
            warning_count += 1
            risk_count += 1
        if metric_type == 'profitability':
            profit_count += 1
        if metric_type == 'revenue':
            revenue_count += 1

    total = max(len(key_metrics), 1)
    score = 60.0
    score += min(15.0, profit_count * 3.0)
    score += min(10.0, revenue_count * 2.0)
    score -= min(35.0, warning_count * 8.0 + risk_count * 4.0)
    # Slightly reward richer datasets so empty stubs don't look identical.
    score += min(8.0, total / 10.0)
    score = max(0.0, min(100.0, round(score, 1)))
    return score, _risk_from_score(score)


def _risk_from_score(score: float) -> str:
    if score >= 75:
        return 'low'
    if score >= 55:
        return 'moderate'
    if score >= 35:
        return 'high'
    return 'critical'


def derive_report_score_and_risk(
    json_data: Any = None,
    ai_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute overall_score (0-100) and risk_level from uploaded data.

    Preference order:
    1. Classic bank ratios (ROA/ROE/NPL/etc.)
    2. Summary totals (assets/income/expenses)
    3. Structural hints from ai_analysis.key_metrics
    """
    numerics: dict[str, float] = {}
    # Prefer values from the uploaded JSON; fill gaps from ai_analysis.key_metrics.
    if isinstance(ai_analysis, dict):
        key_metrics = ai_analysis.get('key_metrics') or {}
        if isinstance(key_metrics, dict):
            for path, payload in key_metrics.items():
                if isinstance(payload, dict):
                    number = _coerce_number(payload.get('value'))
                    if number is not None:
                        numerics[str(path)] = number
    if json_data is not None:
        numerics.update(_walk_numeric_fields(json_data))

    for scorer in (_score_from_bank_ratios, _score_from_summary_totals):
        result = scorer(numerics)
        if result is not None:
            score, risk = result
            return {
                'overall_score': score,
                'risk_level': risk,
                'score_source': scorer.__name__,
            }

    result = _score_from_ai_analysis(ai_analysis)
    if result is not None:
        score, risk = result
        return {
            'overall_score': score,
            'risk_level': risk,
            'score_source': '_score_from_ai_analysis',
        }

    return {
        'overall_score': 50.0,
        'risk_level': 'moderate',
        'score_source': 'default',
    }


def enrich_report_with_score(report: dict[str, Any]) -> dict[str, Any]:
    """Attach overall_score / risk_level when missing, using stored JSON/analysis."""
    report = dict(report or {})
    has_score = report.get('overall_score') is not None
    has_risk = bool(report.get('risk_level'))
    if has_score and has_risk:
        # Keep ai_analysis.risk_level aligned for older UI paths.
        ai_analysis = dict(report.get('ai_analysis') or {})
        ai_analysis['risk_level'] = str(report.get('risk_level')).lower()
        report['ai_analysis'] = ai_analysis
        return report

    original_json = None
    metadata = report.get('metadata') or {}
    if isinstance(metadata, dict):
        original_json = metadata.get('original_json') or metadata.get('normalized_json')

    derived = derive_report_score_and_risk(
        json_data=original_json,
        ai_analysis=report.get('ai_analysis') if isinstance(report.get('ai_analysis'), dict) else None,
    )

    if not has_score:
        report['overall_score'] = derived['overall_score']
    if not has_risk:
        report['risk_level'] = derived['risk_level']

    ai_analysis = dict(report.get('ai_analysis') or {})
    ai_analysis['risk_level'] = str(report.get('risk_level')).lower()
    if 'overall_score' not in ai_analysis:
        ai_analysis['overall_score'] = report.get('overall_score')
    report['ai_analysis'] = ai_analysis
    report.setdefault('score_source', derived.get('score_source'))
    return report
