<template>
  <aside class="w-48 h-full bg-gradient-to-b from-gray-900 to-gray-800 border-r-8 border-gray-700 rounded-r-2xl">
    <div class="py-6">
      <!-- Navigation -->
      <nav class="space-y-2">
        <router-link
          v-for="item in navigationItems"
          :key="item.name"
          :to="item.to"
          :class="[
            'group flex items-center px-4 py-3 rounded-lg transition-all duration-200 relative',
            isActiveRoute(item.to)
              ? 'text-white bg-gradient-to-r from-[#08AAC7] to-[#0691A8]'
              : 'text-gray-300 hover:text-white hover:bg-gray-700'
          ]"
        >
          <!-- Icon -->
          <component
            :is="item.icon"
            class="h-5 w-5 mr-3"
            :style="isActiveRoute(item.to) ? { color: 'white' } : { color: '#94a3b8' }"
          />

          <!-- Text Label -->
          <span class="text-sm font-medium">{{ item.name }}</span>
        </router-link>
      </nav>

      <!-- Recent Reports -->
      <div class="mt-8 px-4" v-if="analyticsStore.recentReports.length > 0">
        <div class="space-y-2">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Recent Reports</h3>
          <div class="space-y-2">
            <router-link
              v-for="report in analyticsStore.recentReports.slice(0, 3)"
              :key="report.id"
              :to="`/reports/${report.id}`"
              class="block p-2 rounded-md transition-colors duration-200 text-gray-300 bg-gray-700 hover:bg-gray-600 group"
            >
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <div class="flex-1">
                  <div class="text-xs font-medium text-white truncate group-hover:text-[#08AAC7] transition-colors">
                    {{ report.bank_name }}
                  </div>
                  <div class="text-xs text-gray-500">
                    {{ formatDate(report.generated_at) }}
                  </div>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import {
  HomeIcon,
  DocumentArrowUpIcon,
  DocumentTextIcon,
  ChartBarIcon,
  CogIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const analyticsStore = useAnalyticsStore()

type NavigationItem = {
  name: string
  to: string
  icon: unknown
}

// Navigation items
const navigationItems: NavigationItem[] = [
  {
    name: 'Dashboard',
    to: '/dashboard',
    icon: HomeIcon,
  },
  {
    name: 'Upload Data',
    to: '/upload',
    icon: DocumentArrowUpIcon,
  },
  {
    name: 'Reports',
    to: '/reports',
    icon: DocumentTextIcon,
  },
  {
    name: 'Analytics',
    to: '/analytics',
    icon: ChartBarIcon,
  },
  {
    name: 'Settings',
    to: '/settings',
    icon: CogIcon,
  },
]

// Methods
const isActiveRoute = (to: string) => {
  if (route.path === to) return true
  if (to === '/dashboard' && route.path === '/') return true
  return false
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

// No mock data function - using real API endpoints only

</script>
