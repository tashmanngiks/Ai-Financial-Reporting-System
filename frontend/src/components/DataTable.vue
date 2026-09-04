<script setup lang="ts">
import { computed, ref, watch } from 'vue'

export type DataTableColumn = {
  key: string
  label: string
  align?: 'left' | 'center' | 'right'
  width?: string
  sortable?: boolean
  numeric?: boolean
  wrap?: boolean
  className?: string
}

const props = withDefaults(
  defineProps<{
    columns: DataTableColumn[]
    rows: Record<string, any>[]
    rowKey?: string
    loading?: boolean
    error?: string | null
    emptyTitle?: string
    emptyMessage?: string
    loadingMessage?: string
    pageSize?: number
    selectable?: boolean
    selectedKeys?: Array<string | number>
    sortKey?: string
    sortDir?: 'asc' | 'desc'
    caption?: string
  }>(),
  {
    rowKey: 'id',
    loading: false,
    error: null,
    emptyTitle: 'No records found',
    emptyMessage: 'There is nothing to display yet.',
    loadingMessage: 'Loading...',
    pageSize: 10,
    selectable: false,
    selectedKeys: () => [],
    sortKey: '',
    sortDir: 'asc',
    caption: '',
  },
)

const emit = defineEmits<{
  'update:selectedKeys': [keys: Array<string | number>]
  'update:sortKey': [key: string]
  'update:sortDir': [dir: 'asc' | 'desc']
  sort: [payload: { key: string; dir: 'asc' | 'desc' }]
  'row-click': [row: Record<string, any>]
}>()

const currentPage = ref(1)

watch(
  () => [props.rows, props.pageSize, props.sortKey, props.sortDir],
  () => {
    currentPage.value = 1
  },
)

const totalPages = computed(() => Math.max(1, Math.ceil(props.rows.length / props.pageSize)))

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * props.pageSize
  return props.rows.slice(start, start + props.pageSize)
})

const pageKeys = computed(() => pagedRows.value.map((row) => row[props.rowKey]))

const allPageSelected = computed(
  () => pageKeys.value.length > 0 && pageKeys.value.every((key) => props.selectedKeys.includes(key)),
)

const somePageSelected = computed(
  () => pageKeys.value.some((key) => props.selectedKeys.includes(key)) && !allPageSelected.value,
)

const alignClass = (column: DataTableColumn) => {
  if (column.align === 'right' || column.numeric) return 'text-right'
  if (column.align === 'center') return 'text-center'
  return 'text-left'
}

const cellClass = (column: DataTableColumn) => [
  'px-3 py-3 text-sm text-slate-800 align-middle',
  alignClass(column),
  column.wrap ? 'whitespace-normal break-words' : 'whitespace-nowrap',
  column.className || '',
]

const headerClass = (column: DataTableColumn) => [
  'px-3 py-3 text-xs font-semibold uppercase tracking-wide text-slate-600',
  alignClass(column),
  column.wrap ? 'whitespace-normal' : 'whitespace-nowrap',
]

const toggleSelectAll = (checked: boolean) => {
  if (!props.selectable) return
  if (checked) {
    const merged = Array.from(new Set([...props.selectedKeys, ...pageKeys.value]))
    emit('update:selectedKeys', merged)
  } else {
    emit(
      'update:selectedKeys',
      props.selectedKeys.filter((key) => !pageKeys.value.includes(key)),
    )
  }
}

const toggleRow = (key: string | number, checked: boolean) => {
  if (!props.selectable) return
  if (checked) {
    emit('update:selectedKeys', Array.from(new Set([...props.selectedKeys, key])))
  } else {
    emit(
      'update:selectedKeys',
      props.selectedKeys.filter((item) => item !== key),
    )
  }
}

const onSort = (column: DataTableColumn) => {
  if (!column.sortable) return
  const nextDir = props.sortKey === column.key && props.sortDir === 'asc' ? 'desc' : 'asc'
  emit('update:sortKey', column.key)
  emit('update:sortDir', nextDir)
  emit('sort', { key: column.key, dir: nextDir })
}

const goToPage = (page: number) => {
  currentPage.value = Math.min(totalPages.value, Math.max(1, page))
}

const rangeLabel = computed(() => {
  if (!props.rows.length) return '0 records'
  const start = (currentPage.value - 1) * props.pageSize + 1
  const end = Math.min(props.rows.length, currentPage.value * props.pageSize)
  return `Showing ${start}–${end} of ${props.rows.length}`
})
</script>

<template>
  <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
    <div class="overflow-x-auto">
      <table class="min-w-full border-separate border-spacing-0" :aria-busy="loading ? 'true' : 'false'">
        <caption v-if="caption" class="sr-only">{{ caption }}</caption>
        <thead class="bg-slate-50 sticky top-0 z-10">
          <tr>
            <th
              v-if="selectable"
              scope="col"
              class="px-3 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-600 w-10 border-b border-slate-200"
            >
              <input
                type="checkbox"
                class="rounded border-slate-300 text-[#08AAC7] focus:ring-[#08AAC7]"
                :checked="allPageSelected"
                :indeterminate.prop="somePageSelected"
                aria-label="Select all rows on this page"
                @change="toggleSelectAll(($event.target as HTMLInputElement).checked)"
              />
            </th>
            <th
              v-for="column in columns"
              :key="column.key"
              scope="col"
              class="border-b border-slate-200"
              :class="headerClass(column)"
              :style="column.width ? { width: column.width, minWidth: column.width } : undefined"
            >
              <button
                v-if="column.sortable"
                type="button"
                class="inline-flex items-center gap-1 hover:text-slate-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#08AAC7] rounded"
                @click="onSort(column)"
              >
                <span>{{ column.label }}</span>
                <span class="text-[10px] text-slate-400" aria-hidden="true">
                  <template v-if="sortKey === column.key">{{ sortDir === 'asc' ? '▲' : '▼' }}</template>
                  <template v-else>↕</template>
                </span>
              </button>
              <span v-else>{{ column.label }}</span>
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-if="loading">
            <td
              :colspan="columns.length + (selectable ? 1 : 0)"
              class="px-4 py-10 text-center text-sm text-slate-500 border-b border-slate-100"
            >
              <div class="inline-flex items-center gap-3">
                <span class="h-5 w-5 rounded-full border-2 border-slate-300 border-t-[#08AAC7] animate-spin" aria-hidden="true" />
                <span>{{ loadingMessage }}</span>
              </div>
            </td>
          </tr>

          <tr v-else-if="error">
            <td
              :colspan="columns.length + (selectable ? 1 : 0)"
              class="px-4 py-10 text-center text-sm text-red-700 border-b border-slate-100"
            >
              <div class="font-medium">{{ error }}</div>
            </td>
          </tr>

          <tr v-else-if="!rows.length">
            <td
              :colspan="columns.length + (selectable ? 1 : 0)"
              class="px-4 py-10 text-center border-b border-slate-100"
            >
              <div class="text-sm font-semibold text-slate-900">{{ emptyTitle }}</div>
              <div class="mt-1 text-sm text-slate-500">{{ emptyMessage }}</div>
              <div v-if="$slots.empty" class="mt-4">
                <slot name="empty" />
              </div>
            </td>
          </tr>

          <tr
            v-for="row in pagedRows"
            v-else
            :key="row[rowKey]"
            class="group hover:bg-slate-50/80 transition-colors"
            @click="emit('row-click', row)"
          >
            <td
              v-if="selectable"
              class="px-3 py-3 border-b border-slate-100 align-middle"
              @click.stop
            >
              <input
                type="checkbox"
                class="rounded border-slate-300 text-[#08AAC7] focus:ring-[#08AAC7]"
                :checked="selectedKeys.includes(row[rowKey])"
                :aria-label="`Select ${row[rowKey]}`"
                @change="toggleRow(row[rowKey], ($event.target as HTMLInputElement).checked)"
              />
            </td>
            <td
              v-for="column in columns"
              :key="`${row[rowKey]}-${column.key}`"
              class="border-b border-slate-100"
              :class="cellClass(column)"
              :style="column.width ? { width: column.width, minWidth: column.width } : undefined"
            >
              <slot :name="`cell-${column.key}`" :row="row" :column="column" :value="row[column.key]">
                <span :class="column.wrap ? 'line-clamp-2' : ''">
                  {{ row[column.key] ?? '—' }}
                </span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-if="!loading && !error && rows.length > pageSize"
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-4 py-3 border-t border-slate-200 bg-slate-50"
    >
      <p class="text-xs text-slate-600">{{ rangeLabel }}</p>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="btn btn-secondary !px-3 !py-1.5 text-xs"
          :disabled="currentPage <= 1"
          @click="goToPage(currentPage - 1)"
        >
          Previous
        </button>
        <span class="text-xs text-slate-600">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          type="button"
          class="btn btn-secondary !px-3 !py-1.5 text-xs"
          :disabled="currentPage >= totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>
