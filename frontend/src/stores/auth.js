import { defineStore } from 'pinia'
import { api } from '@/services/api'

const AUTH_TOKEN_KEY = 'auth_token'
const AUTH_USER_KEY = 'auth_user'

const readStoredUser = () => {
  const raw = localStorage.getItem(AUTH_USER_KEY)
  if (!raw) {
    return null
  }

  try {
    return JSON.parse(raw)
  } catch {
    localStorage.removeItem(AUTH_USER_KEY)
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: readStoredUser(),
    token: localStorage.getItem(AUTH_TOKEN_KEY) || null,
    isAuthenticated: !!localStorage.getItem(AUTH_TOKEN_KEY),
    initialized: false,
    loading: false,
    error: null,
  }),

  getters: {
    currentUser: (state) => state.user,
    isLoggedIn: (state) => !!state.token && state.isAuthenticated,
    isAdmin: (state) => !!(state.user?.is_staff || state.user?.is_superuser),
  },

  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        // Use Django session authentication
        const response = await api.login(credentials)

        this.token = 'session-auth' // Django uses session auth
        this.user = response.data.user || { username: credentials.username }
        this.isAuthenticated = true
        this.initialized = true

        // Store session info
        localStorage.setItem(AUTH_TOKEN_KEY, this.token)
        localStorage.setItem(AUTH_USER_KEY, JSON.stringify(this.user))

        const { useAnalyticsStore } = await import('./analytics')
        const analyticsStore = useAnalyticsStore()
        await analyticsStore.fetchReports()

        return { success: true, user: this.user }
      } catch (error) {
        this.error = error.message || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try {
        // await api.post('/auth/logout/')

        // Clear local state
        this.token = null
        this.user = null
        this.isAuthenticated = false
        this.initialized = true
        this.error = null

        localStorage.removeItem(AUTH_TOKEN_KEY)
        localStorage.removeItem(AUTH_USER_KEY)
      } catch (error) {
        console.error('Logout error:', error)
      }
    },

    async refreshToken() {
      try {
        // const response = await api.post('/auth/refresh/')
        // this.token = response.data.token
        // localStorage.setItem('auth_token', this.token)
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async fetchUser() {
      try {
        const response = await api.getCurrentUser()
        const currentUser = response.data?.user || null
        this.user = currentUser
        this.isAuthenticated = true
        if (currentUser) {
          localStorage.setItem(AUTH_USER_KEY, JSON.stringify(currentUser))
        }
        return this.user
      } catch (error) {
        this.user = null
        this.token = null
        this.isAuthenticated = false
        throw error
      }
    },

    async initializeAuth() {
      if (this.initialized) {
        return this.isAuthenticated
      }

      this.loading = true
      this.error = null

      const token = localStorage.getItem(AUTH_TOKEN_KEY)
      if (token) {
        this.token = token
        try {
          await this.fetchUser()
        } catch {
          await this.logout()
        }
      } else {
        await this.logout()
      }

      this.initialized = true
      this.loading = false

      if (this.isAuthenticated) {
        const { useAnalyticsStore } = await import('./analytics')
        const analyticsStore = useAnalyticsStore()
        await analyticsStore.fetchReports()
      }

      return this.isAuthenticated
    },
  },
})
