<template>
  <header style="background-color: var(--primary-color); color: white;" class="shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo and title -->
        <div class="flex items-center">
          <div class="shrink-0">
            <h1 class="text-xl font-bold">
              AI Financial Analytics
            </h1>
          </div>
        </div>


        <!-- User menu -->
        <div class="flex items-center space-x-4">
          <!-- System health indicator -->
          <div class="flex items-center" role="status" aria-label="System health">
            <div
              :class="[
                'w-2 h-2 rounded-full mr-2',
                systemHealth.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              ]"
              aria-hidden="true"
            ></div>
            <span class="text-sm text-gray-600">System</span>
          </div>

          <!-- User dropdown -->
          <div class="relative" ref="userMenuRef">
            <button
              type="button"
              @click="showUserMenu = !showUserMenu"
              class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              :aria-expanded="showUserMenu"
              aria-haspopup="menu"
              aria-label="Open user account menu"
            >
              <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center" aria-hidden="true">
                <span class="text-white font-medium">
                  {{ userInitials }}
                </span>
              </div>
            </button>

            <!-- Dropdown menu -->
            <div
              v-if="showUserMenu"
              class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
              role="menu"
            >
              <div class="py-1">
                <div class="px-4 py-2 text-sm text-gray-700 border-b">
                  <div class="font-medium">{{ authStore.user?.username }}</div>
                  <div class="text-gray-500">{{ authStore.user?.email }}</div>
                </div>
                <button
                  type="button"
                  role="menuitem"
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

// Reactive state
const showUserMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)
const systemHealth = ref({
  status: 'healthy' as 'healthy' | 'unhealthy',
  timestamp: null as string | null,
})

// Computed properties
const userInitials = computed(() => {
  if (!authStore.user) return 'U'
  const { first_name, last_name, username } = authStore.user
  if (first_name && last_name) {
    return `${first_name[0]}${last_name[0]}`.toUpperCase()
  }
  return username?.slice(0, 2).toUpperCase() || 'U'
})

// Methods
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
  showUserMenu.value = false
}

const fetchSystemHealth = async () => {
  try {
    const response = await api.getSystemHealth()
    systemHealth.value = response.data
  } catch (error) {
    console.error('Failed to fetch system health:', error)
    systemHealth.value = { status: 'unhealthy', timestamp: null }
  }
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target

  if (userMenuRef.value && target instanceof Node && !userMenuRef.value.contains(target)) {
    showUserMenu.value = false
  }
}

// Lifecycle
let healthInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  fetchSystemHealth()
  document.addEventListener('click', handleClickOutside)

  // Set up periodic health checks
  healthInterval = setInterval(fetchSystemHealth, 60000) // Every minute
})

onUnmounted(() => {
  if (healthInterval) {
    clearInterval(healthInterval)
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>
