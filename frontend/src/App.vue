<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initializeAuth()
})
</script>

<template>
  <div class="h-screen bg-gray-50 overflow-hidden">
    <!-- Header -->
    <AppHeader v-if="authStore.isLoggedIn" class="fixed top-0 left-0 right-0 z-50" />

    <!-- Main Content -->
    <div :class="authStore.isLoggedIn ? 'flex h-screen pt-16' : 'h-screen'">
      <!-- Sidebar -->
      <AppSidebar v-if="authStore.isLoggedIn" class="flex-shrink-0" />

      <!-- Main Content Area -->
      <main :class="authStore.isLoggedIn ? 'flex-1 overflow-y-auto h-full' : 'h-full overflow-y-auto'">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style>
/* WebKit scrollbar styling (Safari, Chrome, Edge) */
*::-webkit-scrollbar {
  width: 6px;
}

*::-webkit-scrollbar-track {
  background: #f1f5f9;
}

*::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

*::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
}

/* Firefox scrollbar styling */
@supports (scrollbar-width: thin) {
  * {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e1 #f1f5f9;
  }
}

/* Hide main body scrollbar */
body {
  overflow: hidden;
}

/* Ensure smooth scrolling */
html {
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
}

@supports (text-size-adjust: 100%) {
  html {
    text-size-adjust: 100%;
  }
}

/* Login page specific styles */
.login-container {
  height: 100vh;
  overflow-y: auto;
}
</style>
