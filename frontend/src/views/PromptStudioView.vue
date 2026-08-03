<template>
  <div class="p-6">
    <div v-if="reportId">
      <PromptReportSplitPane :report-id="reportId" />
    </div>
    <div v-else class="card p-8 max-w-lg mx-auto text-center space-y-3">
      <h1 class="text-lg font-semibold text-gray-900">Refine prompts with a report</h1>
      <p class="text-sm text-gray-600">
        Generate a report from Upload Data — the prompt ↔ report split view opens there automatically.
        Or open an existing report from Reports.
      </p>
      <div class="flex justify-center gap-2">
        <router-link to="/upload" class="btn btn-primary text-sm">Upload Data</router-link>
        <router-link to="/reports" class="btn btn-secondary text-sm">Reports</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import PromptReportSplitPane from '@/components/PromptReportSplitPane.vue'

const route = useRoute()
const reportId = computed(() => String(route.params.reportId || ''))
</script>
