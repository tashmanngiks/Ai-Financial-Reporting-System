<script setup lang="ts">
import { computed, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title?: string
    message?: string
    confirmLabel?: string
    cancelLabel?: string
    danger?: boolean
    busy?: boolean
  }>(),
  {
    title: 'Confirm action',
    message: 'Are you sure you want to continue?',
    confirmLabel: 'Confirm',
    cancelLabel: 'Cancel',
    danger: false,
    busy: false,
  },
)

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()

const dialogTitle = computed(() => props.title)

watch(
  () => props.open,
  (isOpen) => {
    if (typeof document === 'undefined') return
    document.body.style.overflow = isOpen ? 'hidden' : ''
  },
)

const onCancel = () => {
  if (props.busy) return
  emit('cancel')
}

const onConfirm = () => {
  if (props.busy) return
  emit('confirm')
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="'confirm-dialog-title'"
    >
      <div class="absolute inset-0 bg-slate-900/40" @click="onCancel" />
      <div class="relative w-full max-w-md rounded-xl bg-white shadow-xl border border-slate-200 p-5">
        <h3 id="confirm-dialog-title" class="text-lg font-semibold text-slate-900">{{ dialogTitle }}</h3>
        <p class="mt-2 text-sm text-slate-600 whitespace-pre-wrap">{{ message }}</p>
        <div class="mt-5 flex justify-end gap-2">
          <button
            type="button"
            class="btn btn-secondary"
            :disabled="busy"
            @click="onCancel"
          >
            {{ cancelLabel }}
          </button>
          <button
            type="button"
            class="btn"
            :class="danger ? 'btn-danger' : 'btn-primary'"
            :disabled="busy"
            @click="onConfirm"
          >
            <span v-if="busy">Working...</span>
            <span v-else>{{ confirmLabel }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
