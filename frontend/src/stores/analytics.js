import { defineStore } from 'pinia'
import { api, ApiError, handleApiError } from '@/services/api'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    // Upload state
    currentUpload: null,
    uploadProgress: 0,
    uploadStatus: 'idle', // idle, uploading, processing, completed, failed

    // Task state
    currentTask: null,
    taskStatus: null,
    taskProgress: 0,

    // Reports state
    reports: [],
    currentReport: null,
    reportDetail: null,
    reportPromptConfig: null,

    // Loading states
    loading: {
      upload: false,
      reports: false,
      report: false,
      insights: false,
    },

    // Error state
    errors: {
      upload: null,
      reports: null,
      report: null,
      insights: null,
    },

    // Insights state
    insights: [],
    insightsLoading: false,
  }),

  getters: {
    isUploading: (state) => state.loading.upload,
    isProcessing: (state) => state.taskStatus === 'processing',
    hasCurrentReport: (state) => !!state.currentReport,
    recentReports: (state) => Array.isArray(state.reports) ? state.reports.slice(0, 5) : [],
    completedReports: (state) => Array.isArray(state.reports) ? state.reports.filter(report => report.risk_level) : [],

    // Getters for current report data
    reportMetrics: (state) => state.reportDetail?.key_metrics || {},
    reportExecutiveSummary: (state) => state.reportDetail?.executive_summary || {},
    reportTrends: (state) => state.reportDetail?.trend_analysis || {},
    reportBenchmark: (state) => state.reportDetail?.benchmark_comparison || {},
    reportRecommendations: (state) => state.reportDetail?.recommendations || {},
  },

  actions: {
    // Upload actions
    async uploadFile(file, prompt, description = '', reportOptions = {}) {
      if (!prompt?.trim()) {
        throw new Error('Analysis prompt is required')
      }

      this.loading.upload = true
      this.errors.upload = null
      this.uploadStatus = 'processing'
      this.taskProgress = 10

      try {
        const response = await api.uploadFile(file, prompt.trim(), description, reportOptions)
        const data = response.data

        this.currentUpload = data
        this.taskProgress = 100
        this.currentReport = data.id || data.report_id
        this.reportDetail = data

        if (data.ai_enhanced && data.comprehensive_analysis?.length) {
          this.uploadStatus = 'completed'
          this.errors.upload = null
        } else if (data.warning) {
          this.uploadStatus = 'completed'
          this.errors.upload = data.warning
        } else {
          this.uploadStatus = 'completed'
        }

        await this.fetchReports()
        return data
      } catch (error) {
        const msg = error.response?.data?.error || error.message
        this.errors.upload = msg
        this.uploadStatus = 'failed'
        this.currentReport = null
        throw handleApiError(error)
      } finally {
        this.loading.upload = false
      }
    },

    // Task monitoring
    async pollTaskStatus(taskId) {
      const maxAttempts = parseInt(import.meta.env.VITE_POLLING_MAX_ATTEMPTS) || 60
      const pollingInterval = parseInt(import.meta.env.VITE_POLLING_INTERVAL) || 5000
      let attempts = 0

      const poll = async () => {
        try {
          const response = await api.getTaskStatus(taskId)
          this.taskStatus = response.data.status
          this.taskProgress = response.data.progress

          if (response.data.status === 'completed') {
            this.uploadStatus = 'completed'
            this.currentReport = response.data.result_data?.report_id
            await this.fetchReports() // Refresh reports list
            return
          } else if (response.data.status === 'failed') {
            this.uploadStatus = 'failed'
            this.errors.upload = response.data.error_message
            return
          }

          attempts++
          if (attempts < maxAttempts) {
            setTimeout(poll, 5000) // Poll every 5 seconds
          } else {
            this.uploadStatus = 'failed'
            this.errors.upload = 'Analysis timed out'
          }
        } catch (error) {
          this.uploadStatus = 'failed'
          this.errors.upload = error.message
        }
      }

      await poll()
    },

    // Reports actions
    async fetchReports(params = {}) {
      this.loading.reports = true
      this.errors.reports = null

      try {
        const response = await api.getReports(params)
        this.reports = response.data.results || response.data
        return response.data
      } catch (error) {
        this.errors.reports = error.message
        throw handleApiError(error)
      } finally {
        this.loading.reports = false
      }
    },

    async fetchReport(reportId) {
      if (!reportId) {
        throw new Error('Report ID is required')
      }

      this.loading.report = true
      this.errors.report = null

      try {
        const response = await api.getReportDetail(reportId)
        this.reportDetail = response.data
        this.currentReport = response.data
        return response.data
      } catch (error) {
        this.errors.report = error.message
        throw handleApiError(error)
      } finally {
        this.loading.report = false
      }
    },

    async fetchReportMetrics(reportId) {
      try {
        const response = await api.getReportMetrics(reportId)
        return response.data
      } catch (error) {
        console.error('Failed to fetch report metrics:', error)
        throw handleApiError(error)
      }
    },

    async fetchReportTrends(reportId) {
      try {
        const response = await api.getReportTrends(reportId)
        return response.data
      } catch (error) {
        console.error('Failed to fetch report trends:', error)
        throw handleApiError(error)
      }
    },

    async fetchReportBenchmark(reportId) {
      try {
        const response = await api.getReportBenchmark(reportId)
        return response.data
      } catch (error) {
        console.error('Failed to fetch benchmark data:', error)
        throw handleApiError(error)
      }
    },

    // Export actions
    async exportReport(reportId, format = 'pdf') {
      if (!reportId) {
        throw new Error('Report ID is required for export')
      }

      const extensionMap = {
        json: 'json',
        pdf: 'pdf',
        csv: 'csv',
        word: 'docx',
        excel: 'xlsx',
      }

      const response = await api.exportReport(reportId, format)
      let filename = `financial_report_${reportId}.${extensionMap[format] || format}`
      const disposition = response.headers?.['content-disposition'] || ''
      const match = disposition.match(/filename="?([^"]+)"?/)
      if (match?.[1]) {
        filename = match[1]
      }

      return { success: true, filename }
    },

    // Insights actions
    async fetchInsights(reportId, type = null) {
      this.insightsLoading = true
      try {
        const response = await api.getReportInsights(reportId, type)
        this.insights = response.data
        return response.data
      } catch (error) {
        console.error('Failed to fetch insights:', error)
        throw handleApiError(error)
      } finally {
        this.insightsLoading = false
      }
    },

    async regenerateInsights(reportId) {
      return this.regenerateAiReport(reportId)
    },

    async regenerateAiReport(reportId) {
      this.loading.insights = true
      this.errors.report = null
      try {
        const reportOptions =
          this.reportDetail?.metadata?.report_options ||
          this.reportDetail?.report_options ||
          {}
        const response = await api.regenerateInsights(reportId, reportOptions)
        const data = response.data
        if (data.comprehensive_analysis && String(this.reportDetail?.id) === String(reportId)) {
          this.reportDetail = {
            ...this.reportDetail,
            comprehensive_analysis: data.comprehensive_analysis,
            ai_enhanced: true,
            ai_error: null,
          }
        }
        await this.fetchReport(reportId)
        return data
      } catch (error) {
        const message = error.response?.data?.error || error.message
        this.errors.report = message
        throw handleApiError(error)
      } finally {
        this.loading.insights = false
      }
    },

    // Direct analysis
    async analyzeDirectData(financialData) {
      this.loading.upload = true
      this.uploadStatus = 'processing'

      try {
        const response = await api.analyzeDirectData(financialData)
        this.reportDetail = response.data
        this.currentReport = response.data
        this.uploadStatus = 'completed'
        return response.data
      } catch (error) {
        this.errors.upload = error.message
        this.uploadStatus = 'failed'
        throw handleApiError(error)
      } finally {
        this.loading.upload = false
      }
    },

    async fetchReportPromptConfig() {
      try {
        const response = await api.getReportPromptConfig()
        this.reportPromptConfig = response.data?.config || null
        return this.reportPromptConfig
      } catch (error) {
        console.error('Failed to fetch prompt config:', error)
        throw handleApiError(error)
      }
    },

    async updateReportPromptConfig(config) {
      try {
        const response = await api.updateReportPromptConfig(config)
        this.reportPromptConfig = response.data?.config || null
        return this.reportPromptConfig
      } catch (error) {
        console.error('Failed to update prompt config:', error)
        throw handleApiError(error)
      }
    },

    // Utility actions
    clearCurrentUpload() {
      this.currentUpload = null
      this.currentTask = null
      this.taskStatus = null
      this.taskProgress = 0
      this.uploadStatus = 'idle'
      this.errors.upload = null
    },

    clearCurrentReport() {
      this.currentReport = null
      this.reportDetail = null
      this.insights = []
    },

    resetErrors() {
      this.errors = {
        upload: null,
        reports: null,
        report: null,
        insights: null,
      }
    },

    // No mock data - using real API endpoints only
  },
})
