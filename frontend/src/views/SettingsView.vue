<template>
  <div class="p-6 space-y-6">
    <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <p class="text-sm text-gray-600 mt-1">
          Configure automatic retention and manage generated reports in a structured table view.
        </p>
      </div>
      <div
        v-if="statusMessage"
        class="text-sm px-3 py-2 rounded-lg border"
        :class="statusError ? 'bg-red-50 text-red-700 border-red-200' : 'bg-emerald-50 text-emerald-800 border-emerald-200'"
        role="status"
      >
        {{ statusMessage }}
      </div>
    </div>

    <section class="card">
      <div class="card-header">
        <h2 class="text-lg font-semibold text-gray-900">Automatic Data Retention</h2>
      </div>
      <div class="card-body space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Retention Period</span>
            <input
              v-model.number="retentionDays"
              type="number"
              min="1"
              max="3650"
              name="retention_days"
              class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#08AAC7]"
            />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Time Unit</span>
            <select
              v-model="retentionUnit"
              name="retention_unit"
              class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#08AAC7]"
            >
              <option value="days">Days</option>
              <option value="weeks">Weeks</option>
              <option value="months">Months</option>
            </select>
          </label>
          <label class="inline-flex items-center gap-2 mt-6">
            <input v-model="autoCleanup" type="checkbox" name="auto_cleanup" class="rounded border-gray-300 text-[#08AAC7] focus:ring-[#08AAC7]" />
            <span class="text-sm text-gray-700">Enable automatic cleanup</span>
          </label>
        </div>

        <div class="flex gap-3 flex-wrap">
          <button class="btn btn-primary" :disabled="savingRetention" @click="saveRetentionSettings">
            <span v-if="savingRetention">Saving...</span>
            <span v-else>Save Settings</span>
          </button>
          <button class="btn btn-secondary" :disabled="savingRetention" @click="resetRetentionDefaults">
            Reset to Default
          </button>
          <button class="btn" :disabled="runningCleanup" @click="runCleanupNow">
            <span v-if="runningCleanup">Cleaning...</span>
            <span v-else>Run Cleanup Now</span>
          </button>
        </div>

        <p v-if="cleanupPreview" class="text-sm text-gray-600">
          Preview: {{ cleanupPreview.result?.total_deleted ?? 0 }} items would be removed with this policy.
        </p>
      </div>
    </section>

    <section class="card">
      <div class="card-header flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Report Management</h2>
          <p class="text-sm text-gray-500 mt-0.5">
            Each row is one report. Actions stay in the Actions column for that report only.
          </p>
        </div>
        <button class="btn btn-secondary" :disabled="loadingReports" @click="refreshReports">
          Refresh
        </button>
      </div>

      <div class="card-body space-y-4">
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-6 gap-3">
            <label class="block xl:col-span-2">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-600">Search reports</span>
              <input
                v-model="filters.search"
                type="search"
                class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[#08AAC7]"
                placeholder="Search by report name, bank, or type..."
              />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-600">Report Type</span>
              <select
                v-model="filters.reportType"
                class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[#08AAC7]"
              >
                <option value="">All types</option>
                <option v-for="option in reportTypeOptions" :key="option" :value="option">{{ option }}</option>
              </select>
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-600">Status</span>
              <select
                v-model="filters.status"
                class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[#08AAC7]"
              >
                <option value="">All statuses</option>
                <option value="completed">Completed</option>
                <option value="processing">Processing</option>
                <option value="draft">Draft</option>
                <option value="failed">Failed</option>
                <option value="archived">Archived</option>
              </select>
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-600">Created from</span>
              <input
                v-model="filters.fromDate"
                type="date"
                class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[#08AAC7]"
              />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-slate-600">Sort by</span>
              <select
                v-model="filters.sort"
                class="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-[#08AAC7]"
              >
                <option value="created_desc">Created Date (newest)</option>
                <option value="created_asc">Created Date (oldest)</option>
                <option value="name_asc">Report Name (A–Z)</option>
                <option value="name_desc">Report Name (Z–A)</option>
                <option value="updated_desc">Updated Date (newest)</option>
              </select>
            </label>
          </div>

          <div class="flex flex-wrap gap-2">
            <button class="btn btn-secondary" :disabled="loadingReports" @click="refreshReports">
              Apply Filters
            </button>
            <button class="btn" :disabled="loadingReports" @click="resetFilters">
              Clear Filters
            </button>
            <button
              class="btn"
              :disabled="selectedIds.length === 0 || actionLoading"
              @click="openBulkConfirm('archive')"
            >
              Archive Selected
            </button>
            <button
              class="btn"
              :disabled="selectedIds.length === 0 || actionLoading"
              @click="openBulkConfirm('restore')"
            >
              Restore Selected
            </button>
            <button
              class="btn btn-danger"
              :disabled="selectedIds.length === 0 || actionLoading"
              @click="openBulkConfirm('delete')"
            >
              Delete Selected
            </button>
          </div>
        </div>

        <DataTable
          :columns="reportColumns"
          :rows="displayRows"
          row-key="id"
          :loading="loadingReports"
          :error="reportsError"
          loading-message="Loading reports..."
          :empty-title="hasActiveFilters ? 'No reports match your search criteria.' : 'No reports found.'"
          :empty-message="hasActiveFilters ? 'Try adjusting search or filters.' : 'Generate a report from Upload Data to see it here.'"
          :selectable="true"
          v-model:selected-keys="selectedIds"
          :page-size="10"
          caption="Report management table"
        >
          <template #cell-report_name="{ row }">
            <div class="min-w-[14rem] max-w-[22rem]">
              <div class="font-medium text-slate-900 line-clamp-2" :title="row.report_name">
                {{ row.report_name }}
              </div>
              <div v-if="row.bank_name" class="text-xs text-slate-500 mt-0.5 truncate">
                {{ row.bank_name }}
              </div>
            </div>
          </template>

          <template #cell-report_type="{ value }">
            <span class="text-slate-800">{{ value || '—' }}</span>
          </template>

          <template #cell-created_by="{ value }">
            <span>{{ value || 'System' }}</span>
          </template>

          <template #cell-created_at="{ value }">
            <span class="tabular-nums">{{ formatDateTime(value) }}</span>
          </template>

          <template #cell-updated_at="{ value }">
            <span class="tabular-nums">{{ formatDateTime(value) }}</span>
          </template>

          <template #cell-status="{ row }">
            <StatusBadge :status="row.status" />
          </template>

          <template #cell-version="{ value }">
            <span class="tabular-nums font-medium text-slate-700">{{ formatVersion(value) }}</span>
          </template>

          <template #cell-sections_count="{ value }">
            <span class="tabular-nums">{{ Number.isFinite(Number(value)) ? value : '—' }}</span>
          </template>

          <template #cell-actions="{ row }">
            <div class="flex flex-wrap items-center gap-1.5 min-w-[16rem]" @click.stop>
              <router-link
                :to="`/reports/${row.id}`"
                class="inline-flex items-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#08AAC7]"
              >
                View
              </router-link>
              <router-link
                :to="`/prompt-studio/${row.id}`"
                class="inline-flex items-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#08AAC7]"
              >
                Edit
              </router-link>
              <button
                type="button"
                class="inline-flex items-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#08AAC7]"
                :disabled="actionLoading"
                @click="openSingleConfirm(row, 'regenerate')"
              >
                Regenerate
              </button>
              <a
                :href="getReportDownloadUrl(row.id, 'pdf')"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center rounded-md border border-slate-300 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#08AAC7]"
              >
                Export
              </a>
              <button
                type="button"
                class="inline-flex items-center rounded-md border border-red-200 bg-white px-2.5 py-1 text-xs font-medium text-red-700 hover:bg-red-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
                :disabled="actionLoading"
                @click="openSingleConfirm(row, 'delete')"
              >
                Delete
              </button>
            </div>
          </template>
        </DataTable>
      </div>
    </section>

    <ConfirmDialog
      :open="confirmOpen"
      :title="confirmTitle"
      :message="confirmMessage"
      :confirm-label="confirmLabel"
      :danger="confirmDanger"
      :busy="actionLoading"
      @cancel="closeConfirm"
      @confirm="executeConfirm"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { useAuthStore } from '@/stores/auth'
import { getReportDownloadUrl } from '@/services/api'
import DataTable from '@/components/DataTable.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { formatDateTime, formatVersion } from '@/utils/tableFormat'

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()
const router = useRouter()

const retentionDays = ref(90)
const retentionUnit = ref('days')
const autoCleanup = ref(false)
const savingRetention = ref(false)
const runningCleanup = ref(false)
const cleanupPreview = ref(null)
const statusMessage = ref('')
const statusError = ref(false)

const filters = reactive({
  search: '',
  status: '',
  reportType: '',
  fromDate: '',
  sort: 'created_desc',
})

const loadingReports = ref(false)
const actionLoading = ref(false)
const reportsError = ref(null)
const reportRows = ref([])
const selectedIds = ref([])

const confirmOpen = ref(false)
const confirmAction = ref('')
const confirmIds = ref([])
const confirmTitle = ref('')
const confirmMessage = ref('')
const confirmLabel = ref('Confirm')
const confirmDanger = ref(false)
const pendingRegenerateId = ref(null)

const reportColumns = [
  { key: 'report_name', label: 'Report Name', wrap: true, width: '16rem' },
  { key: 'report_type', label: 'Report Type', width: '11rem' },
  { key: 'created_by', label: 'Created By', width: '8rem' },
  { key: 'created_at', label: 'Created Date', width: '10rem' },
  { key: 'updated_at', label: 'Updated Date', width: '10rem' },
  { key: 'status', label: 'Status', width: '8rem' },
  { key: 'version', label: 'Version', align: 'right', numeric: true, width: '5rem' },
  { key: 'sections_count', label: 'Sections', align: 'right', numeric: true, width: '5rem' },
  { key: 'actions', label: 'Actions', width: '17rem' },
]

const hasActiveFilters = computed(() =>
  Boolean(filters.search || filters.status || filters.reportType || filters.fromDate),
)

const reportTypeOptions = computed(() => {
  const values = new Set(
    reportRows.value
      .map((row) => row.report_type)
      .filter(Boolean),
  )
  return Array.from(values).sort((a, b) => a.localeCompare(b))
})

const displayRows = computed(() => {
  let rows = [...reportRows.value]

  if (filters.reportType) {
    rows = rows.filter((row) => row.report_type === filters.reportType)
  }

  if (filters.status) {
    rows = rows.filter((row) => String(row.status || '').toLowerCase() === filters.status)
  }

  if (filters.fromDate) {
    const from = new Date(filters.fromDate)
    rows = rows.filter((row) => {
      const created = new Date(row.created_at)
      return !Number.isNaN(created.getTime()) && created >= from
    })
  }

  if (filters.search.trim()) {
    const needle = filters.search.trim().toLowerCase()
    rows = rows.filter((row) => {
      const haystack = [
        row.report_name,
        row.title,
        row.bank_name,
        row.report_type,
        row.created_by,
        row.status,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      return haystack.includes(needle)
    })
  }

  const sorter = {
    created_desc: (a, b) => new Date(b.created_at) - new Date(a.created_at),
    created_asc: (a, b) => new Date(a.created_at) - new Date(b.created_at),
    name_asc: (a, b) => String(a.report_name || '').localeCompare(String(b.report_name || '')),
    name_desc: (a, b) => String(b.report_name || '').localeCompare(String(a.report_name || '')),
    updated_desc: (a, b) => new Date(b.updated_at) - new Date(a.updated_at),
  }
  rows.sort(sorter[filters.sort] || sorter.created_desc)
  return rows
})

const setStatus = (message, isError = false) => {
  statusMessage.value = message
  statusError.value = isError
}

const loadRetentionSettings = async () => {
  const settings = await analyticsStore.fetchUserSettings()
  retentionDays.value = Number(settings.retentionDays || 90)
  retentionUnit.value = String(settings.retentionUnit || 'days')
  autoCleanup.value = Boolean(settings.autoCleanup)
}

const saveRetentionSettings = async () => {
  if (!authStore.isAdmin) {
    setStatus('Only administrators can update retention settings.', true)
    return
  }
  if (!Number.isFinite(retentionDays.value) || retentionDays.value < 1) {
    setStatus('Retention period must be a positive number.', true)
    return
  }
  savingRetention.value = true
  try {
    const settings = await analyticsStore.fetchUserSettings()
    const payload = {
      ...settings,
      retentionDays: retentionDays.value,
      retentionUnit: retentionUnit.value,
      autoCleanup: autoCleanup.value,
    }
    await analyticsStore.saveUserSettings(payload)
    cleanupPreview.value = await analyticsStore.previewCleanup()
    setStatus('Retention settings saved successfully.')
  } catch (error) {
    setStatus(error?.message || 'Failed to save retention settings.', true)
  } finally {
    savingRetention.value = false
  }
}

const resetRetentionDefaults = () => {
  retentionDays.value = 90
  retentionUnit.value = 'days'
  autoCleanup.value = false
  setStatus('Retention defaults restored. Click Save Settings to apply.')
}

const runCleanupNow = async () => {
  runningCleanup.value = true
  try {
    const result = await analyticsStore.runCleanup(false)
    setStatus(result?.message || 'Cleanup completed.')
    await refreshReports()
  } catch (error) {
    setStatus(error?.message || 'Cleanup failed.', true)
  } finally {
    runningCleanup.value = false
  }
}

const refreshReports = async () => {
  loadingReports.value = true
  reportsError.value = null
  try {
    const response = await analyticsStore.fetchManageableReports({
      search: '',
      status: '',
      include_archived: true,
    })
    const rows = (response?.results || []).map((row) => ({
      ...row,
      report_name: row.report_name || row.title || row.filename || row.id,
      created_by: row.created_by || 'System',
      version: row.version ?? 1,
      sections_count: row.sections_count ?? 0,
      status: row.is_archived && row.status === 'completed' ? 'archived' : (row.status || 'completed'),
    }))
    reportRows.value = rows
    selectedIds.value = selectedIds.value.filter((id) => rows.some((row) => row.id === id))
  } catch (error) {
    reportsError.value = 'Unable to load reports. Please try again.'
    setStatus(error?.message || 'Failed to load reports.', true)
  } finally {
    loadingReports.value = false
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.reportType = ''
  filters.fromDate = ''
  filters.sort = 'created_desc'
}

const closeConfirm = () => {
  if (actionLoading.value) return
  confirmOpen.value = false
  confirmAction.value = ''
  confirmIds.value = []
  pendingRegenerateId.value = null
}

const openBulkConfirm = (action) => {
  if (!selectedIds.value.length) return
  const count = selectedIds.value.length
  confirmAction.value = action
  confirmIds.value = [...selectedIds.value]
  pendingRegenerateId.value = null
  confirmDanger.value = action === 'delete'
  confirmLabel.value = action === 'delete' ? 'Delete' : action === 'archive' ? 'Archive' : 'Restore'
  confirmTitle.value = `${confirmLabel.value} ${count} report${count === 1 ? '' : 's'}`
  confirmMessage.value =
    action === 'delete'
      ? `You are about to permanently delete ${count} selected report${count === 1 ? '' : 's'}.\n\nThis cannot be undone.`
      : `You are about to ${action} ${count} selected report${count === 1 ? '' : 's'}.`
  confirmOpen.value = true
}

const openSingleConfirm = (row, action) => {
  confirmAction.value = action
  confirmIds.value = [row.id]
  pendingRegenerateId.value = action === 'regenerate' ? row.id : null
  confirmDanger.value = action === 'delete'
  confirmLabel.value =
    action === 'delete' ? 'Delete' : action === 'regenerate' ? 'Continue' : 'Confirm'
  confirmTitle.value =
    action === 'delete'
      ? 'Delete report'
      : action === 'regenerate'
        ? 'Regenerate report'
        : 'Confirm action'
  confirmMessage.value =
    action === 'delete'
      ? `You are about to permanently delete:\n\n“${row.report_name}”\n\nThis cannot be undone.`
      : action === 'regenerate'
        ? `Open “${row.report_name}” to regenerate sections from the current prompts?\n\nOnly the sections you choose will be regenerated.`
        : `Confirm action for “${row.report_name}”.`
  confirmOpen.value = true
}

const runBulkAction = async (action, ids) => {
  actionLoading.value = true
  try {
    await analyticsStore.bulkReportAction(action, ids)
    const verb = action === 'delete' ? 'deleted' : `${action}d`
    setStatus(`Reports ${verb} successfully.`)
    selectedIds.value = selectedIds.value.filter((id) => !ids.includes(id))
    await refreshReports()
  } catch (error) {
    setStatus(error?.message || `Failed to ${action} reports.`, true)
  } finally {
    actionLoading.value = false
  }
}

const executeConfirm = async () => {
  const action = confirmAction.value
  const ids = [...confirmIds.value]
  if (action === 'regenerate' && pendingRegenerateId.value) {
    confirmOpen.value = false
    router.push(`/reports/${pendingRegenerateId.value}`)
    pendingRegenerateId.value = null
    return
  }
  if (!ids.length || !['archive', 'restore', 'delete'].includes(action)) {
    closeConfirm()
    return
  }
  await runBulkAction(action, ids)
  confirmOpen.value = false
  confirmAction.value = ''
  confirmIds.value = []
}

watch(
  () => [filters.search, filters.status, filters.reportType, filters.fromDate, filters.sort],
  () => {
    selectedIds.value = selectedIds.value.filter((id) => displayRows.value.some((row) => row.id === id))
  },
)

onMounted(async () => {
  await loadRetentionSettings()
  try {
    cleanupPreview.value = await analyticsStore.previewCleanup()
  } catch {
    cleanupPreview.value = null
  }
  await refreshReports()
})
</script>
