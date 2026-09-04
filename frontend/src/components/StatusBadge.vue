<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    status?: string | null
    label?: string | null
  }>(),
  {
    status: '',
    label: null,
  },
)

const normalized = computed(() => String(props.status || '').trim().toLowerCase())

const displayLabel = computed(() => {
  if (props.label) return props.label
  const map: Record<string, string> = {
    completed: 'Completed',
    complete: 'Completed',
    processing: 'Processing',
    pending: 'Processing',
    draft: 'Draft',
    failed: 'Failed',
    error: 'Failed',
    archived: 'Archived',
    active: 'Active',
    current: 'Current',
    synchronized: 'Synchronized',
    mismatch: 'Mismatch',
    missing: 'Missing',
    low: 'Low',
    moderate: 'Moderate',
    medium: 'Moderate',
    high: 'High',
    critical: 'Critical',
  }
  return map[normalized.value] || (props.status ? String(props.status) : 'Unknown')
})

const badgeClass = computed(() => {
  const key = normalized.value
  if (['completed', 'complete', 'active', 'current', 'synchronized', 'low', 'success'].includes(key)) {
    return 'bg-emerald-50 text-emerald-800 ring-emerald-600/20'
  }
  if (['processing', 'pending', 'draft', 'moderate', 'medium', 'mismatch', 'info'].includes(key)) {
    return 'bg-amber-50 text-amber-900 ring-amber-600/20'
  }
  if (['failed', 'error', 'high', 'critical', 'missing', 'danger'].includes(key)) {
    return 'bg-red-50 text-red-800 ring-red-600/20'
  }
  if (['archived'].includes(key)) {
    return 'bg-slate-100 text-slate-700 ring-slate-500/20'
  }
  return 'bg-sky-50 text-sky-800 ring-sky-600/20'
})
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-semibold ring-1 ring-inset whitespace-nowrap"
    :class="badgeClass"
    :title="displayLabel"
  >
    <span class="h-1.5 w-1.5 rounded-full bg-current opacity-70" aria-hidden="true" />
    <span>{{ displayLabel }}</span>
  </span>
</template>
