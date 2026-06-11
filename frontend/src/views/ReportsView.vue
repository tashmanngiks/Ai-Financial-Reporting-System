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
        <!-- Loading State -->
        <div v-if="analyticsStore.loading.reports" class="text-center py-12">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
            <div class="w-8 h-8 border-2 border-[#08AAC7] border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p class="text-gray-500">Loading reports...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="filteredReports.length === 0" class="text-center py-12">
          <div class="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-6">
            <svg class="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">No reports found</h3>
          <p class="text-gray-600 mb-6">
            {{ analyticsStore.reports.length === 0 ? 'Upload financial data to generate your first report.' : 'Try adjusting your filters.' }}
          </p>
          <router-link v-if="analyticsStore.reports.length === 0" to="/upload" class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-[#08AAC7] to-[#0691A8] text-white rounded-lg hover:from-[#0691A8] hover:to-[#057A8F] transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            Upload Data
          </router-link>
        </div>

        <!-- Reports Grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="report in filteredReports"
            :key="report.id"
            class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-lg border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300 group cursor-pointer"
            @click="viewReport(report.id)"
          >
            <!-- Risk Level Indicator -->
            <div class="h-1 bg-gradient-to-r from-[#08AAC7] to-[#0691A8]"></div>

            <!-- Report Content -->
            <div class="p-6">
              <!-- Report Header -->
              <div class="flex justify-between items-start mb-4">
                <div class="flex-1">
                  <h3 class="font-bold text-gray-900 text-lg mb-1 group-hover:text-[#08AAC7] transition-colors">{{ report.bank_name }}</h3>
                  <p class="text-sm text-gray-500">{{ report.data_period }}</p>
                </div>
                <div class="px-3 py-1 rounded-full text-xs font-medium"
                     :class="report.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                             report.risk_level === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                             report.risk_level === 'high' ? 'bg-orange-100 text-orange-800' :
                             'bg-red-100 text-red-800'">
                  {{ report.risk_level }}
                </div>
              </div>

              <!-- Score Display -->
              <div class="mb-4">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">Overall Score</span>
                  <span class="text-xs text-gray-500">{{ formatDate(report.generated_at) }}</span>
                </div>
                <div class="flex items-center">
                  <div class="flex-1 bg-gray-200 rounded-full h-3 mr-3">
                    <div
                      class="h-3 rounded-full transition-all duration-700 ease-out"
                      :class="report.overall_score >= 85 ? 'bg-gradient-to-r from-green-500 to-emerald-600' :
                              report.overall_score >= 70 ? 'bg-gradient-to-r from-yellow-500 to-orange-600' :
                              report.overall_score >= 50 ? 'bg-gradient-to-r from-orange-500 to-red-600' :
                              'bg-gradient-to-r from-red-600 to-pink-600'"
                      :style="{ width: report.overall_score + '%' }"
                    ></div>
                  </div>
                  <span class="text-lg font-bold" :class="report.overall_score >= 85 ? 'text-green-600' :
                                                      report.overall_score >= 70 ? 'text-yellow-600' :
                                                      report.overall_score >= 50 ? 'text-orange-600' :
                                                      'text-red-600'">{{ report.overall_score }}/100</span>
                </div>
              </div>

              <!-- Key Metrics Preview -->
              <div class="grid grid-cols-2 gap-3 mb-4">
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500 mb-1">ROA</div>
                  <div class="text-sm font-bold text-gray-900">{{ report.roa?.toFixed(2) || 'N/A' }}%</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500 mb-1">ROE</div>
                  <div class="text-sm font-bold text-gray-900">{{ report.roe?.toFixed(2) || 'N/A' }}%</div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex flex-wrap gap-2">
                <button
                  @click.stop="viewReport(report.id)"
                  class="flex-1 min-w-[120px] px-3 py-2 bg-gradient-to-r from-[#08AAC7] to-[#0691A8] text-white rounded-lg hover:from-[#0691A8] hover:to-[#057A8F] transition-all duration-300 font-medium text-sm shadow hover:shadow-lg transform hover:scale-105"
                >
                  View Report
                </button>
                <a
                  :href="`/api/media/${report.id}/print/`"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click.stop
                  class="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all duration-300 font-medium text-sm"
                >
                  PDF
                </a>
                <a
                  :href="`/api/media/${report.id}/editable/`"
                  target="_blank"
                  rel="noopener noreferrer"
                  @click.stop
                  class="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all duration-300 font-medium text-sm"
                >
                  Word
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Reports State -->
    <div v-if="analyticsStore.reports.length === 0" class="card mt-6">
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
import {
  DocumentTextIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const analyticsStore = useAnalyticsStore()

// Reactive state
const filters = ref({
  search: '',
  riskLevel: '',
  minScore: null,
  maxScore: null,
})

// Computed
const filteredReports = computed(() => {
  let reports = analyticsStore.reports

  if (filters.value.search) {
    reports = reports.filter(report =>
      report.bank_name.toLowerCase().includes(filters.value.search.toLowerCase())
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

// Methods
const viewReport = (reportId) => {
  if (!reportId) {
    console.error('Report ID is undefined')
    return
  }
  router.push(`/reports/${reportId}`)
}

const exportReport = async (reportId, format = 'pdf') => {
  if (!reportId) {
    console.error('Report ID is undefined for export')
    return
  }
  try {
    await analyticsStore.exportReport(reportId, format)
  } catch (error) {
    console.error('Export failed:', error)
    alert(error.message || 'Export failed')
  }
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
