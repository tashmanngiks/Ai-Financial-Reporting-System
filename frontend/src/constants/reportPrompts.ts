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

export const REPORT_PROMPT_TEMPLATES = [
  {
    id: 'financial-dashboard',
    label: 'Financial Dashboard (Management Report)',
    prompt: FINANCIAL_DASHBOARD_REPORT_PROMPT,
  },
]
