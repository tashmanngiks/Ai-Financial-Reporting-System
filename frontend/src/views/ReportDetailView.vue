<template>
  <div class="p-6">
    <div v-if="analyticsStore.loading.report" class="text-center py-12">
      <div class="loading-spinner w-8 h-8 mx-auto mb-4"></div>
      <p class="text-gray-500">Loading report...</p>
    </div>

    <div v-else-if="report" class="space-y-6 max-w-7xl mx-auto">
      <!-- Header -->
      <div class="card">
        <div class="card-header">
          <div class="flex flex-col gap-4 sm:flex-row sm:justify-between sm:items-start">
            <div class="min-w-0 flex-1">
              <h1 class="text-2xl font-bold text-gray-900 break-words">{{ reportTitle }}</h1>
              <p class="text-gray-600 mt-1">
                {{ getShortReportLabel(report) }} • {{ report.data_period || report.metadata?.period || 'Unknown period' }}
              </p>
              <p class="text-sm text-gray-500 mt-1">
                {{ report.filename }} • Generated {{ report.uploaded_at || report.metadata?.generated_at }}
              </p>
              <span
                v-if="report.ai_enhanced"
                class="inline-flex mt-2 items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
              >
                AI-generated
              </span>
            </div>
            <div class="flex flex-wrap gap-2 shrink-0">
              <a
                :href="`/api/media/${report.id}/print/`"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-secondary text-sm"
              >
                Export PDF
              </a>
              <a
                :href="`/api/media/${report.id}/editable/`"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-secondary text-sm"
              >
                Export Word
              </a>
              <button
                v-if="report.user_prompt || report.metadata?.user_prompt"
                @click="regenerateReport"
                :disabled="analyticsStore.loading.insights"
                class="btn btn-primary text-sm"
              >
                <span v-if="!analyticsStore.loading.insights">Regenerate AI Report</span>
                <span v-else class="flex items-center">
                  <div class="loading-spinner w-4 h-4 mr-2"></div>
                  Regenerating...
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="reportOptionsSummary" class="card">
        <div class="card-header">
          <h2 class="text-lg font-medium text-gray-900">Report settings</h2>
        </div>
        <div class="card-body space-y-3 text-sm text-gray-700">
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="rounded-lg bg-gray-50 p-3">
              <div class="text-xs uppercase tracking-wide text-gray-500">Template</div>
              <div class="font-medium text-gray-900">{{ reportOptionsSummary.template }}</div>
            </div>
            <div class="rounded-lg bg-gray-50 p-3">
              <div class="text-xs uppercase tracking-wide text-gray-500">Length</div>
              <div class="font-medium text-gray-900">{{ reportOptionsSummary.length }}</div>
            </div>
            <div class="rounded-lg bg-gray-50 p-3">
              <div class="text-xs uppercase tracking-wide text-gray-500">Format</div>
              <div class="font-medium text-gray-900">{{ reportOptionsSummary.output_format }}</div>
            </div>
          </div>
          <div>
            <div class="text-xs uppercase tracking-wide text-gray-500 mb-2">Selected sections</div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="section in reportOptionsSummary.sections"
                :key="section"
                class="inline-flex items-center rounded-full bg-[#08AAC7]/10 px-3 py-1 text-xs font-medium text-[#056F80]"
              >
                {{ sectionLabel(section) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Legacy template report (pre-AI) -->
      <div v-if="hasLegacyTemplateOnly" class="card border-amber-200 bg-amber-50">
        <div class="card-body text-sm text-amber-900">
          <p>
            This report was created with an older template engine, not your prompt.
            Use <strong>Regenerate AI Report</strong> after fixing your OpenAI billing to get a real AI analysis.
          </p>
        </div>
      </div>

      <!-- AI error -->
      <div v-if="report.ai_error && !displaySections.length" class="card border-yellow-200 bg-yellow-50">
        <div class="card-body">
          <p class="text-sm text-yellow-900">
            <strong>AI analysis unavailable:</strong> {{ report.ai_error }}
          </p>
          <p v-if="isQuotaError" class="text-sm text-yellow-800 mt-2">
            Add billing or credits at
            <a href="https://platform.openai.com/account/billing" target="_blank" rel="noopener" class="underline font-medium">
              OpenAI Billing
            </a>
            , then upload again or use Regenerate AI Report.
          </p>
        </div>
      </div>

      <!-- Overleaf-style prompt ↔ report pairs -->
      <div v-if="displaySections.length" class="space-y-3">
        <p class="text-sm text-gray-600">
          Click a report section to highlight its prompt. Edit the left side, then Update section.
        </p>
        <PromptReportSplitPane :report-id="reportId" />
      </div>

      <div v-else-if="!report.ai_error" class="card">
        <div class="card-body text-center py-8">
          <p class="text-gray-600">No AI analysis sections for this report yet.</p>
          <router-link to="/upload" class="btn btn-primary mt-4 inline-block">Upload with a new prompt</router-link>
        </div>
      </div>
    </div>

    <div v-else class="card">
      <div class="card-body text-center py-8">
        <ExclamationTriangleIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Report not found</h3>
        <router-link to="/reports" class="btn btn-primary">Back to reports</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { getShortReportLabel } from '@/utils/reportDisplay'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import PromptReportSplitPane from '@/components/PromptReportSplitPane.vue'

const route = useRoute()
const analyticsStore = useAnalyticsStore()

const reportId = computed(() => String(route.params.id || ''))
const report = computed(() => analyticsStore.reportDetail)

const userPrompt = computed(
  () => report.value?.user_prompt || report.value?.metadata?.user_prompt || ''
)

const reportOptionsSummary = computed(() => {
  const options = report.value?.metadata?.report_options || report.value?.report_options || null
  if (!options) return null
  return {
    template: options.template || 'custom',
    length: options.length || 'standard',
    output_format: options.output_format || 'pdf',
    sections: Array.isArray(options.sections) ? options.sections : [],
  }
})

const reportTitle = computed(() => {
  const r = report.value
  if (!r) return 'Analysis Report'
  return getShortReportLabel(r)
})

const displaySections = computed(() => {
  if (!report.value?.ai_enhanced) return []
  return report.value?.comprehensive_analysis || []
})

const hasLegacyTemplateOnly = computed(() => {
  const sections = report.value?.comprehensive_analysis || []
  return sections.length > 0 && !report.value?.ai_enhanced
})

const isQuotaError = computed(() => {
  const err = report.value?.ai_error || ''
  return /quota|billing/i.test(err)
})

function sectionLabel(sectionKey: string) {
  return sectionKey
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

const regenerateReport = async () => {
  try {
    await analyticsStore.regenerateAiReport(reportId.value)
  } catch (error) {
    console.error('Regeneration failed:', error)
  }
}

onMounted(() => {
  if (reportId.value && reportId.value !== 'undefined') {
    analyticsStore.fetchReport(reportId.value)
  }
})

watch(
  () => route.params.id,
  (newId) => {
    if (newId && newId !== 'undefined') {
      analyticsStore.fetchReport(String(newId))
    }
  }
)
</script>

