<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-10">
      <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
        <div class="px-8 py-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-white">Financial Reports</h1>
                <p class="text-[#E6F7FB] text-lg mt-1">View and manage your financial analysis reports</p>
              </div>
            </div>
            <div class="flex items-center space-x-3">
              <div class="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
                <span class="text-white text-sm font-medium">{{ filteredReports.length }} Reports</span>
              </div>
              <router-link
                to="/upload"
                class="bg-white text-[#08AAC7] rounded-lg px-6 py-3 font-medium hover:bg-[#E6F7FB] transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <div class="flex items-center space-x-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  <span>New Analysis</span>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- World-Class KPIs -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Total Institutions Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-[#08AAC7] to-[#0691A8]"></div>
        <div class="p-6 flex-1 flex flex-col">
          <!-- Card Title -->
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-600">Total Institutions</p>
          </div>

          <!-- KPI Value Row -->
          <div class="mb-3">
            <p class="text-3xl font-bold text-gray-900 leading-none">{{ analyticsStore.reports.length }}</p>
          </div>

          <!-- Icon in Right Upper Corner -->
          <div class="absolute top-6 right-6">
            <div class="bg-gradient-to-r from-[#08AAC7]/10 to-[#0691A8]/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-[#08AAC7]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">Financial institutions analyzed</div>
        </div>
      </div>

      <!-- Average Performance Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-green-500 to-emerald-600"></div>
        <div class="p-6 flex-1 flex flex-col">
          <!-- Card Title -->
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-600">Average Performance</p>
          </div>

          <!-- KPI Value Row -->
          <div class="mb-3">
            <p class="text-3xl font-bold text-gray-900 leading-none">{{ analyticsStore.reports.length > 0 ? (analyticsStore.reports.reduce((sum, report) => sum + report.overall_score, 0) / analyticsStore.reports.length).toFixed(1) : '0.0' }}</p>
          </div>

          <!-- Icon in Right Upper Corner -->
          <div class="absolute top-6 right-6">
            <div class="bg-gradient-to-r from-green-500/10 to-emerald-600/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">Overall performance average</div>
        </div>
      </div>

      <!-- High Risk Institutions Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-red-500 to-orange-600"></div>
        <div class="p-6 flex-1 flex flex-col">
          <!-- Card Title -->
          <div class="mb-3">
            <p class="text-sm font-medium text-gray-600">High Risk Institutions</p>
          </div>

          <!-- KPI Value Row -->
          <div class="mb-3">
            <p class="text-3xl font-bold text-gray-900 leading-none">{{ analyticsStore.reports.filter(report => report.risk_level === 'high' || report.risk_level === 'critical').length }}</p>
          </div>

          <!-- Icon in Right Upper Corner -->
          <div class="absolute top-6 right-6">
            <div class="bg-gradient-to-r from-red-500/10 to-orange-600/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">Institutions requiring attention</div>
        </div>
      </div>

      <!-- Total Reports Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group flex flex-col h-full">
        <div class="h-1 bg-gradient-to-r from-purple-500 to-indigo-600"></div>
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
            <div class="bg-gradient-to-r from-purple-500/10 to-indigo-600/10 rounded-lg p-2 group-hover:scale-110 transition-transform duration-300">
              <svg class="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
          </div>

          <!-- Card Description -->
          <div class="text-xs text-gray-500">Generated reports</div>
        </div>
      </div>
    </div>

    <!-- Advanced Filters -->
    <div class="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 mb-8">
      <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <div class="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg p-2">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6.586a1 1 0 00-.293-.707L3.293 3.707A1 1 0 013 3V4z"></path>
            </svg>
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900">Advanced Filters</h3>
            <p class="text-gray-600 text-sm">Refine your report search</p>
          </div>
        </div>
      </div>

      <div class="p-6">
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <!-- Search Input -->
          <div class="space-y-2">
            <label for="search" class="text-sm font-medium text-gray-700 flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <span>Search</span>
            </label>
            <div class="relative">
              <input
                id="search"
                v-model="filters.search"
                type="text"
                placeholder="Search by bank name..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#08AAC7] focus:border-[#08AAC7] transition-colors pl-10"
              />
              <div class="absolute left-3 top-3.5">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Risk Level -->
          <div class="space-y-2">
            <label for="risk-level" class="text-sm font-medium text-gray-700 flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
              <span>Risk Level</span>
            </label>
            <select
              id="risk-level"
              v-model="filters.riskLevel"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#08AAC7] focus:border-[#08AAC7] transition-colors"
            >
              <option value="">All Levels</option>
              <option value="low">Low</option>
              <option value="moderate">Moderate</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <!-- Min Score -->
          <div class="space-y-2">
            <label for="min-score" class="text-sm font-medium text-gray-700 flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
              <span>Min Score</span>
            </label>
            <input
              id="min-score"
              v-model.number="filters.minScore"
              type="number"
              min="0"
              placeholder="0"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#08AAC7] focus:border-[#08AAC7] transition-colors"
            />
          </div>

          <!-- Max Score -->
          <div class="space-y-2">
            <label for="max-score" class="text-sm font-medium text-gray-700 flex items-center space-x-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
              </svg>
              <span>Max Score</span>
            </label>
            <input
              id="max-score"
              v-model.number="filters.maxScore"
              type="number"
              min="0"
              placeholder="100"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#08AAC7] focus:border-[#08AAC7] transition-colors"
            />
          </div>
        </div>

        <div class="mt-6 flex justify-between items-center">
          <div class="flex items-center space-x-2 text-sm text-gray-500">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>{{ filteredReports.length }} reports found</span>
          </div>
          <div class="flex space-x-3">
            <button
              @click="clearFilters"
              class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Clear
            </button>
            <button
              @click="applyFilters"
              class="px-6 py-3 bg-gradient-to-r from-[#08AAC7] to-[#0691A8] text-white rounded-lg hover:from-[#0691A8] hover:to-[#057A8F] transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6.586a1 1 0 00-.293-.707L3.293 3.707A1 1 0 013 3V4z"></path>
                </svg>
                <span>Apply Filters</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- World-Class Reports List -->
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
              <h3 class="text-lg font-bold text-gray-900">Financial Reports</h3>
              <p class="text-gray-600 text-sm">{{ filteredReports.length }} reports available</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <div class="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
              <span class="text-gray-700 text-sm font-medium">{{ filteredReports.length }} Results</span>
            </div>
            <button
              @click="exportAllReports"
              class="px-4 py-2 bg-gradient-to-r from-[#08AAC7] to-[#0691A8] text-white rounded-lg hover:from-[#0691A8] hover:to-[#057A8F] transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4 4m4-4V4"></path>
              </svg>
              Export All (PDF)
            </button>
          </div>
        </div>
      </div>

      <div class="p-6">
        <DataTable
          :columns="reportListColumns"
          :rows="reportTableRows"
          row-key="id"
          :loading="analyticsStore.loading.reports"
          loading-message="Loading reports..."
          :empty-title="analyticsStore.reports.length === 0 ? 'No reports found.' : 'No reports match your search criteria.'"
          :empty-message="analyticsStore.reports.length === 0 ? 'Upload financial data to generate your first report.' : 'Try adjusting your filters.'"
          :page-size="10"
          caption="Financial reports table"
          @row-click="(row) => viewReport(row.id)"
        >
          <template #empty>
            <router-link
              v-if="analyticsStore.reports.length === 0"
              to="/upload"
              class="inline-flex items-center px-4 py-2 bg-[#08AAC7] text-white rounded-lg text-sm font-medium hover:bg-[#0691A8]"
            >
              Upload Data
            </router-link>
          </template>

          <template #cell-report_name="{ row }">
            <div class="min-w-[14rem] max-w-[22rem]">
              <div class="font-semibold text-slate-900 line-clamp-2">{{ row.report_name }}</div>
              <div class="text-xs text-slate-500 mt-0.5">{{ row.period || '—' }}</div>
            </div>
          </template>

          <template #cell-report_type="{ value }">
            <span>{{ value || 'Analysis' }}</span>
          </template>

          <template #cell-created_date="{ value }">
            <span class="tabular-nums">{{ formatDateTime(value) }}</span>
          </template>

          <template #cell-status="{ row }">
            <StatusBadge :status="row.status" />
          </template>

          <template #cell-risk_level="{ row }">
            <StatusBadge :status="row.risk_level" :label="row.risk_label" />
          </template>

          <template #cell-overall_score="{ value }">
            <span class="tabular-nums font-semibold">{{ value ?? '—' }}</span>
          </template>

          <template #cell-actions="{ row }">
            <div class="flex flex-wrap items-center gap-1.5 min-w-[14rem]" @click.stop>
              <button
                type="button"
                class="inline-flex items-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                @click="viewReport(row.id)"
              >
                View
              </button>
              <a
                :href="getReportDownloadUrl(row.id, 'pdf')"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                Export PDF
              </a>
              <a
                :href="getReportDownloadUrl(row.id, 'word')"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
              >
                Export Word
              </a>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <!-- No Reports State -->
    <div v-if="!analyticsStore.loading.reports && analyticsStore.reports.length === 0" class="card mt-6">
      <div class="card-body text-center">
        <DocumentTextIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Reports Yet</h3>
        <p class="text-gray-500 mb-4">Upload JSON and write a prompt to generate your first AI report.</p>
        <router-link to="/upload" class="btn" style="background-color: var(--primary-color); color: white;">
          Upload Data
        </router-link>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { getShortReportLabel } from '@/utils/reportDisplay'
import { getReportDownloadUrl } from '@/services/api'
import { formatDateTime, DATASET_TYPE_LABELS } from '@/utils/tableFormat'
import DataTable from '@/components/DataTable.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import {
  DocumentTextIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const analyticsStore = useAnalyticsStore()

const filters = ref({
  search: '',
  riskLevel: '',
  minScore: null,
  maxScore: null,
})

const reportListColumns = [
  { key: 'report_name', label: 'Report Name', wrap: true, width: '16rem' },
  { key: 'report_type', label: 'Report Type', width: '11rem' },
  { key: 'created_date', label: 'Created Date', width: '10rem' },
  { key: 'status', label: 'Status', width: '8rem' },
  { key: 'risk_level', label: 'Risk Level', width: '8rem' },
  { key: 'overall_score', label: 'Overall Score', align: 'right', numeric: true, width: '7rem' },
  { key: 'actions', label: 'Actions', width: '15rem' },
]

const filteredReports = computed(() => {
  let reports = analyticsStore.reports

  if (filters.value.search) {
    reports = reports.filter(report =>
      String(report.bank_name || '').toLowerCase().includes(filters.value.search.toLowerCase())
      || String(report.metadata?.title || '').toLowerCase().includes(filters.value.search.toLowerCase()),
    )
  }

  if (filters.value.riskLevel) {
    reports = reports.filter(report => report.risk_level === filters.value.riskLevel)
  }

  if (filters.value.minScore !== null) {
    reports = reports.filter(report => report.overall_score >= filters.value.minScore)
  }

  if (filters.value.maxScore !== null) {
    reports = reports.filter(report => report.overall_score <= filters.value.maxScore)
  }

  return reports
})

const reportTableRows = computed(() =>
  filteredReports.value.map((report) => {
    const datasetKey = String(report.dataset_type || report.metadata?.dataset_type || '').toLowerCase()
    const risk = report.risk_level || report.ai_analysis?.risk_level || 'moderate'
    return {
      id: report.id,
      report_name: getShortReportLabel(report),
      period: report.data_period || '',
      report_type: DATASET_TYPE_LABELS[datasetKey] || report.report_type || 'Analysis',
      created_date: report.generated_at || report.created_at || report.metadata?.generated_at,
      status: report.status || 'completed',
      risk_level: risk,
      risk_label: String(risk).replace(/^\w/, (c) => c.toUpperCase()),
      overall_score: report.overall_score ?? '—',
    }
  }),
)

const viewReport = (reportId) => {
  if (!reportId) {
    console.error('Report ID is undefined')
    return
  }
  router.push(`/reports/${reportId}`)
}

const exportAllReports = async () => {
  const reports = filteredReports.value
  if (!reports.length) {
    alert('No reports to export')
    return
  }

  try {
    for (const report of reports) {
      await analyticsStore.exportReport(report.id, 'pdf')
    }
  } catch (error) {
    console.error('Export all failed:', error)
    alert(error.message || 'Export failed')
  }
}

const applyFilters = () => {
  // Filters are reactive, no additional action needed
}

const resetFilters = () => {
  filters.value = {
    search: '',
    riskLevel: '',
    minScore: null,
    maxScore: null,
  }
}

const getStatusBadgeClass = (riskLevel) => {
  const classes = {
    low: 'status-success',
    moderate: 'status-warning',
    high: 'status-danger',
    critical: 'status-danger',
  }
  return classes[riskLevel] || 'status-info'
}

const getScoreColor = (score) => {
  if (score >= 70) return 'bg-success-500'
  if (score >= 50) return 'bg-warning-500'
  return 'bg-danger-500'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

// Lifecycle
onMounted(() => {
  analyticsStore.fetchReports()
})
</script>
