export const DATASET_TYPE_LABELS: Record<string, string> = {
  wacc: 'WACC',
  money_market: 'Money Market',
  financial_instruments: 'Financial Instruments',
  credit_risk: 'Credit Risk',
  financial_statements: 'Financial Statements & Ratios',
  investment_portfolio: 'Investment Portfolio',
  market_macro: 'Market & Macroeconomic Data',
  valuation: 'Valuation',
  annual_financial: 'Annual Financial',
}

export function formatDateTime(value: string | number | Date | null | undefined): string {
  if (!value) return '—'
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export function formatDateOnly(value: string | number | Date | null | undefined): string {
  if (!value) return '—'
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date)
}

export function formatVersion(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') return 'v1'
  const raw = String(value).trim()
  if (/^v/i.test(raw)) return raw
  return `v${raw}`
}
