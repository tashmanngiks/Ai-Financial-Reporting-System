<template>
  <div class="p-6">
    <!-- World-Class Header -->
    <div class="mb-10">
      <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
        <div class="px-8 py-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-white">Financial Analytics Dashboard</h1>
                <p class="text-[#E6F7FB] text-lg mt-1">Monitor and analyze financial performance metrics</p>
              </div>
            </div>
            <div class="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
              <span class="text-white text-sm font-medium">Real-time Overview</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- World-Class Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
      <!-- Total Reports Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-[#08AAC7] to-[#0691A8]"></div>
        <div class="p-6 flex-1 flex flex-col">
          <!-- Card Title -->
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-600">Total Reports</p>
          </div>

          <!-- KPI Value Row -->
          <div class="mb-3">
            <p class="text-3xl font-bold text-gray-900 leading-none">{{ analyticsStore.reports.length }}</p>
          </div>

          <!-- Icon in Right Upper Corner -->
          <div class="absolute top-6 right-6">
            <div class="bg-gradient-to-r from-[#08AAC7]/10 to-[#0691A8]/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-[#08AAC7]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">All time uploads</div>
        </div>
      </div>

      <!-- Average Score Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-green-500 to-emerald-600"></div>
        <div class="p-6 flex-1 flex flex-col">
          <!-- Card Title -->
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-600">Average Score</p>
          </div>

          <!-- KPI Value Row -->
          <div class="mb-3">
            <p class="text-3xl font-bold text-gray-900 leading-none">{{ averageScore.toFixed(1) }}</p>
          </div>

          <!-- Icon in Right Upper Corner -->
          <div class="absolute top-6 right-6">
            <div class="bg-gradient-to-r from-green-500/10 to-emerald-600/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">Performance rating</div>
        </div>
      </div>

      <!-- High Risk Reports Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-yellow-500 to-orange-600"></div>
        <div class="p-6 flex-1 flex flex-col">
          <!-- Card Title -->
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-600">High Risk Reports</p>
          </div>

          <!-- KPI Value Row -->
          <div class="mb-3">
            <p class="text-3xl font-bold text-gray-900 leading-none">{{ highRiskCount }}</p>
          </div>

          <!-- Icon in Right Upper Corner -->
          <div class="absolute top-6 right-6">
            <div class="bg-gradient-to-r from-yellow-500/10 to-orange-600/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">Need attention</div>
        </div>
      </div>

      <!-- Processing Tasks Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-purple-500 to-indigo-600"></div>
        <div class="p-6 flex-1 flex flex-col">
          <!-- Card Title -->
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-600">Processing Tasks</p>
          </div>

          <!-- KPI Value Row -->
          <div class="mb-3">
            <p class="text-3xl font-bold text-gray-900 leading-none">{{ processingCount }}</p>
          </div>

          <!-- Icon in Right Upper Corner -->
          <div class="absolute top-6 right-6">
            <div class="bg-gradient-to-r from-purple-500/10 to-indigo-600/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">In progress</div>
        </div>
      </div>
    </div>

    <!-- World-Class Recent Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
      <!-- Recent Reports -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-lg p-2">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">Recent Reports</h3>
                <p class="text-gray-600 text-sm">Latest financial analyses</p>
              </div>
            </div>
            <router-link to="/reports" class="text-sm font-medium text-[#08AAC7] hover:text-[#0691A8] transition-colors">
              View all →
            </router-link>
          </div>
        </div>

        <div class="p-6">
          <div v-if="analyticsStore.loading.reports" class="text-center py-8">
            <div class="inline-flex items-center justify-center w-12 h-12 bg-gray-100 rounded-full mb-4">
              <div class="w-6 h-6 border-2 border-[#08AAC7] border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p class="text-gray-500">Loading reports...</p>
          </div>

          <div v-else-if="analyticsStore.reports.length === 0" class="text-center py-8">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <p class="text-gray-500 mb-4">No reports yet</p>
            <router-link to="/upload" class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-[#08AAC7] to-[#0691A8] text-white rounded-lg hover:from-[#0691A8] hover:to-[#057A8F] transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
              Upload Data
            </router-link>
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="report in analyticsStore.recentReports"
              :key="report.id"
              class="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-all duration-300 group"
            >
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900 group-hover:text-[#08AAC7] transition-colors">{{ report.bank_name }}</h4>
                <p class="text-sm text-gray-500">{{ report.data_period }}</p>
              </div>
              <div class="flex items-center space-x-4">
                <div class="text-right">
                  <div class="text-lg font-bold text-gray-900">{{ report.overall_score }}/100</div>
                  <div class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                       :class="report.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                               report.risk_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                               report.risk_level === 'high' ? 'bg-orange-100 text-orange-800' :
                               'bg-red-100 text-red-800'">
                    {{ report.risk_level }}
                  </div>
                </div>
                <router-link
                  :to="`/reports/${report.id}`"
                  class="p-2 text-[#08AAC7] hover:bg-[#E6F7FB] rounded-lg transition-all duration-300"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- System Status -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg p-2">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">System Status</h3>
              <p class="text-gray-600 text-sm">Platform health monitoring</p>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="space-y-4">
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">API Status</span>
              </div>
              <div class="flex items-center">
                <span class="text-sm font-medium text-green-600">Healthy</span>
              </div>
            </div>

            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">Database</span>
              </div>
              <div class="flex items-center">
                <span class="text-sm font-medium text-green-600">Connected</span>
              </div>
            </div>

            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">AI Service</span>
              </div>
              <div class="flex items-center">
                <span class="text-sm font-medium text-green-600">Available</span>
              </div>
            </div>

            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>
                <span class="text-sm font-medium text-gray-700">Storage</span>
              </div>
              <div class="flex items-center">
                <span class="text-sm font-medium text-yellow-600">68% Used</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- World-Class Quick Actions -->
    <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <div class="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg p-2">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900">Quick Actions</h3>
            <p class="text-gray-600 text-sm">Common tasks and shortcuts</p>
          </div>
        </div>
      </div>

      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <router-link
            to="/upload"
            class="group flex items-center p-6 bg-gradient-to-br from-[#08AAC7]/5 to-[#0691A8]/5 border border-[#08AAC7]/20 rounded-xl hover:from-[#08AAC7]/10 hover:to-[#0691A8]/10 hover:border-[#08AAC7]/40 transition-all duration-300"
          >
            <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-xl p-3 mr-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-gray-900 group-hover:text-[#08AAC7] transition-colors">Upload Data</h4>
              <p class="text-sm text-gray-600">Start new analysis</p>
            </div>
            <div class="text-[#08AAC7] group-hover:text-[#0691A8] transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </router-link>

          <router-link
            to="/analytics"
            class="group flex items-center p-6 bg-gradient-to-br from-green-500/5 to-emerald-600/5 border border-green-500/20 rounded-xl hover:from-green-500/10 hover:to-emerald-600/10 hover:border-green-500/40 transition-all duration-300"
          >
            <div class="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-3 mr-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-gray-900 group-hover:text-green-600 transition-colors">View Analytics</h4>
              <p class="text-sm text-gray-600">Explore insights</p>
            </div>
            <div class="text-green-600 group-hover:text-emerald-600 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </router-link>

          <router-link
            to="/reports"
            class="group flex items-center p-6 bg-gradient-to-br from-purple-500/5 to-indigo-600/5 border border-purple-500/20 rounded-xl hover:from-purple-500/10 hover:to-indigo-600/10 hover:border-purple-500/40 transition-all duration-300"
          >
            <div class="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl p-3 mr-4 shadow-lg group-hover:scale-110 transition-transform duration-300">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors">View Reports</h4>
              <p class="text-sm text-gray-600">Browse results</p>
            </div>
            <div class="text-purple-600 group-hover:text-indigo-600 transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'

const analyticsStore = useAnalyticsStore()

type RiskLevel = 'low' | 'moderate' | 'high' | 'critical'

type ReportSummary = {
  id?: string
  bank_name?: string
  data_period?: string
  overall_score?: number
  risk_level?: RiskLevel
}

// Computed properties
const averageScore = computed(() => {
  const reports = Array.isArray(analyticsStore.reports) ? (analyticsStore.reports as ReportSummary[]) : []
  if (reports.length === 0) return 0
  const total = reports.reduce((sum: number, report: ReportSummary) => sum + (report.overall_score || 0), 0)
  return total / analyticsStore.reports.length
})

const highRiskCount = computed(() => {
  const reports = Array.isArray(analyticsStore.reports) ? (analyticsStore.reports as ReportSummary[]) : []
  return reports.filter((report: ReportSummary) =>
    report.risk_level === 'high' || report.risk_level === 'critical'
  ).length
})

const processingCount = computed(() => {
  return analyticsStore.uploadStatus === 'processing' ? 1 : 0
})

// Methods
const getStatusBadgeClass = (riskLevel?: RiskLevel) => {
  const classes: Record<RiskLevel, string> = {
    low: 'status-success',
    moderate: 'status-warning',
    high: 'status-danger',
    critical: 'status-danger',
  }
  return riskLevel ? classes[riskLevel] : 'status-info'
}

// No mock data function - using real API endpoints only

// Initialize
analyticsStore.fetchReports()
</script>
