<template>
  <div class="flex flex-col border border-gray-200 rounded-xl overflow-hidden bg-white min-h-[75vh]">
    <!-- Headers / actions -->
    <div class="grid grid-cols-1 lg:grid-cols-2 border-b bg-gray-50 shrink-0">
      <div class="px-4 py-2.5 border-r border-gray-200 flex flex-wrap items-center justify-between gap-2">
        <div>
          <span class="text-[11px] font-semibold uppercase tracking-wider text-[#056F80]">
            Source · Full Prompt
          </span>
          <p class="text-[11px] text-gray-500 mt-0.5">
            Edit any section prompt, then regenerate only that section.
          </p>
        </div>
        <button
          type="button"
          class="text-xs px-3 py-1.5 rounded bg-[#08AAC7] text-white hover:bg-[#0691A8] disabled:opacity-50"
          :disabled="!dirtyKeys.size || regenerating"
          @click="regenerateChangedOnly"
        >
          {{ regenerating
            ? `Updating ${regeneratingLabel}…`
            : `Regenerate changed only (${dirtyKeys.size})` }}
        </button>
      </div>
      <div class="px-4 py-2.5 hidden lg:flex items-center justify-between gap-2">
        <span class="text-[11px] font-semibold uppercase tracking-wider text-emerald-700">
          Output · Full Generated Report
        </span>
        <span v-if="selectedPair" class="text-[11px] text-gray-500 truncate max-w-[55%]">
          Selected: {{ selectedPair.reportTitle }}
        </span>
      </div>
    </div>

    <div v-if="loading" class="flex-1 flex items-center justify-center py-16 text-gray-500 text-sm">
      Loading full prompt and report…
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 flex-1 min-h-0" style="height: 70vh">
      <!-- LEFT: editable prompts -->
      <div class="border-r border-gray-200 overflow-y-auto p-4 space-y-4 bg-white">
        <section
          class="rounded-lg border p-3"
          :class="selectedKey === '__master__' ? 'border-[#08AAC7] bg-[#08AAC7]/5' : 'border-gray-200'"
          @click="selectedKey = '__master__'"
        >
          <h3 class="text-sm font-semibold text-gray-900 mb-1">Master Analysis Prompt</h3>
          <p class="text-[11px] text-gray-500 mb-2">
            Dataset-level context (section prompts below control each report block).
          </p>
          <textarea
            class="w-full border border-gray-200 rounded p-2 font-mono text-xs leading-relaxed max-h-48 overflow-y-auto focus:ring-1 focus:ring-[#08AAC7] bg-white"
            :readonly="!isAdmin"
            v-model="masterEditor"
            rows="8"
            @click.stop
          />
        </section>

        <section
          v-for="pair in pairedRows"
          :id="`prompt-${pair.sectionKey}`"
          :key="'p-' + pair.sectionKey"
          class="rounded-lg border p-3 transition-colors"
          :class="selectedKey === pair.sectionKey
            ? 'border-[#08AAC7] bg-[#08AAC7]/10 ring-1 ring-[#08AAC7]/40'
            : dirtyKeys.has(pair.sectionKey)
              ? 'border-amber-300 bg-amber-50/40'
              : 'border-gray-200 hover:border-gray-300'"
          @click="selectSection(pair.sectionKey, 'prompt')"
        >
          <div class="flex items-center justify-between gap-2 mb-2">
            <div>
              <h3 class="text-sm font-semibold text-gray-900">{{ pair.promptTitle }}</h3>
              <p class="text-[11px] text-gray-500">
                <span v-if="pair.module">v{{ pair.module.version_current }}</span>
                <span v-if="dirtyKeys.has(pair.sectionKey)" class="text-amber-700 font-medium"> · edited</span>
                <span v-else-if="changedKeys.has(pair.sectionKey)" class="text-emerald-700"> · regenerated</span>
              </p>
            </div>
            <button
              type="button"
              class="text-xs px-2 py-1 rounded bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 shrink-0"
              :disabled="regenerating || !canRegenerate(pair)"
              @click.stop="regenerateOne(pair)"
            >
              {{ regeneratingKey === pair.sectionKey ? 'Updating…' : 'Regenerate section' }}
            </button>
          </div>

          <textarea
            v-model="drafts[pair.sectionKey]"
            rows="8"
            class="w-full border border-gray-200 rounded p-2 font-mono text-xs leading-relaxed focus:ring-1 focus:ring-[#08AAC7] bg-white"
            placeholder="Write the prompt instructions for this report section…"
            @click.stop
            @input="onDraftEdit(pair.sectionKey)"
            @focus="selectSection(pair.sectionKey, 'prompt')"
          />
          <p v-if="!pair.module" class="text-[11px] text-amber-700 mt-1">
            No saved module yet — regenerating will still use the text above for this section only.
          </p>
        </section>
      </div>

      <!-- RIGHT: full report -->
      <div class="overflow-y-auto p-4 space-y-6 bg-white">
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
            : dirtyKeys.has(pair.sectionKey)
              ? 'border-amber-200 bg-amber-50/30'
              : 'border-transparent hover:border-gray-200'"
          @click="selectSection(pair.sectionKey, 'report')"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <div>
              <h3 class="text-base font-semibold text-gray-900">{{ pair.reportTitle }}</h3>
              <p v-if="pair.trace" class="text-[11px] text-gray-500">
                From {{ pair.trace.prompt_module_name || 'prompt' }}
                <span v-if="pair.trace.prompt_module_version">· v{{ pair.trace.prompt_module_version }}</span>
              </p>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <span
                v-if="dirtyKeys.has(pair.sectionKey)"
                class="text-[11px] px-2 py-0.5 rounded bg-amber-100 text-amber-800"
              >Prompt edited</span>
              <span
                v-if="changedKeys.has(pair.sectionKey)"
                class="text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800"
              >Updated</span>
              <button
                type="button"
                class="text-xs px-2 py-1 rounded border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50"
                :disabled="regenerating || !canRegenerate(pair)"
                @click.stop="regenerateOne(pair)"
              >
                {{ regeneratingKey === pair.sectionKey ? 'Updating…' : 'Regen' }}
              </button>
            </div>
          </div>
          <div class="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
            <template v-if="pair.missing">
              <span class="text-amber-700">
                This section is missing. Edit the prompt on the left, then click Regenerate section.
              </span>
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

<script setup lang="ts">
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
const baselines = reactive({})
const dirtyKeys = ref(new Set())
const changedKeys = ref(new Set())
const regenerating = ref(false)
const regeneratingKey = ref('')
const regeneratingLabel = ref('')
const statusMessage = ref('')

const masterEditor = ref('')
const syncingFromModules = ref(false)

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function parseMasterPromptForKeys(text: string, keys: string[]) {
  const mapping: Record<string, string> = {}
  const safeText = text || ''
  for (const k of keys || []) {
    const key = String(k).trim()
    if (!key) continue
    const re = new RegExp(`\\[SECTION:${escapeRegExp(key)}\\]([\\s\\S]*?)\\[/SECTION\\]`, 'm')
    const match = safeText.match(re)
    if (match && typeof match[1] === 'string') {
      const extracted = match[1].replace(/\s+$/, '')
      if (extracted.trim()) mapping[key] = extracted
    }
  }
  return mapping
}

function composeMasterFromDrafts(keys: string[], draftMap: Record<string, string>) {
  const parts: string[] = []
  for (const k of keys || []) {
    const key = String(k).trim()
    if (!key) continue
    const promptText = (draftMap[key] ?? '').replace(/\s+$/, '')
    parts.push(`[SECTION:${key}]\n${promptText}\n[/SECTION]`)
  }
  return parts.join('\n\n')
}

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

function markDirty(sectionKey) {
  const current = drafts[sectionKey] ?? ''
  const baseline = baselines[sectionKey] ?? ''
  const next = new Set(dirtyKeys.value)
  if (current.trim() !== baseline.trim()) next.add(sectionKey)
  else next.delete(sectionKey)
  dirtyKeys.value = next
}

function onDraftEdit(sectionKey) {
  markDirty(sectionKey)
  // Keep master prompt synchronized (canonical marker format) when user edits a section prompt.
  // This is the bidirectional link: module edits -> master prompt.
  const keys = pairedRows.value.map((p) => p.sectionKey)
  syncingFromModules.value = true
  masterEditor.value = composeMasterFromDrafts(keys, drafts)
  syncingFromModules.value = false
}

function canRegenerate(pair) {
  return Boolean(pair?.sectionKey && (drafts[pair.sectionKey] || '').trim())
}

function syncDrafts() {
  const keys = pairedRows.value.map((p) => p.sectionKey)

  // Decompose master prompt into per-section editor content.
  const extracted = parseMasterPromptForKeys(masterEditor.value || '', keys)

  for (const pair of pairedRows.value) {
    const key = pair.sectionKey
    const fromMaster = extracted[key]
    const fallback = pair.module?.prompt_text || ''
    const next = typeof fromMaster === 'string' ? fromMaster : fallback

    drafts[key] = next
    baselines[key] = next
  }

  // Canonicalize the master prompt so it always contains all section markers.
  syncingFromModules.value = true
  masterEditor.value = composeMasterFromDrafts(keys, drafts)
  syncingFromModules.value = false

  if (!selectedKey.value && pairedRows.value.length) {
    selectedKey.value = pairedRows.value[0].sectionKey
  }
}

watch(
  masterEditor,
  () => {
    if (syncingFromModules.value) return
    const keys = pairedRows.value.map((p) => p.sectionKey)
    const extracted = parseMasterPromptForKeys(masterEditor.value || '', keys)
    for (const key of keys) {
      if (typeof extracted[key] === 'string') {
        drafts[key] = extracted[key]
        // markDirty uses baselines; we reuse it to keep dirty highlights correct.
        markDirty(key)
      }
    }
  },
  { deep: false },
)

async function selectSection(key, origin) {
  selectedKey.value = key
  await nextTick()
  const otherId = origin === 'prompt' ? `report-${key}` : `prompt-${key}`
  document.getElementById(otherId)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
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
    masterEditor.value =
      resp.data?.user_prompt || resp.data?.metadata?.user_prompt || resp.data?.metadata?.user_prompt || ''
    syncDrafts()
  } catch {
    statusMessage.value = 'Failed to load report.'
  } finally {
    loading.value = false
  }
}

async function persistModuleIfPossible(pair) {
  if (!pair.module || !isAdmin.value) return null
  try {
    const resp = await api.updatePromptModule(pair.module.id, {
      prompt_text: drafts[pair.sectionKey],
      change_comment: `Edited ${pair.promptTitle} before section regeneration`,
    })
    const updated = resp.data?.prompt_module
    if (updated) {
      modules.value = modules.value.map((m) => (m.id === updated.id ? updated : m))
      baselines[pair.sectionKey] = updated.prompt_text
      drafts[pair.sectionKey] = updated.prompt_text
    }
    return updated
  } catch {
    // Non-fatal: regeneration can still use the draft prompt text
    return null
  }
}

async function regenerateOne(pair) {
  if (!pair?.sectionKey || regenerating.value) return
  regenerating.value = true
  regeneratingKey.value = pair.sectionKey
  regeneratingLabel.value = pair.reportTitle
  statusMessage.value = `Regenerating “${pair.reportTitle}” only…`
  try {
    await persistModuleIfPossible(pair)
    await api.regenerateReportSection(props.reportId, pair.sectionKey, {
      reason: 'edited prompt section regeneration',
      prompt: drafts[pair.sectionKey],
    })
    await loadReport()
    baselines[pair.sectionKey] = drafts[pair.sectionKey]
    const dirty = new Set(dirtyKeys.value)
    dirty.delete(pair.sectionKey)
    dirtyKeys.value = dirty
    changedKeys.value = new Set([...changedKeys.value, pair.sectionKey])
    selectedKey.value = pair.sectionKey
    statusMessage.value = `Updated only “${pair.reportTitle}”. Other sections were left unchanged.`
    emit('updated', pair.sectionKey)
  } catch (err) {
    statusMessage.value = err?.response?.data?.error || 'Section regeneration failed.'
  } finally {
    regenerating.value = false
    regeneratingKey.value = ''
    regeneratingLabel.value = ''
  }
}

async function regenerateChangedOnly() {
  const keys = [...dirtyKeys.value]
  if (!keys.length) {
    statusMessage.value = 'No edited prompts to regenerate.'
    return
  }
  for (const key of keys) {
    const pair = pairedRows.value.find((p) => p.sectionKey === key)
    if (pair) await regenerateOne(pair)
  }
  statusMessage.value = `Finished regenerating ${keys.length} edited section(s).`
}

watch(
  () => props.reportId,
  async () => {
    Object.keys(drafts).forEach((k) => delete drafts[k])
    Object.keys(baselines).forEach((k) => delete baselines[k])
    dirtyKeys.value = new Set()
    changedKeys.value = new Set()
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
