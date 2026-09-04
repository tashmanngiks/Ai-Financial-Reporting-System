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
CREDIT_RISK_ANALYSIS_ID = "credit_risk_analysis"
FINANCIAL_STATEMENTS_ANALYSIS_ID = "financial_statements_analysis"
INVESTMENT_PORTFOLIO_ANALYSIS_ID = "investment_portfolio_analysis"
MARKET_MACRO_ANALYSIS_ID = "market_macro_analysis"
VALUATION_ANALYSIS_ID = "valuation_analysis"
ANNUAL_FINANCIAL_ANALYSIS_ID = "annual_financial_analysis"


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


CREDIT_RISK_ANALYSIS_PROMPT = _build_master_prompt(
    title="Credit Risk Master Prompt",
    context=(
        "The uploaded dataset has been selected as Credit Risk. The report must focus on credit exposure, "
        "default risk, probability of default (PD), loss given default (LGD), exposure at default (EAD), "
        "expected loss, credit quality, and counterparty risk using only the supplied data."
    ),
    role=(
        "You are a senior credit risk analyst and portfolio credit specialist. Translate credit-risk "
        "inputs into a decision-ready report for risk, credit, and executive stakeholders."
    ),
    objective=(
        "Assess credit exposure, borrower or counterparty quality, PD/LGD/EAD where available, expected "
        "loss, concentration, collateral, staging or rating migrations, and material credit risks. "
        "Never invent PD, LGD, EAD, ratings, or loss figures that are not supported by the dataset."
    ),
    analysis_focus=[
        "Credit exposure size, composition, and concentration.",
        "Probability of Default (PD) and credit quality indicators where present.",
        "Loss Given Default (LGD), collateral, and recovery assumptions where present.",
        "Exposure at Default (EAD) and undrawn commitment risk where present.",
        "Expected loss, credit migration, staging, or rating movements where present.",
        "Counterparty, sector, and geographic concentration risks supported by the data.",
        "Practical credit-risk mitigation and portfolio actions tied to evidence.",
    ],
    calculations=[
        "Where PD, LGD, and EAD are all available, compute or interpret Expected Loss = PD × LGD × EAD and label it as derived from the dataset.",
        "Summarize exposure distribution and concentration only from supplied fields.",
        "Identify deterioration or improvement in credit quality only when period or rating data supports it.",
        "State clearly when a credit metric cannot be calculated because required inputs are missing.",
    ],
    validation_rules=[
        "If the dataset is not about Credit Risk, stop and return a validation message instead of analyzing it.",
        "Do not fabricate PD, LGD, EAD, ratings, expected loss, or default history.",
        "Missing optional fields (for example collateral or sector splits) should be noted as limitations, not invented.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Summarize overall credit-risk posture, material exposures, key PD/LGD/EAD or quality signals, "
                "major risks, and the highest-priority credit actions supported by the dataset."
            ),
        },
        {
            "key": "credit_risk_analysis",
            "title": "Credit Risk Analysis",
            "instruction": (
                "Analyze credit quality, default risk indicators, rating or staging signals, and the "
                "overall credit-risk profile using only evidence in the dataset."
            ),
        },
        {
            "key": "exposure_analysis",
            "title": "Exposure Analysis",
            "instruction": (
                "Explain the size, composition, and concentration of credit exposures. Highlight "
                "counterparties, sectors, products, or geographies that dominate risk where data exists."
            ),
        },
        {
            "key": "pd_lgd_ead_analysis",
            "title": "PD, LGD and EAD Analysis",
            "instruction": (
                "Interpret available PD, LGD, and EAD inputs. Where all three exist, discuss expected loss. "
                "If any component is missing, state that expected loss cannot be reliably calculated."
            ),
        },
        {
            "key": "risk_assessment",
            "title": "Risk Assessment",
            "instruction": (
                "Assess default, concentration, collateral, migration, and recovery risks supported by the "
                "data. Rank severity and note early-warning indicators that are present."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized credit-risk recommendations for exposure management, monitoring, "
                "collateral, provisioning, or portfolio actions, each tied to dataset evidence."
            ),
        },
    ],
)


FINANCIAL_STATEMENTS_ANALYSIS_PROMPT = _build_master_prompt(
    title="Financial Statements & Ratios Master Prompt",
    context=(
        "The uploaded dataset has been selected as Financial Statements & Ratios. The report must focus on "
        "financial position, profitability, liquidity, leverage, efficiency, and ratio interpretation "
        "using statement and ratio fields present in the file."
    ),
    role=(
        "You are a senior financial statement analyst. Convert statement balances and ratios into a "
        "clear management report that explains what the numbers mean for performance and risk."
    ),
    objective=(
        "Assess assets, liabilities, equity, income, expenses, and the key ratios that describe "
        "liquidity, leverage, profitability, and efficiency. Explain relationships between indicators "
        "and avoid inventing missing statement lines or ratios."
    ),
    analysis_focus=[
        "Financial position across assets, liabilities, and equity.",
        "Profitability and margin performance.",
        "Liquidity and short-term solvency.",
        "Leverage and capital structure signals.",
        "Efficiency and turnover measures where available.",
        "Ratio interpretation with financial implications, not mere listing.",
        "Evidence-based recommendations for statement-driven decisions.",
    ],
    calculations=[
        "Calculate or interpret ratios only when required inputs exist; otherwise state the limitation.",
        "Explain whether each material ratio improved or deteriorated when comparative data exists.",
        "Do not classify ratios as good or bad without considering the available financial context.",
    ],
    validation_rules=[
        "If the dataset is not about financial statements or ratios, stop and return a validation message.",
        "Missing optional lines (for example inventory or interest coverage inputs) are limitations, not failures.",
        "Never invent statement balances, ratios, or trends.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Summarize financial position, profitability, liquidity, leverage, major strengths and "
                "weaknesses, and the priority implications from the statements and ratios dataset."
            ),
        },
        {
            "key": "financial_position_analysis",
            "title": "Financial Position Analysis",
            "instruction": (
                "Evaluate assets, liabilities, equity, and capital structure. Explain implications for "
                "solvency and financial stability using only supplied balances."
            ),
        },
        {
            "key": "profitability_analysis",
            "title": "Profitability Analysis",
            "instruction": (
                "Analyze revenue, expenses, margins, and earnings performance. Identify drivers of "
                "profitability improvement or deterioration where evidence exists."
            ),
        },
        {
            "key": "liquidity_analysis",
            "title": "Liquidity Analysis",
            "instruction": (
                "Assess liquidity ratios, cash position, and short-term obligations. Explain ability to "
                "meet near-term commitments based on available data."
            ),
        },
        {
            "key": "leverage_analysis",
            "title": "Leverage Analysis",
            "instruction": (
                "Interpret debt, leverage, coverage, and capital-structure signals. Discuss financing "
                "risk and flexibility only where the dataset supports the conclusion."
            ),
        },
        {
            "key": "financial_ratios",
            "title": "Financial Ratios",
            "instruction": (
                "Interpret material ratios: what each indicates, whether it improved or deteriorated, "
                "likely causes where evidenced, and implications for profitability, liquidity, leverage, or efficiency."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized recommendations on profitability, liquidity, leverage, and efficiency "
                "that are clearly connected to statement and ratio findings."
            ),
        },
    ],
)


INVESTMENT_PORTFOLIO_ANALYSIS_PROMPT = _build_master_prompt(
    title="Investment Portfolio Master Prompt",
    context=(
        "The uploaded dataset has been selected as Investment Portfolio. The report must focus on "
        "portfolio allocation, performance, return, risk, diversification, and investment decision implications."
    ),
    role=(
        "You are a senior portfolio analyst and investment strategist. Produce a professional portfolio "
        "report for investment and risk decision-makers."
    ),
    objective=(
        "Assess allocation across asset classes or holdings, performance and return metrics, risk and "
        "volatility, diversification or concentration, and portfolio implications using only the uploaded data."
    ),
    analysis_focus=[
        "Portfolio allocation and weighting across holdings or asset classes.",
        "Performance, returns, and contribution analysis where available.",
        "Risk, volatility, drawdown, and risk-adjusted return signals.",
        "Diversification versus concentration.",
        "Benchmark comparison only when benchmark data is present.",
        "Practical portfolio and risk-management recommendations.",
    ],
    calculations=[
        "Interpret return, weight, and risk metrics only from supplied fields.",
        "Where weights and returns exist, discuss contribution without inventing missing holdings.",
        "Label any derived portfolio metrics as calculations from the supplied data.",
    ],
    validation_rules=[
        "If the dataset is not about an investment portfolio, stop and return a validation message.",
        "Do not fabricate prices, returns, benchmarks, or risk statistics.",
        "Missing optional holdings or benchmark series should be noted as limitations.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Summarize portfolio posture, allocation themes, performance and risk highlights, and the "
                "highest-priority portfolio implications from the dataset."
            ),
        },
        {
            "key": "portfolio_allocation_analysis",
            "title": "Portfolio Allocation Analysis",
            "instruction": (
                "Analyze asset-class or holding weights, concentration, and diversification. Explain what "
                "the allocation implies for risk and return."
            ),
        },
        {
            "key": "performance_analysis",
            "title": "Performance Analysis",
            "instruction": (
                "Interpret portfolio and holding performance, returns, and contribution patterns present "
                "in the data. Distinguish short-term moves from sustained trends when history exists."
            ),
        },
        {
            "key": "risk_return_analysis",
            "title": "Risk and Return Analysis",
            "instruction": (
                "Assess volatility, drawdown, risk-adjusted return, and the risk-return tradeoff using "
                "only available metrics."
            ),
        },
        {
            "key": "investment_analysis",
            "title": "Investment Analysis",
            "instruction": (
                "Provide an investment view of the portfolio's attractiveness, opportunity set, and "
                "material risks supported by the dataset."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized allocation, rebalancing, and risk-management recommendations tied "
                "directly to portfolio evidence."
            ),
        },
    ],
)


MARKET_MACRO_ANALYSIS_PROMPT = _build_master_prompt(
    title="Market & Macroeconomic Data Master Prompt",
    context=(
        "The uploaded dataset has been selected as Market & Macroeconomic Data. The report must focus on "
        "economic indicators, market conditions, interest rates, inflation, growth, FX, and related trends."
    ),
    role=(
        "You are a senior macro and markets analyst. Explain how macroeconomic and market indicators "
        "affect the financial outlook using only the supplied dataset."
    ),
    objective=(
        "Assess GDP, inflation, interest rates, unemployment, FX, equity or market indexes, policy "
        "signals, and country or regional risk where present. Connect indicators to financial implications "
        "without inventing series or forecasts unsupported by the data."
    ),
    analysis_focus=[
        "Macroeconomic indicators such as growth, inflation, employment, and policy rates.",
        "Market conditions, indexes, spreads, and volatility where present.",
        "Interest-rate and FX dynamics.",
        "Country or regional risk signals when available.",
        "Trend direction and material turning points.",
        "Evidence-based implications and recommendations.",
    ],
    calculations=[
        "Summarize level and direction of indicators only from supplied series.",
        "Where multiple periods exist, describe percentage changes and label them as derived from the data.",
        "Do not produce unsupported forecasts; discuss outlook only when the dataset provides forward indicators.",
    ],
    validation_rules=[
        "If the dataset is not about market or macroeconomic information, stop and return a validation message.",
        "Never invent economic series, market prices, or policy outcomes.",
        "Missing optional indicators should be noted as limitations.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Summarize the dominant macro and market signals, key risks and opportunities, and the "
                "main implications for financial decision-making from the dataset."
            ),
        },
        {
            "key": "macroeconomic_indicators",
            "title": "Macroeconomic Indicators",
            "instruction": (
                "Analyze growth, inflation, employment, policy rates, and related macro fields. Explain "
                "financial significance of each material movement."
            ),
        },
        {
            "key": "market_trends",
            "title": "Market Trends",
            "instruction": (
                "Interpret market indexes, spreads, volatility, and directional trends present in the data. "
                "Distinguish short-term moves from sustained trends when history exists."
            ),
        },
        {
            "key": "country_risk_analysis",
            "title": "Country Risk Analysis",
            "instruction": (
                "Assess country or regional political, economic, currency, and sovereign risk signals "
                "when the dataset provides them. State clearly if country-risk data is absent."
            ),
        },
        {
            "key": "risk_assessment",
            "title": "Risk Assessment",
            "instruction": (
                "Evaluate macro, market, rate, FX, and policy risks supported by the evidence. Rank "
                "severity and note early-warning indicators."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized recommendations for positioning, hedging, funding, or monitoring "
                "that follow from the macro and market evidence."
            ),
        },
    ],
)


VALUATION_ANALYSIS_PROMPT = _build_master_prompt(
    title="Valuation Master Prompt",
    context=(
        "The uploaded dataset has been selected as Valuation. The report must focus on intrinsic and "
        "relative valuation, including DCF inputs, multiples, enterprise value, and equity value where available."
    ),
    role=(
        "You are a senior valuation analyst. Build a rigorous, evidence-based valuation report for "
        "investment and corporate-finance decision-makers."
    ),
    objective=(
        "Assess DCF building blocks, discount rates, cash-flow forecasts only when supplied, trading or "
        "transaction multiples, enterprise value, equity value, and valuation drivers. Never invent "
        "cash flows, multiples, or terminal values that are not in the dataset."
    ),
    analysis_focus=[
        "Valuation approach and available methods in the dataset.",
        "DCF inputs, cash flows, discount rate, and terminal assumptions where present.",
        "Multiples-based valuation and peer or transaction context where present.",
        "Enterprise value and equity value bridges where present.",
        "Key value drivers and sensitivity signals supported by the data.",
        "Practical valuation conclusions and recommendations.",
    ],
    calculations=[
        "Use only supplied cash flows, rates, and multiples for any derived value; label calculations clearly.",
        "If required DCF or multiples inputs are missing, state that the valuation cannot be completed reliably.",
        "Reconcile enterprise value to equity value only when net debt or equivalent bridge items exist.",
    ],
    validation_rules=[
        "If the dataset is not about valuation, stop and return a validation message.",
        "Do not fabricate forecasts, discount rates, multiples, or concluded values.",
        "Missing optional methods (for example no DCF) should narrow the analysis, not invent a method.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Summarize the valuation methods available, headline enterprise/equity value signals, "
                "key drivers, major uncertainties, and priority implications from the dataset."
            ),
        },
        {
            "key": "valuation_analysis",
            "title": "Valuation Analysis",
            "instruction": (
                "Provide an integrated valuation assessment across the methods and inputs present in the "
                "dataset. Explain what is driving value up or down."
            ),
        },
        {
            "key": "dcf_analysis",
            "title": "DCF Analysis",
            "instruction": (
                "Interpret DCF cash flows, discount rate, terminal value, and resulting intrinsic value "
                "when those fields exist. If DCF inputs are incomplete, state the limitation clearly."
            ),
        },
        {
            "key": "multiples_analysis",
            "title": "Multiples Analysis",
            "instruction": (
                "Analyze trading or transaction multiples and implied value where available. Compare only "
                "to peers or history present in the file."
            ),
        },
        {
            "key": "enterprise_equity_value",
            "title": "Enterprise and Equity Value",
            "instruction": (
                "Explain enterprise value, equity value, and any bridge items such as net debt when "
                "supplied. Clarify how the components relate."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide prioritized valuation, diligence, and decision recommendations tied to the "
                "valuation evidence and gaps in the dataset."
            ),
        },
    ],
)


ANNUAL_FINANCIAL_ANALYSIS_PROMPT = _build_master_prompt(
    title="Annual Financial Master Prompt",
    context=(
        "The uploaded dataset has been selected as Annual Financial. It may contain single-year or "
        "multi-year annual financial information for a company, institution, financial organisation, "
        "investment entity, or other reporting entity. Analyze income statement, balance sheet / statement "
        "of financial position, cash flow statement, financial ratios, and annual performance information "
        "that are present. Support both single-year and multi-year datasets. For multi-year data, perform "
        "meaningful historical and year-over-year analysis."
    ),
    role=(
        "You are a senior financial analyst and annual financial reporting specialist. Produce a "
        "comprehensive, evidence-based annual financial report suitable for management and decision-makers."
    ),
    objective=(
        "Examine all available annual financial data; identify the reporting period or periods; analyze "
        "financial position, income and profitability, cash flows, assets, liabilities, equity, debt and "
        "capital structure, working capital, and financial ratios; identify year-over-year changes where "
        "multiple years exist; identify positive and negative trends, unusual movements, strengths, "
        "weaknesses, material risks, and opportunities; explain relationships between indicators; and "
        "provide evidence-based recommendations. Never invent financial values, ratios, historical results, "
        "assumptions, trends, forecasts, or conclusions that are not supported by the supplied dataset. "
        "If information required for a calculation is unavailable, clearly state that the calculation "
        "cannot reliably be performed."
    ),
    analysis_focus=[
        "Reporting period identification for single-year or multi-year annual data.",
        "Income statement performance: revenue, cost of sales, gross profit, operating income/expenses, EBITDA, EBIT, finance costs, profit before tax, tax, net income, EPS, dividends.",
        "Financial position: assets (current/non-current), cash, receivables, inventory, investments, PPE, intangibles, liabilities, borrowings/debt, equity, retained earnings.",
        "Cash flows: operating, investing, financing, capex, free cash flow, net change in cash.",
        "Financial ratios where inputs exist: liquidity, leverage, coverage, margins, ROA, ROE, turnover, and other supplied ratios.",
        "Multi-year YoY growth and trend analysis for revenue, profit, assets, liabilities, equity, debt, cash flows, margins, ratios, earnings, dividends, and capital structure.",
        "Financial strengths, weaknesses, material risks, opportunities, and practical recommendations tied to findings.",
    ],
    calculations=[
        "Where multiple years exist, calculate Year-over-Year Growth = (Current Year - Previous Year) / Previous Year × 100 and clearly label results as calculations derived from the supplied data.",
        "Compute ratios only when required inputs are present; otherwise state that the ratio cannot reliably be calculated.",
        "Distinguish short-term movements, sustained trends, significant changes, and potential anomalies. Do not claim a long-term trend without sufficient historical periods.",
        "For ratio movements, explain what the ratio indicates, whether it improved or deteriorated, evidenced causes, implications, and links to profitability, liquidity, leverage, or efficiency—without automatically labelling a ratio good or bad out of context.",
    ],
    validation_rules=[
        "If the dataset is not about annual financial information, stop and return a validation message instead of analyzing it.",
        "Missing optional information (for example no cash-flow block, no debt detail, or no pre-computed ratios) must not invent values; note the limitation in the relevant section.",
        "Never invent financial values, ratios, historical results, assumptions, trends, forecasts, or unsupported conclusions.",
        "Only discuss risks for which there is supporting evidence in the dataset.",
    ],
    report_sections=[
        {
            "key": "executive_summary",
            "title": "Executive Summary",
            "instruction": (
                "Summarize the most important findings only: overall financial performance, major positive "
                "and negative developments, significant financial risks, important opportunities, major "
                "year-over-year movements, key management implications, and priority recommendations. "
                "Do not duplicate the entire detailed analysis."
            ),
        },
        {
            "key": "annual_financial_overview",
            "title": "Annual Financial Overview",
            "instruction": (
                "Identify the reporting entity and period(s). Provide a structured overview of the annual "
                "financial package available in the dataset and note any material data gaps."
            ),
        },
        {
            "key": "revenue_income_performance",
            "title": "Revenue and Income Performance",
            "instruction": (
                "Analyze revenue, cost of sales, gross profit, operating income, and related income-statement "
                "lines. Explain performance drivers and YoY changes where multiple years exist."
            ),
        },
        {
            "key": "profitability_analysis",
            "title": "Profitability Analysis",
            "instruction": (
                "Analyze EBITDA, EBIT, finance costs, profit before tax, tax expense, net income, EPS, and "
                "margins. Explain profitability quality and trajectory using only supplied evidence."
            ),
        },
        {
            "key": "financial_position_analysis",
            "title": "Financial Position Analysis",
            "instruction": (
                "Evaluate the statement of financial position holistically—assets, liabilities, and equity—"
                "and explain implications for solvency, stability, and capital intensity."
            ),
        },
        {
            "key": "asset_analysis",
            "title": "Asset Analysis",
            "instruction": (
                "Analyze total, current, and non-current assets, cash, receivables, inventory, investments, "
                "PPE, and intangibles where present. Discuss composition and material changes."
            ),
        },
        {
            "key": "liability_debt_analysis",
            "title": "Liability and Debt Analysis",
            "instruction": (
                "Analyze total, current, and non-current liabilities and borrowings/debt. Discuss leverage, "
                "maturity or refinancing signals only when evidenced, and implications for financial flexibility."
            ),
        },
        {
            "key": "equity_capital_structure_analysis",
            "title": "Equity and Capital Structure Analysis",
            "instruction": (
                "Analyze total equity, retained earnings, and capital structure. Explain how the mix of debt "
                "and equity has changed and what that implies for financing risk and flexibility."
            ),
        },
        {
            "key": "cash_flow_analysis",
            "title": "Cash Flow Analysis",
            "instruction": (
                "Analyze operating, investing, and financing cash flows, capital expenditure, free cash flow, "
                "and net change in cash. Explain cash generation quality and sustainability where data allows."
            ),
        },
        {
            "key": "working_capital_analysis",
            "title": "Working Capital Analysis",
            "instruction": (
                "Assess working capital using current assets and current liabilities, receivables, inventory, "
                "and related turnover measures when available. Identify working-capital pressure or improvement."
            ),
        },
        {
            "key": "financial_ratio_analysis",
            "title": "Financial Ratio Analysis",
            "instruction": (
                "Interpret liquidity, leverage, coverage, profitability, and efficiency ratios that can be "
                "supported by the dataset. For each material ratio explain indication, movement, evidenced "
                "cause, implications, and related risk or strength—without rote good/bad labels."
            ),
        },
        {
            "key": "year_over_year_trend_analysis",
            "title": "Year-over-Year Trend Analysis",
            "instruction": (
                "When multiple years exist (for example 2022→2023→2024→2025), analyze YoY changes in revenue, "
                "profitability, margins, assets, liabilities, equity, debt, cash flows, and ratios. Label "
                "percentage changes as derived calculations. If only one year exists, state that multi-year "
                "trend analysis cannot be performed."
            ),
        },
        {
            "key": "financial_strength_stability",
            "title": "Financial Strength and Stability",
            "instruction": (
                "Synthesize evidence of financial strength and stability across profitability, balance sheet, "
                "cash flow, liquidity, and capital structure. Base conclusions only on supported indicators."
            ),
        },
        {
            "key": "financial_risks_weaknesses",
            "title": "Financial Risks and Weaknesses",
            "instruction": (
                "Assess evidenced risks such as liquidity, leverage, interest burden, refinancing, "
                "profitability deterioration, cash-flow risk, working-capital pressure, concentration, and "
                "capital-structure risk. Discuss only risks with supporting evidence."
            ),
        },
        {
            "key": "key_performance_drivers",
            "title": "Key Performance Drivers",
            "instruction": (
                "Identify the primary drivers of annual performance—revenue, margins, cost, asset utilisation, "
                "funding, or cash conversion—using relationships evidenced in the dataset."
            ),
        },
        {
            "key": "recommendations",
            "title": "Recommendations",
            "instruction": (
                "Provide practical recommendations connected to findings on profitability, cost, working "
                "capital, debt, liquidity, capital structure, cash flow, asset utilisation, efficiency, "
                "investment decisions, and risk management as supported by the analysis."
            ),
        },
        {
            "key": "conclusion",
            "title": "Conclusion",
            "instruction": (
                "Conclude with an overall assessment of annual financial health, the most material risks, "
                "and the highest-priority strategic actions supported by the dataset."
            ),
        },
    ],
)


_ANNUAL_FINANCIAL_SECTIONS = [
    "executive_summary",
    "annual_financial_overview",
    "revenue_income_performance",
    "profitability_analysis",
    "financial_position_analysis",
    "asset_analysis",
    "liability_debt_analysis",
    "equity_capital_structure_analysis",
    "cash_flow_analysis",
    "working_capital_analysis",
    "financial_ratio_analysis",
    "year_over_year_trend_analysis",
    "financial_strength_stability",
    "financial_risks_weaknesses",
    "key_performance_drivers",
    "recommendations",
    "conclusion",
]


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
            "prompt_id": CREDIT_RISK_ANALYSIS_ID,
            "title": "Credit Risk Analysis",
            "content": CREDIT_RISK_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "credit_risk_analysis",
                "exposure_analysis",
                "pd_lgd_ead_analysis",
                "risk_assessment",
                "recommendations",
            ],
        },
        {
            "prompt_id": FINANCIAL_STATEMENTS_ANALYSIS_ID,
            "title": "Financial Statements & Ratios Analysis",
            "content": FINANCIAL_STATEMENTS_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "financial_position_analysis",
                "profitability_analysis",
                "liquidity_analysis",
                "leverage_analysis",
                "financial_ratios",
                "recommendations",
            ],
        },
        {
            "prompt_id": INVESTMENT_PORTFOLIO_ANALYSIS_ID,
            "title": "Investment Portfolio Analysis",
            "content": INVESTMENT_PORTFOLIO_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "portfolio_allocation_analysis",
                "performance_analysis",
                "risk_return_analysis",
                "investment_analysis",
                "recommendations",
            ],
        },
        {
            "prompt_id": MARKET_MACRO_ANALYSIS_ID,
            "title": "Market & Macroeconomic Data Analysis",
            "content": MARKET_MACRO_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "macroeconomic_indicators",
                "market_trends",
                "country_risk_analysis",
                "risk_assessment",
                "recommendations",
            ],
        },
        {
            "prompt_id": VALUATION_ANALYSIS_ID,
            "title": "Valuation Analysis",
            "content": VALUATION_ANALYSIS_PROMPT,
            "recommended_sections": [
                "executive_summary",
                "valuation_analysis",
                "dcf_analysis",
                "multiples_analysis",
                "enterprise_equity_value",
                "recommendations",
            ],
        },
        {
            "prompt_id": ANNUAL_FINANCIAL_ANALYSIS_ID,
            "title": "Annual Financial Analysis",
            "content": ANNUAL_FINANCIAL_ANALYSIS_PROMPT,
            "recommended_sections": list(_ANNUAL_FINANCIAL_SECTIONS),
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
