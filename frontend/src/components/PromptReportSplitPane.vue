<template>
  <div class="flex flex-col border border-gray-200 rounded-xl overflow-hidden bg-white min-h-[75vh]">
    <!-- Headers -->
    <div class="grid grid-cols-1 lg:grid-cols-2 border-b bg-gray-50 shrink-0">
      <div class="px-4 py-2.5 border-r border-gray-200 flex items-center justify-between gap-2">
        <span class="text-[11px] font-semibold uppercase tracking-wider text-[#056F80]">
          Source · Full Prompt
        </span>
        <div class="flex gap-1" v-if="selectedPair">
          <button
            v-if="selectedPair.module && isAdmin"
            type="button"
            class="text-xs px-2 py-1 rounded bg-[#08AAC7] text-white hover:bg-[#0691A8] disabled:opacity-50"
            :disabled="saving"
            @click="saveSelected"
          >
            {{ saving ? 'Saving…' : 'Save prompt' }}
          </button>
          <button
            type="button"
            class="text-xs px-2 py-1 rounded border border-gray-300 bg-white text-gray-700 hover:bg-gray-100 disabled:opacity-50"
            :disabled="regenerating || !selectedKey"
            @click="regenerateSelected"
          >
            {{ regenerating ? 'Updating…' : 'Update selected section' }}
          </button>
        </div>
      </div>
      <div class="px-4 py-2.5 hidden lg:flex items-center justify-between">
        <span class="text-[11px] font-semibold uppercase tracking-wider text-emerald-700">
          Output · Full Generated Report
        </span>
        <span v-if="selectedPair" class="text-[11px] text-gray-500 truncate max-w-[50%]">
          Selected: {{ selectedPair.reportTitle }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="flex-1 flex items-center justify-center py-16 text-gray-500 text-sm">
      Loading full prompt and report…
    </div>

    <!-- Two full panes side by side -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 flex-1 min-h-0" style="height: 70vh">
      <!-- LEFT: whole prompt document -->
      <div
        ref="promptPane"
        class="border-r border-gray-200 overflow-y-auto p-4 space-y-4 bg-white"
      >
        <section
          class="rounded-lg border p-3"
          :class="selectedKey === '__master__' ? 'border-[#08AAC7] bg-[#08AAC7]/5' : 'border-gray-200'"
          @click="selectedKey = '__master__'"
        >
          <h3 class="text-sm font-semibold text-gray-900 mb-1">Master Analysis Prompt</h3>
          <p class="text-[11px] text-gray-500 mb-2">Dataset-level prompt used for this report</p>
          <pre class="whitespace-pre-wrap font-mono text-xs text-gray-800 leading-relaxed">{{ masterPrompt || 'No master prompt stored.' }}</pre>
        </section>

        <section
          v-for="pair in pairedRows"
          :id="`prompt-${pair.sectionKey}`"
          :key="'p-' + pair.sectionKey"
          class="rounded-lg border p-3 transition-colors"
          :class="selectedKey === pair.sectionKey
            ? 'border-[#08AAC7] bg-[#08AAC7]/10 ring-1 ring-[#08AAC7]/40'
            : 'border-gray-200 hover:border-gray-300'"
          @click="selectSection(pair.sectionKey, 'prompt')"
        >
          <div class="flex items-center justify-between gap-2 mb-2">
            <h3 class="text-sm font-semibold text-gray-900">{{ pair.promptTitle }}</h3>
            <span class="text-[11px] text-gray-500 shrink-0">
              <template v-if="pair.module">v{{ pair.module.version_current }}</template>
              <template v-if="staleKeys.has(pair.sectionKey)"> · pending</template>
            </span>
          </div>
          <textarea
            v-if="pair.module"
            v-model="drafts[pair.sectionKey]"
            rows="8"
            class="w-full border border-gray-200 rounded p-2 font-mono text-xs leading-relaxed focus:ring-1 focus:ring-[#08AAC7] bg-white"
            :readonly="!isAdmin"
            @click.stop
            @focus="selectSection(pair.sectionKey, 'prompt')"
          />
          <pre
            v-else
            class="whitespace-pre-wrap font-mono text-xs text-gray-600"
          >No module linked for this section.</pre>
        </section>
      </div>

      <!-- RIGHT: whole generated report -->
      <div
        ref="reportPane"
        class="overflow-y-auto p-4 space-y-6 bg-white"
      >
        <header class="border-b border-gray-100 pb-3 mb-2">
          <h2 class="text-lg font-semibold text-gray-900">{{ reportTitle }}</h2>
          <p class="text-sm text-gray-500">
            {{ report?.bank_name || 'Financial Dataset' }}
            · {{ report?.data_period || report?.metadata?.period || '' }}
          </p>
        </header>

        <article
          v-for="pair in pairedRows"
          :id="`report-${pair.sectionKey}`"
          :key="'r-' + pair.sectionKey"
          class="rounded-lg border p-4 transition-colors cursor-pointer"
          :class="selectedKey === pair.sectionKey
            ? 'border-[#08AAC7] bg-[#08AAC7]/10 ring-1 ring-[#08AAC7]/40'
            : 'border-transparent hover:border-gray-200'"
          @click="selectSection(pair.sectionKey, 'report')"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <h3 class="text-base font-semibold text-gray-900">{{ pair.reportTitle }}</h3>
            <span
              v-if="changedKeys.has(pair.sectionKey)"
              class="text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 shrink-0"
            >Updated</span>
          </div>
          <p v-if="pair.trace" class="text-[11px] text-gray-500 mb-2">
            Produced by {{ pair.trace.prompt_module_name || 'prompt' }}
            <span v-if="pair.trace.prompt_module_version">· v{{ pair.trace.prompt_module_version }}</span>
            <span v-if="pair.trace.ai_model">· {{ pair.trace.ai_model }}</span>
          </p>
          <div class="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
            <template v-if="pair.missing">
              <span class="text-amber-700">This section was requested but not returned by the AI. Select it and click Update selected section.</span>
            </template>
            <template v-else>
              {{ pair.reportNarrative || 'No content.' }}
            </template>
          </div>
          <ul v-if="pair.keyPoints.length" class="mt-3 list-disc list-inside text-sm text-gray-700 space-y-1">
            <li v-for="(point, i) in pair.keyPoints" :key="i">{{ point }}</li>
          </ul>
          <ul v-if="pair.recommendations.length" class="mt-3 list-disc list-inside text-sm text-gray-700 space-y-1">
            <li v-for="(rec, i) in pair.recommendations" :key="'rec-' + i">{{ formatRec(rec) }}</li>
          </ul>
        </article>

        <p v-if="!pairedRows.length" class="text-sm text-gray-500 text-center py-12">
          No generated report sections yet.
        </p>
      </div>
    </div>

    <p v-if="statusMessage" class="px-4 py-2 text-xs border-t bg-gray-50 text-gray-600 shrink-0">
      {{ statusMessage }}
    </p>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const props = defineProps({
  reportId: { type: String, required: true },
})

const emit = defineEmits(['updated'])

const authStore = useAuthStore()
const isAdmin = computed(() => Boolean(authStore.isAdmin))

const loading = ref(false)
const report = ref(null)
const modules = ref([])
const selectedKey = ref('')
const drafts = reactive({})
const staleKeys = ref(new Set())
const changedKeys = ref(new Set())
const saving = ref(false)
const regenerating = ref(false)
const statusMessage = ref('')
const promptPane = ref(null)
const reportPane = ref(null)

const masterPrompt = computed(
  () => report.value?.user_prompt || report.value?.metadata?.user_prompt || '',
)

const reportTitle = computed(
  () =>
    report.value?.metadata?.title ||
    report.value?.filename ||
    'Generated Financial Report',
)

function narrative(section) {
  const c = section?.content
  if (typeof c === 'string') return c
  if (c && typeof c === 'object') return c.content || ''
  return ''
}

function keyPointsOf(section) {
  const c = section?.content
  if (c && typeof c === 'object') return c.key_points || []
  return []
}

function recommendationsOf(section) {
  const c = section?.content
  if (c && typeof c === 'object') return c.recommendations || []
  return []
}

function formatRec(rec) {
  if (typeof rec === 'string') return rec
  if (rec && typeof rec === 'object') return rec.action || rec.area || JSON.stringify(rec)
  return String(rec)
}

function moduleForSection(sectionKey, section) {
  const byId = section?.trace?.prompt_module_id
  if (byId) {
    const found = modules.value.find((m) => m.id === byId)
    if (found) return found
  }
  return modules.value.find((m) => (m.related_sections || []).includes(sectionKey)) || null
}

const pairedRows = computed(() => {
  const generated = report.value?.comprehensive_analysis || []
  const generatedByKey = new Map()
  generated.forEach((section, index) => {
    const key = section.section_key || section.key || `section_${index}`
    generatedByKey.set(key, section)
  })

  const expectedKeys =
    report.value?.report_options?.sections ||
    report.value?.metadata?.report_options?.sections ||
    []

  const orderedKeys = []
  for (const key of expectedKeys) {
    if (key && !orderedKeys.includes(key)) orderedKeys.push(key)
  }
  for (const key of generatedByKey.keys()) {
    if (!orderedKeys.includes(key)) orderedKeys.push(key)
  }

  // If nothing expected, fall back to generated order
  const keys = orderedKeys.length ? orderedKeys : [...generatedByKey.keys()]

  return keys.map((sectionKey) => {
    const section = generatedByKey.get(sectionKey) || null
    const module = moduleForSection(sectionKey, section)
    const libraryTitle = sectionKey.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    return {
      sectionKey,
      module,
      promptTitle: module?.name || `${section?.title || libraryTitle} Prompt`,
      reportTitle: section?.title || libraryTitle,
      reportNarrative: narrative(section),
      keyPoints: keyPointsOf(section),
      recommendations: recommendationsOf(section),
      trace: section?.trace || null,
      missing: !section,
    }
  })
})

const selectedPair = computed(() => {
  if (!selectedKey.value || selectedKey.value === '__master__') return null
  return pairedRows.value.find((p) => p.sectionKey === selectedKey.value) || null
})

function syncDrafts() {
  for (const pair of pairedRows.value) {
    if (pair.module && drafts[pair.sectionKey] === undefined) {
      drafts[pair.sectionKey] = pair.module.prompt_text || ''
    }
  }
  if (!selectedKey.value && pairedRows.value.length) {
    selectedKey.value = pairedRows.value[0].sectionKey
  }
}

async function selectSection(key, origin) {
  selectedKey.value = key
  await nextTick()
  const otherId = origin === 'prompt' ? `report-${key}` : `prompt-${key}`
  const el = document.getElementById(otherId)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

async function loadModules() {
  try {
    const resp = await api.getPromptModules({ include_archived: false })
    modules.value = resp.data?.prompt_modules || []
  } catch {
    modules.value = []
  }
}

async function loadReport() {
  if (!props.reportId) return
  loading.value = true
  try {
    const resp = await api.getReport(props.reportId)
    report.value = resp.data
    syncDrafts()
  } catch {
    statusMessage.value = 'Failed to load report.'
  } finally {
    loading.value = false
  }
}

async function saveSelected() {
  const pair = selectedPair.value
  if (!pair?.module || !isAdmin.value) return
  saving.value = true
  statusMessage.value = ''
  try {
    const resp = await api.updatePromptModule(pair.module.id, {
      prompt_text: drafts[pair.sectionKey],
      change_comment: `Edited ${pair.promptTitle} in split view`,
    })
    const updated = resp.data?.prompt_module
    modules.value = modules.value.map((m) => (m.id === updated.id ? updated : m))
    drafts[pair.sectionKey] = updated.prompt_text
    staleKeys.value = new Set([...staleKeys.value, pair.sectionKey])
    statusMessage.value = `Saved full prompt section “${pair.promptTitle}” (v${updated.version_current}). Click Update selected section to refresh the report.`
  } catch {
    statusMessage.value = 'Save failed — administrator access required.'
  } finally {
    saving.value = false
  }
}

async function regenerateSelected() {
  const pair = selectedPair.value
  if (!pair) return
  regenerating.value = true
  statusMessage.value = ''
  try {
    if (pair.module && isAdmin.value && drafts[pair.sectionKey] !== pair.module.prompt_text) {
      await saveSelected()
    }
    await api.regenerateReportSection(props.reportId, pair.sectionKey, {
      reason: 'full-pane section refinement',
      prompt: drafts[pair.sectionKey] || undefined,
    })
    await loadReport()
    changedKeys.value = new Set([...changedKeys.value, pair.sectionKey])
    const next = new Set(staleKeys.value)
    next.delete(pair.sectionKey)
    staleKeys.value = next
    selectedKey.value = pair.sectionKey
    statusMessage.value = `Updated report section “${pair.reportTitle}”.`
    emit('updated', pair.sectionKey)
  } catch (err) {
    statusMessage.value = err?.response?.data?.error || 'Section update failed.'
  } finally {
    regenerating.value = false
  }
}

watch(
  () => props.reportId,
  async () => {
    Object.keys(drafts).forEach((k) => delete drafts[k])
    await loadReport()
  },
)

watch(pairedRows, () => syncDrafts())

onMounted(async () => {
  await loadModules()
  await loadReport()
})

defineExpose({ reload: loadReport })
</script>
