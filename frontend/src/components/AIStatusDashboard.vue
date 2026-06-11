<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-gray-900">AI System Status</h3>
      <div class="flex items-center space-x-2">
        <div 
          :class="statusIndicatorClass" 
          class="w-3 h-3 rounded-full animate-pulse"
        ></div>
        <span :class="statusTextClass" class="text-sm font-medium">
          {{ statusText }}
        </span>
      </div>
    </div>

    <!-- AI Configuration -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
      <div class="space-y-4">
        <h4 class="text-sm font-semibold text-gray-700">Configuration</h4>
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Model:</span>
            <span class="font-medium text-gray-900">{{ aiStatus.configuration?.model || 'N/A' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Max Tokens:</span>
            <span class="font-medium text-gray-900">{{ aiStatus.configuration?.max_tokens || 'N/A' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Temperature:</span>
            <span class="font-medium text-gray-900">{{ aiStatus.configuration?.temperature || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <h4 class="text-sm font-semibold text-gray-700">Rate Limiting</h4>
        <div class="space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Delay:</span>
            <span class="font-medium text-gray-900">{{ aiStatus.configuration?.rate_limit_delay || 'N/A' }}s</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Max Retries:</span>
            <span class="font-medium text-gray-900">{{ aiStatus.configuration?.max_retries || 'N/A' }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-600">Daily Limit:</span>
            <span class="font-medium text-gray-900">{{ aiStatus.configuration?.daily_quota_limit || 'N/A' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quota Status -->
    <div v-if="aiStatus.quota_status" class="mb-6">
      <h4 class="text-sm font-semibold text-gray-700 mb-3">Quota Status</h4>
      <div class="space-y-3">
        <div>
          <div class="flex justify-between text-sm mb-1">
            <span class="text-gray-600">Daily Usage</span>
            <span class="font-medium text-gray-900">
              {{ aiStatus.quota_status.daily_usage || 0 }} / {{ aiStatus.quota_status.daily_quota_limit || 0 }}
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div 
              :class="quotaBarClass" 
              :style="{ width: quotaPercentage + '%' }"
              class="h-2 rounded-full transition-all duration-300"
            ></div>
          </div>
        </div>
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Remaining:</span>
          <span :class="quotaTextClass" class="font-medium">
            {{ aiStatus.quota_status.remaining_quota || 0 }}
          </span>
        </div>
      </div>
    </div>

    <!-- Features Status -->
    <div class="mb-6">
      <h4 class="text-sm font-semibold text-gray-700 mb-3">AI Features</h4>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div 
          v-for="(enabled, feature) in aiStatus.features" 
          :key="feature"
          class="flex items-center space-x-2 text-sm"
        >
          <div 
            :class="enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-400'"
            class="w-2 h-2 rounded-full"
          ></div>
          <span :class="enabled ? 'text-gray-700' : 'text-gray-400'">
            {{ formatFeatureName(feature) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex space-x-3 pt-4 border-t border-gray-200">
      <button
        @click="testAIConnection"
        :disabled="testing"
        class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="!testing">Test Connection</span>
        <span v-else class="flex items-center">
          <div class="animate-spin w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
          Testing...
        </span>
      </button>
      
      <button
        @click="refreshStatus"
        :disabled="refreshing"
        class="px-4 py-2 bg-gray-600 text-white text-sm rounded-lg hover:bg-gray-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="!refreshing">Refresh</span>
        <span v-else class="flex items-center">
          <div class="animate-spin w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
          Refreshing...
        </span>
      </button>

      <button
        v-if="isAdmin"
        @click="resetQuota"
        :disabled="resetting"
        class="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="!resetting">Reset Quota</span>
        <span v-else class="flex items-center">
          <div class="animate-spin w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
          Resetting...
        </span>
      </button>
    </div>

    <!-- Test Results Modal -->
    <div v-if="testResults" class="mt-4 p-4 bg-gray-50 rounded-lg">
      <h4 class="text-sm font-semibold text-gray-700 mb-2">Test Results</h4>
      <div class="space-y-2 text-sm">
        <div class="flex justify-between">
          <span class="text-gray-600">Status:</span>
          <span :class="testResults.test_successful ? 'text-green-600' : 'text-red-600'" class="font-medium">
            {{ testResults.test_successful ? 'Success' : 'Failed' }}
          </span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600">Response Time:</span>
          <span class="font-medium text-gray-900">{{ testResults.response_time_seconds?.toFixed(2) || 'N/A' }}s</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600">Insights Generated:</span>
          <span class="font-medium text-gray-900">{{ testResults.insights_generated || 0 }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600">Data Source:</span>
          <span class="font-medium text-gray-900">
            {{ testResults.data_sources?.[0] || 'N/A' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AIStatusDashboard',
  setup() {
    const authStore = useAuthStore()
    
    const aiStatus = ref({})
    const loading = ref(false)
    const refreshing = ref(false)
    const testing = ref(false)
    const resetting = ref(false)
    const testResults = ref(null)

    const isAdmin = computed(() => authStore.user?.is_staff || false)

    const statusIndicatorClass = computed(() => {
      if (!aiStatus.value.ai_enabled) return 'bg-gray-400'
      if (aiStatus.value.system_health === 'healthy') return 'bg-green-500'
      if (aiStatus.value.system_health === 'degraded') return 'bg-yellow-500'
      return 'bg-red-500'
    })

    const statusTextClass = computed(() => {
      if (!aiStatus.value.ai_enabled) return 'text-gray-500'
      if (aiStatus.value.system_health === 'healthy') return 'text-green-600'
      if (aiStatus.value.system_health === 'degraded') return 'text-yellow-600'
      return 'text-red-600'
    })

    const statusText = computed(() => {
      if (!aiStatus.value.ai_enabled) return 'AI Disabled'
      if (aiStatus.value.system_health === 'healthy') return 'AI Healthy'
      if (aiStatus.value.system_health === 'degraded') return 'AI Degraded'
      return 'AI Error'
    })

    const quotaPercentage = computed(() => {
      if (!aiStatus.value.quota_status) return 0
      const usage = aiStatus.value.quota_status.daily_usage || 0
      const limit = aiStatus.value.quota_status.daily_quota_limit || 1
      return Math.min((usage / limit) * 100, 100)
    })

    const quotaBarClass = computed(() => {
      const percentage = quotaPercentage.value
      if (percentage >= 90) return 'bg-red-500'
      if (percentage >= 70) return 'bg-yellow-500'
      return 'bg-green-500'
    })

    const quotaTextClass = computed(() => {
      const percentage = quotaPercentage.value
      if (percentage >= 90) return 'text-red-600'
      if (percentage >= 70) return 'text-yellow-600'
      return 'text-green-600'
    })

    const fetchAIStatus = async () => {
      try {
        const response = await fetch('/api/analytics/ai/status/')
        if (response.ok) {
          aiStatus.value = await response.json()
        }
      } catch (error) {
        console.error('Failed to fetch AI status:', error)
      }
    }

    const refreshStatus = async () => {
      refreshing.value = true
      await fetchAIStatus()
      refreshing.value = false
    }

    const testAIConnection = async () => {
      testing.value = true
      testResults.value = null
      
      try {
        const response = await fetch('/api/analytics/ai/test/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          }
        })
        
        if (response.ok) {
          testResults.value = await response.json()
        } else {
          testResults.value = {
            test_successful: false,
            error: 'Test failed'
          }
        }
      } catch (error) {
        testResults.value = {
          test_successful: false,
          error: error.message
        }
      }
      
      testing.value = false
    }

    const resetQuota = async () => {
      if (!confirm('Are you sure you want to reset the AI quota tracking?')) return
      
      resetting.value = true
      
      try {
        const response = await fetch('/api/analytics/ai/reset-quota/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          }
        })
        
        if (response.ok) {
          await fetchAIStatus()
          alert('Quota tracking reset successfully')
        } else {
          alert('Failed to reset quota')
        }
      } catch (error) {
        alert('Error resetting quota: ' + error.message)
      }
      
      resetting.value = false
    }

    const formatFeatureName = (feature) => {
      return feature.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
    }

    const getCookie = (name) => {
      let cookieValue = null
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim()
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
            break
          }
        }
      }
      return cookieValue
    }

    onMounted(() => {
      fetchAIStatus()
    })

    return {
      aiStatus,
      loading,
      refreshing,
      testing,
      resetting,
      testResults,
      isAdmin,
      statusIndicatorClass,
      statusTextClass,
      statusText,
      quotaPercentage,
      quotaBarClass,
      quotaTextClass,
      refreshStatus,
      testAIConnection,
      resetQuota,
      formatFeatureName
    }
  }
}
</script>
