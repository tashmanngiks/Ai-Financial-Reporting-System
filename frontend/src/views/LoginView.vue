<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900">AI Financial Analytics</h1>
        <p class="mt-2 text-gray-600">Sign in to your account</p>
      </div>

      <!-- Login Form -->
      <div class="card">
        <div class="card-body">
          <form @submit.prevent="handleLogin" class="space-y-6">
            <!-- Email/Username -->
            <div>
              <label for="username" class="form-label">Username or Email</label>
              <input
                id="username"
                v-model="loginForm.username"
                type="text"
                required
                autocomplete="username"
                class="form-input"
                placeholder="Enter your username or email"
              />
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="form-label">Password</label>
              <input
                id="password"
                v-model="loginForm.password"
                type="password"
                required
                autocomplete="current-password"
                class="form-input"
                placeholder="Enter your password"
              />
            </div>

            <!-- Remember Me -->
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <input
                  id="remember-me"
                  v-model="loginForm.rememberMe"
                  type="checkbox"
                  class="rounded border-gray-300 focus:ring-primary-500" style="color: var(--primary-color);"
                />
                <label for="remember-me" class="ml-2 text-sm text-gray-700">
                  Remember me
                </label>
              </div>
              <a href="#" class="text-sm" style="color: var(--primary-color);" onmouseover="this.style.color='var(--primary-dark)'" onmouseout="this.style.color='var(--primary-color)'">
                Forgot your password?
              </a>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="rounded-md bg-danger-50 p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <ExclamationTriangleIcon class="h-5 w-5 text-danger-400" />
                </div>
                <div class="ml-3">
                  <h3 class="text-sm font-medium text-danger-800">
                    {{ error }}
                  </h3>
                </div>
              </div>
            </div>

            <!-- Submit Button -->
            <div>
              <button
                type="submit"
                :disabled="loading"
                class="btn w-full" style="background-color: var(--primary-color); color: white;"
              >
                <span v-if="!loading">Sign in</span>
                <span v-else class="flex items-center justify-center">
                  <div class="loading-spinner w-4 h-4 mr-2"></div>
                  Signing in...
                </span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

// Reactive state
const loading = ref(false)
const error = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

// Methods
const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    // Redirect to dashboard on success
    router.push('/')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
