<template>
  <div class="max-w-4xl mx-auto p-6">
    <h1 class="text-2xl font-semibold mb-4">System Prompt Editor</h1>

    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-1">Editable System Prompt Template</label>
      <textarea
        v-model="templateText"
        rows="14"
        class="w-full border rounded p-3 font-mono text-sm"
      />
    </div>

    <div class="flex items-center gap-3">
      <button @click="save" class="btn btn-primary">Save</button>
      <button @click="reload" class="btn">Reload</button>
      <span v-if="statusMessage" class="ml-4 text-sm">{{ statusMessage }}</span>
    </div>

    <div class="mt-6">
      <h2 class="text-lg font-medium mb-2">Template Variables</h2>
      <ul class="list-disc ml-6 text-sm">
        <li><strong>{template_name}</strong> — template name</li>
        <li><strong>{length}</strong> — report length</li>
        <li><strong>{detail_level}</strong> — detail level</li>
        <li><strong>{output_format}</strong> — output format</li>
        <li><strong>{bank_name}</strong> — bank or entity name</li>
        <li><strong>{data_period}</strong> — reporting period</li>
        <li><strong>{available_data}</strong> — comma-separated available data areas</li>
        <li><strong>{selected_sections_block}</strong> — newline list of selected sections</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

const templateText = ref('')
const statusMessage = ref('')

async function load() {
  try {
    const resp = await api.getReportPromptConfig()
    if (resp.data && resp.data.config) {
      templateText.value = resp.data.config.system_prompt_template || ''
      statusMessage.value = ''
    }
  } catch (err) {
    statusMessage.value = 'Failed to load template.'
  }
}

function reload() {
  load()
}

async function save() {
  statusMessage.value = 'Saving...'
  try {
    // Get current config, update template key, and send entire config back
    const resp = await api.getReportPromptConfig()
    const config = resp.data && resp.data.config ? resp.data.config : {}
    config.system_prompt_template = templateText.value
    const saveResp = await api.updateReportPromptConfig(config)
    if (saveResp.data && saveResp.data.config) {
      statusMessage.value = 'Saved successfully.'
    } else {
      statusMessage.value = 'Save returned unexpected response.'
    }
  } catch (err) {
    statusMessage.value = 'Save failed.'
  }
}

onMounted(load)
</script>

<style scoped>
.btn { padding: 0.5rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; background: white }
.btn-primary { background: #2563eb; color: white; border-color: #2563eb }
</style>
