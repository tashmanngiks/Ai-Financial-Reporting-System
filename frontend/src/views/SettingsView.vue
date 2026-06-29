<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <p class="text-sm text-gray-600 mt-1">Configure automatic retention and manage generated reports.</p>
      </div>
      <div v-if="statusMessage" class="text-sm px-3 py-2 rounded" :class="statusError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'">
        {{ statusMessage }}
      </div>
    </div>

    <section class="card">
      <div class="card-header">
        <h2 class="text-lg font-semibold">Automatic Data Retention</h2>
      </div>
      <div class="card-body space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Retention Period</span>
            <input v-model.number="retentionDays" type="number" min="1" max="3650" name="retention_days" class="mt-1 w-full border rounded px-3 py-2" />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-gray-700">Time Unit</span>
            <select v-model="retentionUnit" name="retention_unit" class="mt-1 w-full border rounded px-3 py-2">
              <option value="days">Days</option>
              <option value="weeks">Weeks</option>
              <option value="months">Months</option>
            </select>
          </label>
          <label class="inline-flex items-center gap-2 mt-6">
            <input v-model="autoCleanup" type="checkbox" name="auto_cleanup" />
            <span class="text-sm text-gray-700">Enable automatic cleanup</span>
          </label>
        </div>

        <div class="flex gap-3 flex-wrap">
          <button class="btn btn-primary" :disabled="savingRetention" @click="saveRetentionSettings">
            <span v-if="savingRetention">Saving...</span>
            <span v-else>Save Settings</span>
          </button>
          <button class="btn btn-secondary" :disabled="savingRetention" @click="resetRetentionDefaults">Reset to Default</button>
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
      <div class="card-header flex items-center justify-between">
        <h2 class="text-lg font-semibold">Report Management</h2>
        <button class="btn" :disabled="loadingReports" @click="refreshReports">Refresh</button>
      </div>
      <div class="card-body space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-3">
          <input v-model="filters.search" type="text" class="border rounded px-3 py-2" placeholder="Search reports..." />
          <select v-model="filters.status" class="border rounded px-3 py-2">
            <option value="">All statuses</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
          <select v-model="filters.archiveFilter" class="border rounded px-3 py-2">
            <option value="all">All records</option>
            <option value="active">Active only</option>
            <option value="archived">Archived only</option>
          </select>
          <input v-model="filters.fromDate" type="date" class="border rounded px-3 py-2" />
          <button class="btn" :disabled="loadingReports" @click="refreshReports">Apply Filters</button>
        </div>

        <div class="flex gap-2 flex-wrap">
          <button class="btn" :disabled="selectedIds.length === 0 || actionLoading" @click="confirmBulkAction('archive')">Archive Selected</button>
          <button class="btn" :disabled="selectedIds.length === 0 || actionLoading" @click="confirmBulkAction('restore')">Restore Selected</button>
          <button class="btn btn-danger" :disabled="selectedIds.length === 0 || actionLoading" @click="confirmBulkAction('delete')">Delete Selected</button>
        </div>

        <div v-if="loadingReports" class="text-sm text-gray-500">Loading reports...</div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="text-left border-b">
                <th class="py-2"><input type="checkbox" :checked="allVisibleSelected" @change="toggleSelectAll($event)" /></th>
                <th class="py-2">Title</th>
                <th class="py-2">Bank</th>
                <th class="py-2">Type</th>
                <th class="py-2">Status</th>
                <th class="py-2">Created</th>
                <th class="py-2">Archived</th>
                <th class="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in reportRows" :key="report.id" class="border-b">
                <td class="py-2"><input type="checkbox" :value="report.id" v-model="selectedIds" /></td>
                <td class="py-2">{{ report.title }}</td>
                <td class="py-2">{{ report.bank_name || '-' }}</td>
                <td class="py-2">{{ report.report_type }}</td>
                <td class="py-2">{{ report.status }}</td>
                <td class="py-2">{{ formatDate(report.created_at) }}</td>
                <td class="py-2">{{ report.is_archived ? 'Yes' : 'No' }}</td>
                <td class="py-2 flex gap-2">
                  <button class="text-xs text-blue-600" @click="singleAction(report.id, report.is_archived ? 'restore' : 'archive')">
                    {{ report.is_archived ? 'Restore' : 'Archive' }}
                  </button>
                  <button class="text-xs text-red-600" @click="singleAction(report.id, 'delete')">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useAnalyticsStore } from '@/stores/analytics'
import { useAuthStore } from '@/stores/auth'

const analyticsStore = useAnalyticsStore()
const authStore = useAuthStore()

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
  archiveFilter: 'all',
  fromDate: '',
})
const loadingReports = ref(false)
const actionLoading = ref(false)
const reportRows = ref([])
const selectedIds = ref([])

const allVisibleSelected = computed(
  () => reportRows.value.length > 0 && reportRows.value.every((row) => selectedIds.value.includes(row.id)),
)

const setStatus = (message, isError = false) => {
  statusMessage.value = message
  statusError.value = isError
}

const formatDate = (value) => {
  if (!value) return '-'
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString()
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
  try {
    const include_archived = filters.archiveFilter !== 'active'
    const response = await analyticsStore.fetchManageableReports({
      search: filters.search,
      status: filters.status,
      include_archived,
    })
    let rows = response?.results || []
    if (filters.archiveFilter === 'archived') rows = rows.filter((r) => r.is_archived)
    if (filters.archiveFilter === 'active') rows = rows.filter((r) => !r.is_archived)
    if (filters.fromDate) {
      const from = new Date(filters.fromDate)
      rows = rows.filter((r) => new Date(r.created_at) >= from)
    }
    reportRows.value = rows
    selectedIds.value = selectedIds.value.filter((id) => rows.some((r) => r.id === id))
  } catch (error) {
    setStatus(error?.message || 'Failed to load reports.', true)
  } finally {
    loadingReports.value = false
  }
}

const toggleSelectAll = (event) => {
  const checked = event.target.checked
  selectedIds.value = checked ? reportRows.value.map((r) => r.id) : []
}

const runBulkAction = async (action, ids) => {
  actionLoading.value = true
  try {
    await analyticsStore.bulkReportAction(action, ids)
    setStatus(`Reports ${action}d successfully.`)
    await refreshReports()
  } catch (error) {
    setStatus(error?.message || `Failed to ${action} reports.`, true)
  } finally {
    actionLoading.value = false
  }
}

const confirmBulkAction = async (action) => {
  if (selectedIds.value.length === 0) return
  const confirmed = window.confirm(`Are you sure you want to ${action} ${selectedIds.value.length} selected report(s)?`)
  if (!confirmed) return
  await runBulkAction(action, selectedIds.value)
}

const singleAction = async (id, action) => {
  if (action === 'delete') {
    const confirmed = window.confirm('Delete this report permanently?')
    if (!confirmed) return
  }
  await runBulkAction(action, [id])
}

watch(() => [filters.search, filters.status, filters.archiveFilter, filters.fromDate], () => {
  refreshReports()
})

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
