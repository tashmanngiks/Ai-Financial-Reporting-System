type ReportLike = {
  bank_name?: string | null
  metadata?: { title?: string | null } | null
  title?: string | null
}

export const getShortReportLabel = (report: ReportLike | null | undefined) => {
  const bankName = String(report?.bank_name || '').replace(/\s+/g, ' ').trim()
  if (bankName) {
    const words = bankName.split(' ').filter(Boolean)
    if (words.length <= 2 && bankName.length <= 24) return bankName
    return words.slice(0, 2).join(' ')
  }

  const rawLabel = report?.metadata?.title || report?.title || 'Financial Report'
  const label = String(rawLabel).replace(/\s+/g, ' ').trim()
  const maxLength = 22
  if (label.length <= maxLength) return label

  const trimmed = label.slice(0, maxLength).trimEnd()
  return `${trimmed.replace(/[,.:-]+$/, '').trimEnd()}…`
}

export const getFullReportLabel = (report: ReportLike | null | undefined) => {
  const bankName = String(report?.bank_name || '').replace(/\s+/g, ' ').trim()
  if (bankName) return bankName
  return String(report?.metadata?.title || report?.title || 'Financial Report')
}
