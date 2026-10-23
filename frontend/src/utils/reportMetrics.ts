export type RiskLevel = 'low' | 'moderate' | 'high' | 'critical'

export type ReportMetricsSource = {
  overall_score?: number | string | null
  risk_level?: string | null
  status?: string | null
  ai_analysis?: {
    overall_score?: number | string | null
    risk_level?: string | null
  } | null
  executive_summary?: {
    overall_assessment?: {
      score?: number | string | null
    } | null
  } | null
}

function toNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === '') return null
  const number = Number(value)
  return Number.isFinite(number) ? number : null
}

export function resolveReportScore(report: ReportMetricsSource | null | undefined): number {
  const candidates = [
    report?.overall_score,
    report?.ai_analysis?.overall_score,
    report?.executive_summary?.overall_assessment?.score,
  ]
  for (const candidate of candidates) {
    const number = toNumber(candidate)
    if (number !== null) return number
  }
  return 0
}

export function resolveReportRisk(report: ReportMetricsSource | null | undefined): RiskLevel {
  const raw = String(report?.risk_level || report?.ai_analysis?.risk_level || 'moderate')
    .trim()
    .toLowerCase()
  if (raw === 'low' || raw === 'moderate' || raw === 'high' || raw === 'critical') {
    return raw
  }
  if (raw === 'medium') return 'moderate'
  return 'moderate'
}

export function isHighRiskReport(report: ReportMetricsSource | null | undefined): boolean {
  const risk = resolveReportRisk(report)
  return risk === 'high' || risk === 'critical'
}

export function isProcessingReport(report: ReportMetricsSource | null | undefined): boolean {
  const status = String(report?.status || '').trim().toLowerCase()
  return status === 'processing' || status === 'pending' || status === 'in_progress'
}

export function averageReportScore(reports: ReportMetricsSource[]): number {
  if (!reports.length) return 0
  const total = reports.reduce((sum, report) => sum + resolveReportScore(report), 0)
  return total / reports.length
}
