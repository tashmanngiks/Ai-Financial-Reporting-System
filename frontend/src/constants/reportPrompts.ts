export const FINANCIAL_DASHBOARD_REPORT_PROMPT = `Analyze the provided JSON financial dashboard data and generate a professional Financial Report. Include:

* Executive Summary
* Financial Position Analysis (Assets and Loans)
* Risk & Duration Analysis
* Efficiency & Cost Analysis
* Liquidity Assessment
* Key Findings
* Strategic Recommendations
* Conclusion

Interpret all financial metrics, ratios, and durations, explaining their implications for profitability, risk, liquidity, and operational efficiency. Present the report in a clear management-style format with concise commentary, key insights, and recommendations based on industry best practices.`

export const CAPITAL_ADEQUACY_CRIPE_PROMPT = `# CRIPE Prompt: Capital Adequacy

## Context
You are operating in a scenario where a commercial bank is preparing for its quarterly Asset-Liability Committee (ALCO) meeting and an upcoming regulatory review. The primary objective is to present a definitive, data-driven report to senior management (CFO, Chief Credit Officer, Market Risk Officer, Director of Liquidity Management) and regulators. This report must analyze the bank\'s current capital position, benchmark it rigorously, and propose actionable strategies to decisively improve the Capital Adequacy ("C") component of the bank\'s CAMELS rating. The analysis must be grounded in the provided financial dataset, which follows a standardized structure (\`JSON data in the report \`).

## Role
You are the Chief Officer of Balance Sheet Management with 20 years of experience. You are the bank\'s foremost authority on capital adequacy, interest rate risk, and balance sheet optimization. Your analysis must reflect deep expertise, a command of complex financial data, and a strategic, senior-management-level perspective. The tone should be authoritative, conclusive, and geared towards actionable decision-making.

## Instruction
Synthesize the provided financial dataset to produce a comprehensive capital adequacy report. Your analysis must be guided by the following rigorous, multi-step reasoning framework. **Treat the provided data as the single source of truth.** The following steps are a universal analytical guide:

**1. Performance and Income Effects Analysis:**
-   Calculate and evaluate the link between capital absorption and income resilience.
-   Quantify income vulnerability under stress using the provided \`NIs\` and/or \`NI24s\` objects. For example: \`Earnings at Risk (EaR) = NI_Base - NI_StressScenario\`.
-   Assess whether current earnings (\`ROA\`, \`ROE\`) support or weaken the capital base under stress. Determine if the bank\'s earnings are sufficient to replenish capital organically.

**2. Valuation & Sensitivity Effects (EVE vs. Tier 1 Analysis):**
-   Perform a detailed comparison between the \`EVE/Assets ratio\` (or \`EVERatio\`) and the \`Tier 1 Capital Ratio\`.
-   **Interpret the Divergence using Universal Logic:**
    -   If \`Equity Ratio > Tier 1 Ratio\`: This indicates that the economic value of assets is at a *premium* and/or liabilities (especially non-maturity deposits) are at a *discount*, which positively contributes to liquidity.
    -   If \`Equity Ratio < Tier 1 Ratio\`: This suggests a *discount* on assets or a *premium* on liabilities, potentially adding a liquidity drain.
-   Analyze the \`EVEChange\` object to assess sensitivity to interest rate changes (IRRBB). Correlate this with the \`OptionSpread\` to evaluate embedded optionality risk.

**3. Structural Drivers & Risk Concentration:**
-   Analyze the balance sheet mismatch using \`GapRatio\` and \`Duration\` gap.
-   Evaluate the funding mix stability using the \`Loan-to-Deposit ratio\`. A high ratio indicates reliance on volatile funding.
-   Assess credit risk overlays using the \`CECL\` reserve and loss distribution metrics (e.g., \`P95Loss\`).
-   Evaluate liquidity profile using the \`ShortTermToAssetRatio\` and its implication for capital stability.

**4. Capital Strength & Benchmarking (Apply Universal Decision Logic):**
-   **Peer Benchmarking:** Compare the bank\'s \`Tier 1 Ratio\` against the provided peer groups (e.g., \`THC_Peer\`, \`FFIEC_CU_Peer\`).
-   **Apply Universal Decision Logic:**
    -   If \`Bank\'s Tier 1 Ratio < THC_Peer and < FFIEC_CU_Peer\`: Conclude a capital deficiency; the bank must increase capital.
    -   If \`Bank\'s Tier 1 Ratio > THC_Peer and < FFIEC_CU_Peer\`: Conclude the position is acceptable but requires monitoring.
    -   If \`Bank\'s Tier 1 Ratio > THC_Peer and > FFIEC_CU_Peer\`: Conclude the bank has a strong relative capital position and may consider **strategically leveraging the balance sheet** for growth.
-   **Trend Analysis:** Use the \`QCDashboard\` array to analyze the historical trend of \`EVERatio\` and other key metrics to identify stability or volatility.
-   **Advanced Capital Adjustment (Conceptual):** The framework for a risk-adjusted Tier 1 capital is: \`Adjusted Tier 1 = Reported Tier 1 + [ -CECL + min(0, EVE_$change_+200bp, EVE_$change_-200bp) + CFP_LCAP * (Max(2-LCAP, 0) - 1) * (Net_Surplus/Deficit) ]\`. Use the available data points to apply this logic to the extent possible.

## Performance
The final output must be a comprehensive, board-ready report that adheres strictly to the following specifications, regardless of the specific data values:

## Output Format & Content

Title: **Capital Adequacy**

### 1. SUMMARY TABLE
Generate the markdown table exactly as specified with these strict rules:

| **Attributes** | **Bank** | **Risk Class** |
| --- | ---: | ---: |
| Equity Ratio (%) | [Value]% | [Value]% |
| Tier 1 Ratio (%) | [Value]% | [Value]% |
| Option Spread (%) | [Value]% | [Value]% |
| Short-Term to Asset Ratio (%) | [Value]% | [Value]% |
| Loan-to-Deposit Ratio (%) | [Value]% | [Value]% |
| UP400bp EVE Change (%) | [Value]% | [Value]% |

**Data Source Rules:**
- Bank column: \`IncomeRisk.Bank.<Field>\`
- Risk Class column: \`IncomeRisk.THC_Peer.<Field>\`
- The model must preserve the original sign of every numeric value.
- If the source value is negative, the output MUST also be negative after multiplying by 100.
- The output must equal: (raw_value   100), formatted to three decimals, including the negative sign when present.
- Use \`N/A\` for missing/null values
- DO NOT convert negative values to positive.
- DO NOT apply absolute values.
- DO NOT use \`IncomeRisk["FFIEC_CU_Peer"]\` data
- DO NOT use \`Dashboard["EVERatio"]\` data for bank , should get the value from IncomeRisk.Bank.EquityRatio
- The map relationship between the values   and the JSON data is as follows:
\tEquity Ratio (EquityRatio) -> IncomeRisk.Bank.EquityRatio, IncomeRisk.THC_Peer.EquityRatio
\tTier 1 Ratio -> IncomeRisk.Bank.Tier1Ratio, IncomeRisk.THC_Peer.Tier1Ratio
\tOption Spread -> IncomeRisk.Bank.OptionSpread, IncomeRisk.THC_Peer.OptionSpread
\tShort-Term to Asset Ratio -> IncomeRisk.Bank.ShortTermToAssetRatio, IncomeRisk.THC_Peer.ShortTermToAssetRatio
\tLoan-to-Deposit Ratio -> IncomeRisk.Bank.LoanToDeposit, IncomeRisk.THC_Peer.LoanToDeposit
\tUP400bp EVE Change -> IncomeRisk.Bank.UP400bpEVEChange, IncomeRisk.THC_Peer.UP400bpEVEChange

### 2. **Report Sections (Do not use bullet points in these sections):**
1.  **EVE vs Tier 1 Capital Analysis:** Detail the divergence and its implications for liquidity and valuation, and assess interest rate risk exposure.
2.  **Peer and Five-Year Benchmarking:** Present the benchmarking results and historical trend analysis.
3.  **Structural Drivers and Risk Factors:** Analyze the key balance sheet mismatches and risk concentrations.
4.  **Leverage Assessment:** Conclude on the bank\'s capacity for strategic leverage based on the benchmarking logic.
5.  **Strategic ALCO Recommendations:** Provide clear, executive-level actions.

### 3. **Conclusion:** State definitively whether the bank\'s key capital metrics differ by more than 30% from the primary Risk-Class median.

### 4. **Strategic Recommendations:** Provide 3-5 clear, prioritized, and actionable ALCO-level recommendations. These must address:
    -   **Capital Optimization:** Actions regarding capital deployment or preservation.
    -   **Duration Rebalancing:** Actions to manage interest rate risk.
    -   **Liquidity Posture:** Actions to improve funding stability.
    -   **Value Preservation:** Actions to hedge risks and protect economic value.

**Formatting Rules:**
-   All ratios must be multiplied by 100 and shown with three decimal places.
-   Duration is to be displayed in years, not as a percentage, with three decimal places.
-   All other data points must use three decimal places.
-   **Absolutely no bullet points** are to be used in the five main sections. Use full, prose sentences and structured paragraphs.
-   The recommended final Tier 1 Ratio must be explicitly stated and must not be less than 8% or less than 80% of the primary peer group median.

## Example
*(This section illustrates how to apply the universal framework to specific data.)*

**For a bank with data similar to \`report_data_capital.json\`:**
"The bank\'s Tier 1 Ratio of 47.49% is substantially higher than the Stratified peer median of 15.32%. According to our decision logic, this indicates a strong relative capital position, creating capacity for strategic leverage. However, this strength is juxtaposed with a significant EVE sensitivity of -27.27% under a +400 bp shock, revealing a critical exposure to rising rates. This conflict between capital strength (C) and interest rate risk sensitivity (S) is the central challenge that our bespoke optimization strategy must address."

`

export const REPORT_PROMPT_TEMPLATES = [
  {
    id: 'financial-dashboard',
    label: 'Financial Dashboard (Management Report)',
    prompt: FINANCIAL_DASHBOARD_REPORT_PROMPT,
    sections: [
      'executive_summary',
      'financial_ratios',
      'risk_assessment',
      'recommendations',
    ],
  },
  {
    id: 'capital-adequacy-cripe',
    label: 'Capital Adequacy (CRIPE)',
    prompt: CAPITAL_ADEQUACY_CRIPE_PROMPT,
    sections: [
      'executive_summary',
      'financial_ratios',
      'wacc_analysis',
      'risk_assessment',
      'benchmark_comparison',
      'recommendations',
    ],
  },
]
