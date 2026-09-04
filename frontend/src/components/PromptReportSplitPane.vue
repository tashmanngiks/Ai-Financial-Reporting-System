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
          <div class="flex items-center justify-between gap-2 mb-1">
            <h3 class="text-sm font-semibold text-gray-900">Master Analysis Prompt</h3>
            <button
              type="button"
              class="text-xs px-2 py-1 rounded bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50"
              :disabled="!masterEditor.trim() || savingMasterPrompt"
              @click.stop="saveMasterPromptToDataset"
            >
              {{ savingMasterPrompt ? 'Saving…' : 'Save to Dataset' }}
            </button>
          </div>
          <p class="text-[11px] text-gray-500 mb-2">
            Dataset-level context (section prompts below control each report block).
            <span class="text-emerald-700 font-medium">Edits auto-save to Dataset Analysis Prompt.</span>
          </p>
          <textarea
            id="master-analysis-prompt"
            name="master_analysis_prompt"
            class="w-full border border-gray-200 rounded p-2 font-mono text-xs leading-relaxed max-h-48 overflow-y-auto focus:ring-1 focus:ring-[#08AAC7] bg-white"
            v-model="masterEditor"
            rows="8"
            @click.stop
            @input="onMasterEdit"
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
            :id="`section-prompt-${pair.sectionKey}`"
            :name="`section_prompt_${pair.sectionKey}`"
            :value="drafts[pair.sectionKey] ?? ''"
            rows="8"
            class="w-full border border-gray-200 rounded p-2 font-mono text-xs leading-relaxed focus:ring-1 focus:ring-[#08AAC7] bg-white relative z-10"
            placeholder="Write the prompt instructions for this report section…"
            @click.stop
            @mousedown.stop
            @input="onSectionInput(pair.sectionKey, $event)"
            @focus="selectedKey = pair.sectionKey"
          />
          <p v-if="!(drafts[pair.sectionKey] || '').trim()" class="text-[11px] text-amber-700 mt-1">
            This section prompt is empty — paste or type instructions, then regenerate.
          </p>
          <p v-else-if="!pair.module" class="text-[11px] text-amber-700 mt-1">
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
            · {{ report?.data_period || (report?.metadata as Record<string, unknown>)?.period || '' }}
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
              <span
                v-if="sectionState(pair.sectionKey) === 'REGENERATING'"
                class="text-[11px] px-2 py-0.5 rounded bg-blue-100 text-blue-800"
              >Regenerating</span>
              <span
                v-else-if="sectionState(pair.sectionKey) === 'ERROR'"
                class="text-[11px] px-2 py-0.5 rounded bg-red-100 text-red-800"
              >Generation failed</span>
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
          <details v-if="versionHistory(pair).length" class="mt-4 rounded border border-gray-200 bg-gray-50 px-3 py-2">
            <summary class="cursor-pointer text-xs font-semibold uppercase tracking-wide text-gray-600">
              Version history
            </summary>
            <div class="mt-3">
              <DataTable
                :columns="versionHistoryColumns"
                :rows="versionHistoryRows(pair)"
                row-key="id"
                :page-size="5"
                empty-title="No version history."
                empty-message="Regenerate this section to create version records."
                caption="Prompt and report section version history"
              >
                <template #cell-version="{ value }">
                  <span class="font-medium tabular-nums">{{ formatVersion(value) }}</span>
                </template>
                <template #cell-section="{ value }">
                  <span>{{ value }}</span>
                </template>
                <template #cell-changed_by="{ value }">
                  <span>{{ value || 'System' }}</span>
                </template>
                <template #cell-change_date="{ value }">
                  <span class="tabular-nums">{{ formatDateTime(value) }}</span>
                </template>
                <template #cell-change_type="{ value }">
                  <span>{{ value || 'Update' }}</span>
                </template>
                <template #cell-status="{ row }">
                  <StatusBadge :status="row.status" :label="row.status_label" />
                </template>
                <template #cell-actions="{ row }">
                  <span class="text-xs text-slate-500">{{ row.actions_label }}</span>
                </template>
              </DataTable>
            </div>
          </details>
        </article>

        <p v-if="!pairedRows.length" class="text-sm text-gray-500 text-center py-12">
          No generated report sections yet.
        </p>
      </div>
    </div>

    <p v-if="statusMessage" class="px-4 py-2 text-xs border-t shrink-0" :class="errorMessage ? 'bg-red-50 text-red-700' : 'bg-gray-50 text-gray-600'">
      {{ statusMessage }}
    </p>

    <!-- Debug View Toggle -->
    <button
      type="button"
      class="px-4 py-2 text-xs border-t bg-gray-100 hover:bg-gray-200 text-gray-700"
      @click="showDebugView = !showDebugView"
    >
      {{ showDebugView ? 'Hide' : 'Show' }} Section Mapping Debug
    </button>

    <!-- Debug View -->
    <div v-if="showDebugView" class="px-4 py-3 border-t bg-gray-50 text-xs overflow-y-auto max-h-64">
      <div class="font-semibold mb-2">Section Mapping Validation</div>
      <div v-if="Array.isArray(mappingValidation.issues) && mappingValidation.issues.length" class="text-red-600 mb-2">
        <div class="font-medium">Issues:</div>
        <ul class="list-disc pl-4">
          <li v-for="(issue, idx) in mappingValidation.issues" :key="idx">{{ issue }}</li>
        </ul>
      </div>
      <div class="text-green-600 mb-2">
        Status: {{ mappingValidation.valid ? '✓ VALID' : '✗ INVALID' }}
        ({{ mappingValidation.synchronized_count }}/{{ mappingValidation.total_sections }} synchronized)
      </div>
      <div class="space-y-1">
        <div v-for="mapping in mappingValidation.mappings" :key="(mapping as SectionMapping).section_key"
             class="p-1 rounded" :class="{
               'bg-green-100': (mapping as SectionMapping).status === 'SYNCHRONIZED',
               'bg-yellow-100': (mapping as SectionMapping).status === 'MISMATCH',
               'bg-red-100': (mapping as SectionMapping).status === 'MISSING'
             }">
          <div class="font-medium">{{ (mapping as SectionMapping).section_title }}</div>
          <div class="text-gray-600">Key: {{ (mapping as SectionMapping).section_key }}</div>
          <div class="text-[10px]">
            Master: {{ (mapping as SectionMapping).has_master_prompt ? '✓' : '✗' }} |
            Dataset: {{ (mapping as SectionMapping).has_dataset_prompt ? '✓' : '✗' }} |
            Editor: {{ (mapping as SectionMapping).has_editor_prompt ? '✓' : '✗' }} |
            Report: {{ (mapping as SectionMapping).has_report_content ? '✓' : '✗' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { api } from '@/services/api'
import DataTable from '@/components/DataTable.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import { formatDateTime, formatVersion } from '@/utils/tableFormat'

const props = defineProps({
  reportId: { type: String, required: true },
})

const emit = defineEmits(['updated'])

type AnyRecord = Record<string, unknown>

interface PromptModuleRecord {
  id: string | number
  name?: string
  prompt_text?: string
  version_current?: number
  related_sections?: string[]
}

interface GeneratedPair {
  sectionKey: string
  module: PromptModuleRecord | null
  promptTitle: string
  reportTitle: string
  reportNarrative: string
  keyPoints: unknown[]
  recommendations: unknown[]
  trace: AnyRecord | null
  missing: boolean
}

const versionHistoryColumns = [
  { key: 'version', label: 'Version', width: '5rem' },
  { key: 'section', label: 'Section', wrap: true, width: '10rem' },
  { key: 'changed_by', label: 'Changed By', width: '8rem' },
  { key: 'change_date', label: 'Change Date', width: '10rem' },
  { key: 'change_type', label: 'Change Type', width: '9rem' },
  { key: 'status', label: 'Status', width: '7rem' },
  { key: 'actions', label: 'Actions', width: '8rem' },
]

const loading = ref(false)
const report = ref<AnyRecord | null>(null)
const modules = ref<PromptModuleRecord[]>([])
const selectedKey = ref<string>('')
const drafts = reactive<Record<string, string>>({})
const baselines = reactive<Record<string, string>>({})
const dirtyKeys = ref<Set<string>>(new Set())
const changedKeys = ref<Set<string>>(new Set())
const regenerating = ref(false)
const regeneratingKey = ref<string>('')
const regeneratingLabel = ref('')
const statusMessage = ref('')
const errorMessage = ref('')
const savingMasterPrompt = ref(false)
const sectionStates = reactive<Record<string, { state: string; error: string }>>({})
const showDebugView = ref(false)
const mappingValidation = ref<Record<string, unknown>>({})

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
  for (const k of keys) {
    const key = String(k).trim()
    if (!key) continue
    const promptText = String(draftMap[key] ?? '').replace(/\s+$/, '')
    parts.push(`[SECTION:${key}]\n${promptText}\n[/SECTION]`)
  }
  return parts.join('\n\n')
}

/** Replace only one section block inside the master prompt (preserves other sections + preamble). */
function upsertSectionInMaster(master: string, sectionKey: string, body: string) {
  const key = String(sectionKey).trim()
  const block = `[SECTION:${key}]\n${String(body || '').replace(/\s+$/, '')}\n[/SECTION]`
  const re = new RegExp(`\\[SECTION:${escapeRegExp(key)}\\][\\s\\S]*?\\[/SECTION\\]`, 'i')
  if (re.test(master || '')) {
    return (master || '').replace(re, () => block)
  }
  const trimmed = (master || '').replace(/\s+$/, '')
  return trimmed ? `${trimmed}\n\n${block}` : block
}

const reportTitle = computed(
  () =>
    (report.value?.metadata as Record<string, unknown>)?.title ||
    report.value?.filename ||
    'Generated Financial Report',
)

function narrative(section: AnyRecord | null) {
  const c = section?.content
  if (typeof c === 'string') return c
  if (c && typeof c === 'object') return (c as Record<string, unknown>).content || ''
  return ''
}

function keyPointsOf(section: AnyRecord | null) {
  const c = section?.content
  if (c && typeof c === 'object') return (c as Record<string, unknown>).key_points || []
  return []
}

function recommendationsOf(section: AnyRecord | null) {
  const c = section?.content
  if (c && typeof c === 'object') return (c as Record<string, unknown>).recommendations || []
  return []
}

function formatRec(rec: unknown) {
  if (typeof rec === 'string') return rec
  if (rec && typeof rec === 'object') return (rec as Record<string, unknown>).action || (rec as Record<string, unknown>).area || JSON.stringify(rec)
  return String(rec)
}

function formatTimestamp(value: string | null | undefined) {
  if (!value) return 'Unknown time'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return String(value)
  }
}

function moduleForSection(sectionKey: string, section: AnyRecord | null) {
  const trace = section?.trace as Record<string, unknown> | null
  const byId = trace?.prompt_module_id
  if (byId) {
    const found = modules.value.find((m) => String(m.id) === String(byId))
    if (found) return found
  }

  // Try exact match first
  const exactMatch = modules.value.find((m) => (m.related_sections || []).includes(sectionKey))
  if (exactMatch) return exactMatch

  // Try normalized match (handle underscores, hyphens, spaces)
  const normalizedKey = sectionKey.toLowerCase().replace(/[_\s-]/g, '')
  const normalizedMatch = modules.value.find((m) =>
    (m.related_sections || []).some((rs: string) =>
      rs.toLowerCase().replace(/[_\s-]/g, '') === normalizedKey
    )
  )
  if (normalizedMatch) return normalizedMatch

  // Try matching by name as fallback
  const nameMatch = modules.value.find((m) =>
    m.name?.toLowerCase().replace(/[_\s-]/g, '') === normalizedKey
  )

  return nameMatch || null
}

interface SectionMapping {
  section_key: string
  section_title: string
  section_order: number
  has_master_prompt: boolean
  has_dataset_prompt: boolean
  has_editor_prompt: boolean
  has_report_content: boolean
  status: 'SYNCHRONIZED' | 'MISMATCH' | 'MISSING' | 'DUPLICATE'
}

function validateSectionMapping(): Record<string, unknown> {
  const reportSections = Array.isArray(report.value?.comprehensive_analysis)
    ? report.value?.comprehensive_analysis
    : []
  const sectionKeys = new Set<string>()
  const mappings: SectionMapping[] = []
  const issues: string[] = []

  // Collect all section keys from report
  reportSections.forEach((section: unknown, index: number) => {
    const sectionRecord = section as Record<string, unknown>
    const key = String(sectionRecord.section_key || sectionRecord.key || `section_${index}`)
    if (sectionKeys.has(key)) {
      issues.push(`Duplicate section key: ${key}`)
    }
    sectionKeys.add(key)

    const title = String(sectionRecord.title || 'Untitled')
    const content = sectionRecord.content as Record<string, unknown> | string | null
    const hasContent = Boolean(content)

    // Check if this section exists in master prompt
    const hasMaster = masterEditor.value.includes(`[SECTION:${key}]`) ||
                      masterEditor.value.toLowerCase().includes(title.toLowerCase())

    // Check if this section exists in drafts
    const hasEditor = Boolean(String(drafts[key] || '').trim())

    mappings.push({
      section_key: key,
      section_title: title,
      section_order: index,
      has_master_prompt: hasMaster,
      has_dataset_prompt: hasMaster, // Assuming same as master for now
      has_editor_prompt: hasEditor,
      has_report_content: hasContent,
      status: (hasMaster && hasEditor && hasContent) ? 'SYNCHRONIZED' : 'MISMATCH'
    })
  })

  // Check for orphan prompts in drafts
  Object.keys(drafts).forEach((key) => {
    if (!sectionKeys.has(key) && String(drafts[key] || '').trim()) {
      issues.push(`Orphan prompt for section: ${key}`)
    }
  })

  return {
    valid: issues.length === 0,
    issues,
    mappings,
    total_sections: reportSections.length,
    synchronized_count: mappings.filter(m => m.status === 'SYNCHRONIZED').length
  }
}

function normalizeSectionKey(value: string, fallback = 'section') {
  const normalized = String(value || fallback)
    .trim()
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
  return normalized || fallback
}

const pairedRows = computed<GeneratedPair[]>(() => {
  const generated: AnyRecord[] = Array.isArray(report.value?.comprehensive_analysis)
    ? report.value?.comprehensive_analysis
    : []
  const generatedByKey = new Map<string, AnyRecord>()
  generated.forEach((section: AnyRecord, index: number) => {
    const explicitKey = section?.section_key || section?.key
    let sectionKey = ''
    if (explicitKey && String(explicitKey).trim()) {
      sectionKey = String(explicitKey).trim()
    } else {
      const title = section?.title || section?.heading || `Section ${index + 1}`
      sectionKey = normalizeSectionKey(String(title), `section_${index}`)
    }
    if (!generatedByKey.has(sectionKey)) {
      generatedByKey.set(sectionKey, section)
    }
  })

  const reportOptions = (report.value?.report_options || (report.value?.metadata as AnyRecord | undefined)?.report_options || {}) as AnyRecord
  const expectedKeys = Array.isArray(reportOptions.sections)
    ? reportOptions.sections.map((k: unknown) => String(k).trim()).filter(Boolean)
    : []

  const orderedKeys: string[] = []
  for (const key of expectedKeys) {
    if (!orderedKeys.includes(key)) orderedKeys.push(key)
  }
  for (const key of generatedByKey.keys()) {
    if (!orderedKeys.includes(key)) orderedKeys.push(key)
  }

  const keys = orderedKeys.length ? orderedKeys : [...generatedByKey.keys()]

    return keys.map((sectionKey) => {
    const section = generatedByKey.get(sectionKey) || null
    const module = moduleForSection(sectionKey, section)
    const libraryTitle = normalizeSectionKey(sectionKey, 'section').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
    const sectionTitle = section?.title ? String(section.title) : libraryTitle

    return {
      sectionKey,
      module,
      promptTitle: module?.name || `${sectionTitle} Prompt`,
      reportTitle: sectionTitle,
      reportNarrative: String(narrative(section) || ''),
      keyPoints: keyPointsOf(section) as unknown[],
      recommendations: recommendationsOf(section) as unknown[],
      trace: (section?.trace as AnyRecord | null) || null,
      missing: !section,
    } satisfies GeneratedPair
  })
})

const selectedPair = computed<GeneratedPair | null>(() => {
  if (!selectedKey.value || selectedKey.value === '__master__') return null
  return pairedRows.value.find((p) => p.sectionKey === selectedKey.value) || null
})

function markDirty(sectionKey: string) {
  const current = String(drafts[sectionKey] ?? '')
  const baseline = String(baselines[sectionKey] ?? '')
  const dirty = new Set(dirtyKeys.value)
  if (current.trim() !== baseline.trim()) dirty.add(sectionKey)
  else dirty.delete(sectionKey)
  dirtyKeys.value = dirty
}

function onSectionInput(sectionKey: string, event: Event) {
  const target = event.target as HTMLTextAreaElement | null
  const value = target ? target.value : ''
  drafts[sectionKey] = value
  markDirty(sectionKey)

  // Update only this section inside the master prompt (do not rebuild all sections).
  // Keep the flag set until after the watcher flush so edits are not overwritten.
  syncingFromModules.value = true
  masterEditor.value = upsertSectionInMaster(masterEditor.value, sectionKey, value)
  void nextTick(() => {
    syncingFromModules.value = false
  })
}

function onMasterEdit() {
  try {
    errorMessage.value = ''
    // Debounce saving to avoid excessive API calls
    if (masterEditTimeout) {
      clearTimeout(masterEditTimeout)
    }
    masterEditTimeout = setTimeout(() => {
      saveMasterPromptToDataset()
    }, 2000) // Save after 2 seconds of no edits
  } catch (error: unknown) {
    console.error('Error editing master prompt:', error)
    errorMessage.value = 'Failed to update master prompt. Please try again.'
  }
}

let masterEditTimeout: ReturnType<typeof setTimeout> | null = null

async function saveMasterPromptToDataset() {
  if (!masterEditor.value.trim()) {
    return
  }

  savingMasterPrompt.value = true
  try {
    statusMessage.value = 'Saving master prompt to Dataset Analysis Prompt...'
    const response = await api.saveMasterPromptToDatasetPrompt(props.reportId, masterEditor.value)

    if (response.data?.success) {
      statusMessage.value = response.data?.message || 'Master prompt saved successfully'
      errorMessage.value = ''
      console.log('Master prompt saved to Dataset Analysis Prompt:', response.data)
    } else {
      throw new Error(response.data?.error || 'Failed to save master prompt')
    }
  } catch (error: unknown) {
    console.error('Error saving master prompt to dataset:', error)
    const errorMsg = (error as Record<string, unknown>)?.response?.data?.error || (error as Error)?.message || 'Failed to save master prompt'
    statusMessage.value = errorMsg
    errorMessage.value = errorMsg
  } finally {
    savingMasterPrompt.value = false
  }
}

function canRegenerate(pair: GeneratedPair) {
  if (!pair?.sectionKey) return false
  if (sectionState(pair.sectionKey) === 'REGENERATING') return false
  if (regenerating.value) return false
  return Boolean(String(drafts[pair.sectionKey] || '').trim())
}

function sectionState(sectionKey: string) {
  return sectionStates[sectionKey]?.state || (dirtyKeys.value.has(sectionKey) ? 'DIRTY' : 'UNCHANGED')
}

function setSectionState(sectionKey: string, state: string, error = '') {
  sectionStates[sectionKey] = { state, error }
}

function versionHistory(pair: GeneratedPair) {
  const reportData = report.value as AnyRecord | null
  const versions = (reportData?.section_versions as AnyRecord | undefined)?.[pair.sectionKey]
  if (Array.isArray(versions)) {
    return [...versions].sort(
      (a: AnyRecord, b: AnyRecord) => Number(b?.version_number || 0) - Number(a?.version_number || 0),
    )
  }
  const history = (reportData?.section_history as AnyRecord | undefined)?.[pair.sectionKey]
  return Array.isArray(history) ? history : []
}

function versionHistoryRows(pair: GeneratedPair) {
  return versionHistory(pair).map((version: AnyRecord, index: number) => {
    const isCurrent = Boolean(version.is_current) || index === 0
    const status = isCurrent ? 'current' : String(version.generation_status || 'archived')
    return {
      id: String(version.id || `${pair.sectionKey}-${version.version_number || index}`),
      version: version.version_number || index + 1,
      section: pair.reportTitle || pair.promptTitle || pair.sectionKey,
      changed_by: version.generated_by || version.created_by || version.changed_by || 'System',
      change_date: version.generated_at || version.created_at || version.change_date,
      change_type: version.generation_reason || version.change_type || 'Section update',
      status,
      status_label: isCurrent ? 'Current' : String(version.generation_status || 'Archived').replace(/^\w/, (c: string) => c.toUpperCase()),
      actions_label: isCurrent ? 'Active version' : 'Historical',
    }
  })
}

function syncDrafts() {
  try {
    const keys = pairedRows.value.map((p) => p.sectionKey)
    const originalMaster = masterEditor.value || ''
    const extracted = parseMasterPromptForKeys(originalMaster, keys)

    for (const pair of pairedRows.value) {
      const key = pair.sectionKey
      if (dirtyKeys.value.has(key)) {
        continue
      }

      const fromMaster = extracted[key]
      let promptText = ''
      if (typeof fromMaster === 'string' && fromMaster.trim()) {
        promptText = fromMaster.trim()
      } else if (pair.module?.prompt_text?.trim()) {
        promptText = String(pair.module.prompt_text).trim()
      }

      // Always initialize every section key so every left editor is bound and editable.
      drafts[key] = promptText
      baselines[key] = promptText
      setSectionState(key, 'UNCHANGED')
    }

    if (!selectedKey.value && pairedRows.value.length) {
      selectedKey.value = pairedRows.value[0]!.sectionKey
    }

    mappingValidation.value = validateSectionMapping()
  } catch (error: unknown) {
    console.error('Error syncing drafts:', error)
    errorMessage.value = 'Failed to sync prompts. Please refresh the page.'
  }
}

watch(
  masterEditor,
  () => {
    if (syncingFromModules.value) return
    // Only decompose master → section editors when the user edits the master textarea.
    const keys = pairedRows.value.map((p) => p.sectionKey)
    const extracted = parseMasterPromptForKeys(masterEditor.value || '', keys)
    for (const key of keys) {
      const extractedText = extracted[key]
      if (typeof extractedText === 'string') {
        drafts[key] = extractedText.trim()
        markDirty(key)
      }
    }
  },
  { flush: 'sync' },
)

async function selectSection(key: string, origin: 'prompt' | 'report') {
  selectedKey.value = key
  await nextTick()
  const otherId = origin === 'prompt' ? `report-${key}` : `prompt-${key}`
  document.getElementById(otherId)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

async function loadModules() {
  try {
    const resp = await api.getPromptModules({ include_archived: false })
    modules.value = resp.data?.prompt_modules || []
  } catch (error: unknown) {
    console.error('Error loading modules:', error)
    modules.value = []
  }
}

async function loadReport() {
  if (!props.reportId) return
  loading.value = true
  errorMessage.value = ''
  try {
    const resp = await api.getReport(props.reportId)
    report.value = resp.data as AnyRecord

    // Load the master prompt without treating it as a user edit of the master textarea.
    const userPrompt = resp.data?.user_prompt || (resp.data as Record<string, unknown>)?.metadata?.user_prompt || ''
    syncingFromModules.value = true
    masterEditor.value = String(userPrompt)
    await nextTick()
    syncingFromModules.value = false

    console.log('Loaded report with user_prompt length:', userPrompt.length)

    // Log the actual section keys in the report for debugging
    const sections = Array.isArray(resp.data?.comprehensive_analysis)
      ? resp.data?.comprehensive_analysis
      : []
    const sectionKeys = sections.map((s: unknown, idx: number) => {
      const sectionRecord = s as Record<string, unknown>
      return {
        key: sectionRecord.section_key || sectionRecord.key,
        title: sectionRecord.title,
        index: idx
      }
    })
    console.log('Report sections:', JSON.stringify(sectionKeys, null, 2))

    // Clear dirty state from any prior report, then hydrate every section editor.
    dirtyKeys.value = new Set()
    syncDrafts()
    console.log(
      'Section editors ready:',
      pairedRows.value.map((p) => `${p.sectionKey}:${String(drafts[p.sectionKey] || '').length}`),
    )
  } catch (error: unknown) {
    console.error('Error loading report:', error)
    statusMessage.value = 'Failed to load report.'
    errorMessage.value = 'Failed to load report. Please try again.'
  } finally {
    loading.value = false
  }
}

async function regenerateOne(pair: GeneratedPair) {
  if (!pair?.sectionKey || regenerating.value) return
  if (!canRegenerate(pair)) {
    const reason = !drafts[pair.sectionKey]?.trim() ? 'Prompt is empty' : 'Section already up to date'
    setSectionState(pair.sectionKey, 'ERROR', reason)
    errorMessage.value = reason
    statusMessage.value = reason
    return
  }

  regenerating.value = true
  regeneratingKey.value = pair.sectionKey
  regeneratingLabel.value = pair.reportTitle
  setSectionState(pair.sectionKey, 'REGENERATING')
  errorMessage.value = ''
  statusMessage.value = `Regenerating "${pair.reportTitle}" only…`

  try {
    // Use the edited section prompt to ensure accurate correspondence
    const sectionPrompt = String(drafts[pair.sectionKey] || '').trim()

    console.log('Regenerating section:', pair.sectionKey, 'with prompt length:', sectionPrompt.length)

    const response = await api.regenerateReportSection(props.reportId, pair.sectionKey, {
      reason: pair.missing ? 'missing section generation' : 'edited prompt section regeneration',
      prompt: sectionPrompt,
      force: true,
    })

    if (response.data?.error) {
      throw new Error(response.data.error)
    }

    await loadReport()
    const draftValue = drafts[pair.sectionKey] ?? ''
    const draftStr = typeof draftValue === 'string' ? draftValue : ''
    baselines[pair.sectionKey] = draftStr
    drafts[pair.sectionKey] = draftStr
    const dirty = new Set(dirtyKeys.value)
    dirty.delete(pair.sectionKey)
    dirtyKeys.value = dirty
    changedKeys.value = new Set([...changedKeys.value, pair.sectionKey])
    setSectionState(pair.sectionKey, 'GENERATED')
    selectedKey.value = pair.sectionKey
    statusMessage.value = `Successfully updated "${pair.reportTitle}". Other sections were left unchanged.`
    errorMessage.value = ''
    emit('updated', pair.sectionKey)
  } catch (err: unknown) {
    const errorData = (err as Record<string, unknown>)?.response?.data
    const errorMsg = errorData?.error || (err as Error)?.message || 'Section regeneration failed. Please try again.'
    const errorDetails = errorData ? JSON.stringify(errorData) : 'No additional details'

    statusMessage.value = errorMsg
    errorMessage.value = errorMsg
    setSectionState(pair.sectionKey, 'ERROR', errorMsg)

    console.error('Regeneration error:', errorMsg)
    console.error('Full error response:', errorDetails)
    console.error('Section key sent:', pair.sectionKey)
    console.error('Prompt length:', String(drafts[pair.sectionKey] || '').length)
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
    Object.keys(sectionStates).forEach((k) => delete sectionStates[k])
    dirtyKeys.value = new Set()
    changedKeys.value = new Set()
    await loadReport()
  },
)

// Sync drafts once when the section list first becomes available (not on every reactive tweak).
watch(
  () => pairedRows.value.map((p) => p.sectionKey).join('|'),
  (keyList, previous) => {
    if (!keyList || keyList === previous) return
    syncDrafts()
  },
)

onMounted(async () => {
  await loadModules()
  await loadReport()
})

defineExpose({ reload: loadReport })
</script>
