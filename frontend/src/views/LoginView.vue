<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 px-4 sm:px-6 lg:px-8">
    <!-- Background image (place your image at frontend/public/login-bg.jpg) -->
    <div class="absolute inset-0 overflow-hidden">
      <div
        class="absolute inset-0 bg-cover bg-center"
        style="background-image: url('/login-bg.svg'); filter: blur(3px) saturate(1.1); opacity: 0.72; background-repeat: no-repeat; background-size: cover;"
        aria-hidden="true"
      ></div>
      <!-- subtle dark overlay to improve contrast -->
      <div class="absolute inset-0 bg-gradient-to-tr from-slate-900/70 to-slate-900/80" aria-hidden="true"></div>
    </div>

    <div class="relative max-w-md w-full">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-lg mb-4">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h1 class="text-4xl font-bold text-white mb-2">AI Financial Analytics</h1>
        <p class="text-gray-400">Sign in to your account</p>
      </div>

      <!-- Login Card -->
      <div class="bg-slate-800 rounded-2xl shadow-2xl p-8 space-y-8 backdrop-blur-sm border border-slate-700">
        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <!-- Username/Email Field -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-300 mb-2">
              Username or Email
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 01-5 0V12m0 0v-1.5a2.5 2.5 0 015 0V12m0 0h4m0 0v1.5a2.5 2.5 0 01-5 0V12" />
                </svg>
              </div>
              <input
                id="username"
                v-model="loginForm.username"
                type="text"
                required
                autocomplete="username"
                class="w-full pl-10 pr-4 py-3 bg-slate-700 border border-slate-600 text-white placeholder-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="Enter your username"
              />
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
              Password
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                id="password"
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                autocomplete="current-password"
                class="w-full pl-10 pr-12 py-3 bg-slate-700 border border-slate-600 text-white placeholder-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                placeholder="Enter your password"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-300 transition"
              >
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-4.803m5.596-3.856a3.375 3.375 0 11-4.753 4.753m12.384-12.353A10.048 10.048 0 0112 5c-4.478 0-8.268 2.943-9.543 7a10.047 10.047 0 001.586 4.823m8.369 6.46l-6.16-6.16" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between">
            <label class="flex items-center">
              <input
                v-model="loginForm.rememberMe"
                type="checkbox"
                class="w-4 h-4 bg-slate-700 border border-slate-600 text-blue-500 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
              />
              <span class="ml-2 text-sm text-gray-400">Remember me</span>
            </label>
            <a href="#" class="text-sm text-blue-400 hover:text-blue-300 transition">
              Forgot password?
            </a>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="rounded-lg bg-red-900/20 border border-red-800 p-4">
            <div class="flex gap-3">
              <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-sm font-medium text-red-400">
                  {{ error }}
                </h3>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:from-gray-500 disabled:to-gray-600 transition duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none flex items-center justify-center gap-2"
          >
            <div v-if="loading" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>{{ loading ? 'Signing in...' : 'Sign in' }}</span>
          </button>
        </form>
      </div>

      <!-- Footer -->
      <div class="mt-8 text-center">
        <p class="text-sm text-gray-500">
          Contact your administrator for account details
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Reactive state
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

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

