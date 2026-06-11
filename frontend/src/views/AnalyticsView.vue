<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">Analytics Overview</h1>
      <p class="text-gray-600 mt-2">Comprehensive analytics and insights across all reports</p>
    </div>

    <!-- Analytics Dashboard -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
      <!-- Performance Trends Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <!-- Header with Icon -->
        <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-white">Performance Trends</h3>
                <p class="text-[#E6F7FB] text-sm">Key financial metrics</p>
              </div>
            </div>
            <div class="bg-white/20 backdrop-blur-sm rounded-full px-3 py-1">
              <span class="text-white text-xs font-medium">Live</span>
            </div>
          </div>
        </div>

        <!-- Metrics Content -->
        <div class="p-6 space-y-6">
          <!-- ROA Metric -->
          <div class="group">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <div class="bg-gradient-to-r from-emerald-500 to-green-600 rounded-lg p-2 group-hover:scale-110 transition-transform">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-gray-600 text-sm font-medium">Average ROA</p>
                  <div class="flex items-baseline space-x-2">
                    <span class="text-2xl font-bold text-gray-900">{{ averageMetrics.roa.toFixed(2) }}%</span>
                    <span :class="getTrendIcon(averageMetrics.roa_trend)" class="text-lg font-bold">
                      {{ averageMetrics.roa_trend === 'up' ? '↑' : averageMetrics.roa_trend === 'down' ? '↓' : '→' }}
                    </span>
                  </div>
                </div>
              </div>
              <div :class="averageMetrics.roa_trend === 'up' ? 'bg-green-100 text-green-800' : averageMetrics.roa_trend === 'down' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ averageMetrics.roa_trend === 'up' ? 'Positive' : averageMetrics.roa_trend === 'down' ? 'Negative' : 'Stable' }}
              </div>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div :class="averageMetrics.roa_trend === 'up' ? 'bg-gradient-to-r from-green-500 to-emerald-600' : averageMetrics.roa_trend === 'down' ? 'bg-gradient-to-r from-red-500 to-pink-600' : 'bg-gradient-to-r from-gray-500 to-gray-600'" class="h-full rounded-full transition-all duration-500" :style="{ width: Math.min(Math.abs(averageMetrics.roa) * 10, 100) + '%' }"></div>
            </div>
          </div>

          <!-- ROE Metric -->
          <div class="group">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-lg p-2 group-hover:scale-110 transition-transform">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-gray-600 text-sm font-medium">Average ROE</p>
                  <div class="flex items-baseline space-x-2">
                    <span class="text-2xl font-bold text-gray-900">{{ averageMetrics.roe.toFixed(2) }}%</span>
                    <span :class="getTrendIcon(averageMetrics.roe_trend)" class="text-lg font-bold">
                      {{ averageMetrics.roe_trend === 'up' ? '↑' : averageMetrics.roe_trend === 'down' ? '↓' : '→' }}
                    </span>
                  </div>
                </div>
              </div>
              <div :class="averageMetrics.roe_trend === 'up' ? 'bg-green-100 text-green-800' : averageMetrics.roe_trend === 'down' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ averageMetrics.roe_trend === 'up' ? 'Positive' : averageMetrics.roe_trend === 'down' ? 'Negative' : 'Stable' }}
              </div>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div :class="averageMetrics.roe_trend === 'up' ? 'bg-gradient-to-r from-green-500 to-emerald-600' : averageMetrics.roe_trend === 'down' ? 'bg-gradient-to-r from-red-500 to-pink-600' : 'bg-gradient-to-r from-gray-500 to-gray-600'" class="h-full rounded-full transition-all duration-500" :style="{ width: Math.min(Math.abs(averageMetrics.roe) * 5, 100) + '%' }"></div>
            </div>
          </div>

          <!-- Efficiency Metric -->
          <div class="group">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <div class="bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg p-2 group-hover:scale-110 transition-transform">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-gray-600 text-sm font-medium">Average Efficiency</p>
                  <div class="flex items-baseline space-x-2">
                    <span class="text-2xl font-bold text-gray-900">{{ averageMetrics.efficiency.toFixed(1) }}%</span>
                    <span :class="getTrendIcon(averageMetrics.efficiency_trend)" class="text-lg font-bold">
                      {{ averageMetrics.efficiency_trend === 'up' ? '↑' : averageMetrics.efficiency_trend === 'down' ? '↓' : '→' }}
                    </span>
                  </div>
                </div>
              </div>
              <div :class="averageMetrics.efficiency_trend === 'up' ? 'bg-green-100 text-green-800' : averageMetrics.efficiency_trend === 'down' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ averageMetrics.efficiency_trend === 'up' ? 'Positive' : averageMetrics.efficiency_trend === 'down' ? 'Negative' : 'Stable' }}
              </div>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div :class="averageMetrics.efficiency_trend === 'up' ? 'bg-gradient-to-r from-green-500 to-emerald-600' : averageMetrics.efficiency_trend === 'down' ? 'bg-gradient-to-r from-red-500 to-pink-600' : 'bg-gradient-to-r from-gray-500 to-gray-600'" class="h-full rounded-full transition-all duration-500" :style="{ width: Math.min(averageMetrics.efficiency, 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Risk Distribution Card -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <!-- Header with Icon -->
        <div class="bg-gradient-to-r from-orange-600 to-red-600 px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-white">Risk Distribution</h3>
                <p class="text-orange-100 text-sm">Risk level analysis</p>
              </div>
            </div>
            <div class="bg-white/20 backdrop-blur-sm rounded-full px-3 py-1">
              <span class="text-white text-xs font-medium">Real-time</span>
            </div>
          </div>
        </div>

        <!-- Risk Content -->
        <div class="p-6 space-y-5">
          <div v-for="(count, level) in riskDistribution" :key="level" class="group">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-3">
                <div :class="getRiskIconBackground(level)" class="rounded-lg p-2 group-hover:scale-110 transition-transform">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div>
                  <p class="text-gray-600 text-sm font-medium capitalize">{{ level }}</p>
                  <div class="flex items-baseline space-x-2">
                    <span class="text-2xl font-bold text-gray-900">{{ count }}</span>
                    <span class="text-gray-500 text-sm">reports</span>
                  </div>
                </div>
              </div>
              <div :class="getRiskBadgeClass(level)" class="px-3 py-1 rounded-full text-xs font-medium">
                {{ getRiskLabel(level) }}
              </div>
            </div>
            <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700 ease-out"
                :class="getRiskGradient(level)"
                :style="{ width: getRiskPercentage(count) + '%' }"
              ></div>
            </div>
            <div class="flex justify-between text-xs text-gray-500 mt-1">
              <span>{{ getRiskDescription(level) }}</span>
              <span>{{ getRiskPercentage(count).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
      <!-- Score Distribution Chart -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <!-- Header with Icon -->
        <div class="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-white">Score Distribution</h3>
                <p class="text-purple-100 text-sm">Performance score analytics</p>
              </div>
            </div>
            <div class="bg-white/20 backdrop-blur-sm rounded-full px-3 py-1">
              <span class="text-white text-xs font-medium">Analytics</span>
            </div>
          </div>
        </div>

        <!-- Chart Content -->
        <div class="p-6">
          <div class="mb-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">Average Score</span>
              <span class="text-2xl font-bold" :class="getScoreTextColor(averageScore)">{{ averageScore.toFixed(1) }}</span>
            </div>
            <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700 ease-out"
                :class="getScoreBarColor(averageScore)"
                :style="{ width: averageScore + '%' }"
              ></div>
            </div>
          </div>

          <div class="chart-container bg-white/50 rounded-xl p-4 border border-gray-100">
            <canvas ref="scoreChart"></canvas>
          </div>

          <!-- Score Ranges -->
          <div class="grid grid-cols-2 gap-3 mt-4">
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">Excellent (85-100)</span>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">Good (70-84)</span>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">Fair (50-69)</span>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">Poor (0-49)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Risk Level Analysis Chart -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <!-- Header with Icon -->
        <div class="bg-gradient-to-r from-red-600 to-orange-600 px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="bg-white/20 backdrop-blur-sm rounded-lg p-2">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-xl font-bold text-white">Risk Level Analysis</h3>
                <p class="text-red-100 text-sm">Comprehensive risk assessment</p>
              </div>
            </div>
            <div class="bg-white/20 backdrop-blur-sm rounded-full px-3 py-1">
              <span class="text-white text-xs font-medium">Risk Matrix</span>
            </div>
          </div>
        </div>

        <!-- Chart Content -->
        <div class="p-6">
          <div class="mb-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-600">High Risk Reports</span>
              <span class="text-2xl font-bold text-red-600">{{ highRiskCount }}</span>
            </div>
            <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-700 ease-out bg-gradient-to-r from-red-500 to-pink-600"
                :style="{ width: Math.min((highRiskCount / Math.max(analyticsStore.reports.length, 1)) * 100, 100) + '%' }"
              ></div>
            </div>
          </div>

          <div class="chart-container bg-white/50 rounded-xl p-4 border border-gray-100">
            <canvas ref="riskChart"></canvas>
          </div>

          <!-- Risk Summary -->
          <div class="grid grid-cols-2 gap-3 mt-4">
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">Low Risk</span>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">Moderate Risk</span>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-orange-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">High Risk</span>
              </div>
            </div>
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                <span class="text-sm font-medium text-gray-700">Critical Risk</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Executive Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- Total Institutions Card -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-3 bg-primary-100 rounded-full">
            <svg class="w-6 h-6 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9zM11 4v1a1 1 0 11-2 0V4h2z"/>
            </svg>
          </div>
          <div class="ml-4">
            <div class="text-2xl font-bold text-gray-900">{{ analyticsStore.reports.length }}</div>
            <div class="text-gray-600">Total Institutions</div>
          </div>
        </div>
      </div>

      <!-- Average Performance Card -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-3 bg-success-100 rounded-full">
            <svg class="w-6 h-6 text-success-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M13 7H7l-3 3 3 3h6l3-3-3-3z"/>
            </svg>
          </div>
          <div class="ml-4">
            <div class="text-2xl font-bold text-gray-900">{{ averageScore.toFixed(1) }}</div>
            <div class="text-gray-600">Average Performance Score</div>
          </div>
        </div>
      </div>

      <!-- High Risk Institutions Card -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-3 bg-warning-100 rounded-full">
            <svg class="w-6 h-6 text-warning-600" fill="currentColor" viewBox="0 0 20 20">
              <path d="M12 9v2m0 0h1m-6 0H9m12 0v9m0 0h1m-6 0H9"/>
            </svg>
          </div>
          <div class="ml-4">
            <div class="text-2xl font-bold text-gray-900">{{ highRiskCount }}</div>
            <div class="text-gray-600">High Risk Institutions</div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Insights Panel -->
    <div class="bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
      <div class="flex items-center mb-4">
        <div class="p-2 bg-primary-600 rounded-lg">
          <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4a1 1 0 00-1.414-1.414L10 10.586z"/>
          </svg>
        </div>
        <div class="ml-3">
          <div class="text-lg font-bold text-gray-900">AI-Powered Financial Intelligence</div>
          <div class="text-gray-600">Advanced analytics powered by machine learning</div>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-white bg-opacity-90 rounded-lg p-4">
          <h4 class="font-medium text-gray-900 mb-2">Key Findings</h4>
          <ul class="text-sm text-gray-700 space-y-1">
                      <li class="flex items-center">
                        <svg class="w-4 h-4 text-success-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M13 7H7l-3 3 3 3h6l3-3-3-3z"/>
                        </svg>
                        <span>AI analysis complete for {{ analyticsStore.reports.length }} institutions</span>
                      </li>
                      <li class="flex items-center">
                        <svg class="w-4 h-4 text-warning-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9 12l2 2m0 0h1m-6 0H9m12 0v9m0 0h1m-6 0H9"/>
                        </svg>
                        <span>{{ riskDistribution.high + riskDistribution.critical }} institutions require immediate attention</span>
                      </li>
                      <li class="flex items-center">
                        <svg class="w-4 h-4 text-info-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M13 16a1 1 0 00-1-1H8a1 1 0 00-1 1v3a1 1 0 001 1h4a1 1 0 001-1v-3z"/>
                        </svg>
                        <span>Average risk score: {{ averageScore.toFixed(1) }}/100</span>
                      </li>
                    </ul>
        </div>

        <div class="bg-white bg-opacity-90 rounded-lg p-4">
          <h4 class="font-medium text-gray-900 mb-2">Performance Trends</h4>
          <div class="space-y-2">
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600">Best Performing Institution</span>
              <span class="font-medium text-gray-900">{{ bestPerformingInstitution }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-600">Average ROA</span>
              <span class="font-medium text-gray-900">{{ averageMetrics.roa.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Comparison Table -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="card-header px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">Financial Performance Analysis</h3>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-500">Last updated</span>
            <span class="text-sm font-medium text-gray-700">{{ new Date().toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Institution</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Performance Score</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Key Metrics</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trend</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="report in analyticsStore.reports" :key="report.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="font-medium text-gray-900">{{ report.bank_name }}</div>
                  <div class="text-sm text-gray-500">{{ report.data_period }}</div>
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-3">
                  <div class="flex-1">
                    <div class="flex items-center">
                      <div class="text-sm text-gray-500 mr-2">Score</div>
                      <div class="text-lg font-bold" :class="getScoreTextColor(report.ai_analysis?.key_metrics?.net_income?.value / 1000)">
                        {{ getPerformanceScore(report.ai_analysis?.key_metrics?.net_income?.value / 1000) }}
                      </div>
                    </div>
                    <div class="w-24 bg-gray-200 rounded-full h-2">
                      <div
                        class="h-2 rounded-full transition-all duration-300"
                        :class="getScoreBarColor(report.ai_analysis?.key_metrics?.net_income?.value / 1000)"
                        :style="{ width: getPerformanceScore(report.ai_analysis?.key_metrics?.net_income?.value / 1000) + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span
                    v-if="report.ai_analysis?.risk_level"
                    class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
                    :class="getRiskBadgeClass(report.ai_analysis.risk_level)"
                  >
                    <svg v-if="report.ai_analysis.risk_level === 'low'" class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 12l2 2m0 0h1m-6 0H9m12 0v9m0 0h1m-6 0H9"/>
                    </svg>
                    <svg v-else-if="report.ai_analysis.risk_level === 'moderate'" class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M12 9v2m0 0h1m-6 0H9m12 0v9m0 0h1m-6 0H9"/>
                    </svg>
                    <svg v-else-if="report.ai_analysis.risk_level === 'high'" class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M12 8v4m0 0h1m-6 0H9m12 0v9m0 0h1m-6 0H9"/>
                    </svg>
                    {{ report.ai_analysis.risk_level || 'Unknown' }}
                  </span>
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="space-y-1">
                  <div class="flex justify-between text-xs">
                    <span class="text-gray-500">ROA</span>
                    <span class="font-medium">{{ getMetricDisplay(report.data_summary?.sample_data?.roa) }}</span>
                  </div>
                  <div class="flex justify-between text-xs">
                    <span class="text-gray-500">ROE</span>
                    <span class="font-medium">{{ getMetricDisplay(report.data_summary?.sample_data?.roe) }}</span>
                  </div>
                  <div class="flex justify-between text-xs">
                    <span class="text-gray-500">Efficiency</span>
                    <span class="font-medium">{{ getMetricDisplay(report.data_summary?.sample_data?.efficiency_ratio) }}</span>
                  </div>
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-1">
                  <span v-if="getTrendDirection(report.data_summary?.sample_data?.roe) === 'up'" class="text-success-600 flex items-center text-sm">
                    <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 7H7l-3 3 3 3h6l3-3-3-3z"/>
                    </svg>
                    Improving
                  </span>
                  <span v-else-if="getTrendDirection(report.data_summary?.sample_data?.roe) === 'down'" class="text-danger-600 flex items-center text-sm">
                    <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 17l-5-5m0 0L8 12l-5 5m5-5v6m0 0h6"/>
                    </svg>
                    Declining
                  </span>
                  <span v-else class="text-gray-600 flex items-center text-sm">
                    <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 12l2 2m0 0h1m-6 0H9m12 0v9m0 0h1m-6 0H9"/>
                    </svg>
                    Stable
                  </span>
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center space-x-2">
                  <router-link
                    :to="`/reports/${report.id}`"
                    class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                  >
                    <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4zm1-9a1 1 0 10-2 0v1a1 1 0 002 0V3z"/>
                    </svg>
                    View Details
                  </router-link>
                  <a
                    :href="`/api/media/${report.id}/print/`"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                  >
                    PDF
                  </a>
                  <a
                    :href="`/api/media/${report.id}/editable/`"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                  >
                    Word
                  </a>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

      </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'

const analyticsStore = useAnalyticsStore()

type TrendDirection = 'up' | 'down' | 'stable'
type RiskLevel = 'low' | 'moderate' | 'high' | 'critical'
type PartialRiskLevel = 'low' | 'moderate' | 'high'

type AverageMetrics = {
  roa: number
  roe: number
  efficiency: number
  roa_trend: TrendDirection
  roe_trend: TrendDirection
  efficiency_trend: TrendDirection
}

type ReportRecord = {
  id?: string
  bank_name?: string
  overall_score?: number
  risk_level?: RiskLevel
  ai_analysis?: {
    risk_level?: RiskLevel
  }
  data_summary?: {
    sample_data?: {
      roa?: number | null
      roe?: number | null
      efficiency_ratio?: number | null
    }
  }
}

// Chart refs
const scoreChart = ref<HTMLElement | null>(null)
const riskChart = ref<HTMLElement | null>(null)

// Computed
const averageMetrics = computed<AverageMetrics>(() => {
  const reports = Array.isArray(analyticsStore.reports) ? (analyticsStore.reports as ReportRecord[]) : []
  if (reports.length === 0) {
    return {
      roa: 0,
      roe: 0,
      efficiency: 0,
      roa_trend: 'stable' as TrendDirection,
      roe_trend: 'stable' as TrendDirection,
      efficiency_trend: 'stable' as TrendDirection,
    }
  }

  const validReports = reports.filter(
    (r: ReportRecord) =>
      r.data_summary?.sample_data?.roa !== null &&
      r.data_summary?.sample_data?.roe !== null &&
      r.data_summary?.sample_data?.efficiency_ratio !== null,
  )

  if (validReports.length === 0) {
    return {
      roa: 0,
      roe: 0,
      efficiency: 0,
      roa_trend: 'stable' as TrendDirection,
      roe_trend: 'stable' as TrendDirection,
      efficiency_trend: 'stable' as TrendDirection,
    }
  }

  const roa = validReports.reduce((sum: number, r: ReportRecord) => sum + (r.data_summary?.sample_data?.roa || 0), 0) / validReports.length
  const roe = validReports.reduce((sum: number, r: ReportRecord) => sum + (r.data_summary?.sample_data?.roe || 0), 0) / validReports.length
  const efficiency = validReports.reduce((sum: number, r: ReportRecord) => sum + (r.data_summary?.sample_data?.efficiency_ratio || 0), 0) / validReports.length
  // Simple trend calculation
  const roa_trend = roa > 1.0 ? 'up' : roa < 0.5 ? 'down' : 'stable'
  const roe_trend = roe > 10 ? 'up' : roe < 5 ? 'down' : 'stable'
  const efficiency_trend = efficiency < 60 ? 'up' : efficiency > 75 ? 'down' : 'stable'

  return { roa, roe, efficiency, roa_trend, roe_trend, efficiency_trend }
})

const bestPerformingInstitution = computed(() => {
  const reports = Array.isArray(analyticsStore.reports) ? (analyticsStore.reports as ReportRecord[]) : []
  if (reports.length === 0) {
    return 'No data available'
  }

  const validReports = reports.filter((r: ReportRecord) => r.data_summary?.sample_data?.roa !== null)

  if (validReports.length === 0) {
    return 'No data available'
  }

  const bestReport = validReports.reduce((best: ReportRecord, current: ReportRecord) => {
    const currentROA = current.data_summary?.sample_data?.roa || 0
    const bestROA = best.data_summary?.sample_data?.roa || 0
    return currentROA > bestROA ? current : best
  })

  return bestReport.bank_name || 'Unknown Institution'
})

const riskDistribution = computed(() => {
  const reports = Array.isArray(analyticsStore.reports) ? (analyticsStore.reports as ReportRecord[]) : []
  const distribution: Record<RiskLevel, number> = {
    low: 0,
    moderate: 0,
    high: 0,
    critical: 0,
  }
  reports.forEach((report: ReportRecord) => {
    const riskLevel = report.ai_analysis?.risk_level
    if (riskLevel) {
      distribution[riskLevel]++
    }
  })
  return distribution
})

const averageScore = computed(() => {
  const reports = Array.isArray(analyticsStore.reports) ? (analyticsStore.reports as ReportRecord[]) : []
  if (reports.length === 0) return 0
  return reports.reduce((sum: number, r: ReportRecord) => sum + (r.overall_score || 0), 0) / reports.length
})

const highRiskCount = computed(() => {
  const reports = Array.isArray(analyticsStore.reports) ? (analyticsStore.reports as ReportRecord[]) : []
  return reports.filter((r: ReportRecord) => r.risk_level === 'high' || r.risk_level === 'critical').length
})

// Methods
const getTrendIcon = (trend: TrendDirection) => {
  switch (trend) {
    case 'up':
      return 'text-green-600'
    case 'down':
      return 'text-red-600'
    default:
      return 'text-gray-600'
  }
}

const getStatusBadgeClass = (riskLevel?: RiskLevel) => {
  const classes: Record<RiskLevel, string> = {
    low: 'status-success',
    moderate: 'status-warning',
    high: 'status-danger',
    critical: 'status-danger',
  }
  return riskLevel ? classes[riskLevel] : 'status-info'
}

const getRiskColor = (level?: PartialRiskLevel) => {
  const colors: Record<PartialRiskLevel, string> = {
    low: 'bg-success-500',
    moderate: 'bg-warning-500',
    high: 'bg-danger-500',
  }
  return level ? colors[level] : 'bg-gray-500'
}

const getRiskBadgeClass = (riskLevel?: RiskLevel) => {
  const classes: Record<RiskLevel, string> = {
    low: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800',
    moderate: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800',
    high: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800',
    critical: 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-900',
  }
  return riskLevel ? classes[riskLevel] : 'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800'
}

const getScoreTextColor = (score: number) => {
  if (score >= 85) return 'text-green-600'
  if (score >= 70) return 'text-yellow-600'
  if (score >= 50) return 'text-orange-600'
  return 'text-red-600'
}

const getScoreBarColor = (score: number) => {
  if (score >= 85) return 'bg-green-500'
  if (score >= 70) return 'bg-yellow-500'
  if (score >= 50) return 'bg-orange-500'
  return 'bg-red-500'
}

const getPerformanceScore = (score: number) => {
  return Math.min(100, Math.max(0, score))
}

const getMetricDisplay = (value: number | null | undefined) => {
  if (value === null || value === undefined || value === 0) return 'Data Unavailable'
  if (typeof value === 'number') return `${(value * 100).toFixed(2)}%`
  return 'N/A'
}

const getTrendDirection = (value: number) => {
  // Simple trend calculation - in real app, this would compare with historical data
  if (value > 8) return 'up'
  if (value < 5) return 'down'
  return 'stable'
}

const getRiskPercentage = (count: number) => {
  const total = analyticsStore.reports.length
  return total > 0 ? (count / total) * 100 : 0
}

const getScoreColor = (score: number) => {
  if (score >= 70) return 'bg-success-500'
  if (score >= 50) return 'bg-warning-500'
  return 'bg-danger-500'
}

// New world-class helper methods
const getRiskIconBackground = (level?: RiskLevel) => {
  const backgrounds: Record<RiskLevel, string> = {
    low: 'bg-gradient-to-r from-green-500 to-emerald-600',
    moderate: 'bg-gradient-to-r from-yellow-500 to-orange-600',
    high: 'bg-gradient-to-r from-red-500 to-pink-600',
    critical: 'bg-gradient-to-r from-red-600 to-red-800',
  }
  return level ? backgrounds[level] : 'bg-gradient-to-r from-gray-500 to-gray-600'
}

const getRiskGradient = (level?: RiskLevel) => {
  const gradients: Record<RiskLevel, string> = {
    low: 'bg-gradient-to-r from-green-500 to-emerald-600',
    moderate: 'bg-gradient-to-r from-yellow-500 to-orange-600',
    high: 'bg-gradient-to-r from-red-500 to-pink-600',
    critical: 'bg-gradient-to-r from-red-600 to-red-800',
  }
  return level ? gradients[level] : 'bg-gradient-to-r from-gray-500 to-gray-600'
}

const getRiskLabel = (level?: RiskLevel) => {
  const labels: Record<RiskLevel, string> = {
    low: 'Low Risk',
    moderate: 'Moderate Risk',
    high: 'High Risk',
    critical: 'Critical Risk',
  }
  return level ? labels[level] : 'Unknown Risk'
}

const getRiskDescription = (level?: RiskLevel) => {
  const descriptions: Record<RiskLevel, string> = {
    low: 'Excellent performance indicators',
    moderate: 'Some areas need attention',
    high: 'Significant concerns identified',
    critical: 'Immediate action required',
  }
  return level ? descriptions[level] : 'Risk level assessment'
}

const initCharts = () => {
  nextTick(() => {
    // Initialize charts here if needed
    // This is a placeholder for chart initialization
    console.log('Charts would be initialized here')
  })
}

// Lifecycle
onMounted(() => {
  analyticsStore.fetchReports()
  initCharts()
})
</script>
