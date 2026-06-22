<template>
  <div class="p-6">
    <!-- World-Class Header -->
    <div class="mb-10">
      <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
        <div class="px-8 py-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="bg-white/20 backdrop-blur-sm rounded-lg p-3">
                <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
              </div>
              <div>
                <h1 class="text-3xl font-bold text-white">Upload Financial Data</h1>
                <p class="text-[#E6F7FB] text-lg mt-1">Upload JSON data and describe the report you need</p>
              </div>
            </div>
            <div class="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
              <span class="text-white text-sm font-medium">Secure Upload</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- World-Class Upload Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
      <!-- Main Upload Area -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-lg p-2">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Upload File</h3>
              <p class="text-gray-600 text-sm">Drag & drop or browse your JSON file</p>
            </div>
          </div>
        </div>

        <div class="p-8">
          <div
            class="relative border-2 border-dashed border-[#08AAC7]/30 rounded-2xl p-8 text-center hover:border-[#08AAC7]/50 transition-all duration-300 bg-gradient-to-br from-[#08AAC7]/5 to-[#0691A8]/5 hover:from-[#08AAC7]/10 hover:to-[#0691A8]/10 cursor-pointer group"
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="handleDrop"
            @click="openFilePicker"
          >
            <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-[#08AAC7]/10 to-[#0691A8]/10 rounded-full -mr-12 -mt-12 group-hover:scale-110 transition-transform duration-300"></div>
            <div class="flex flex-col items-center">
              <div class="bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-full p-4 mb-4 group-hover:scale-110 transition-transform duration-300">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
              </div>
              <p class="text-lg font-semibold text-gray-900 mb-2">Drop your JSON file here</p>
              <p class="text-sm text-gray-600 mb-4">or click to browse</p>
              <div class="inline-flex items-center px-4 py-2 bg-[#08AAC7] text-white rounded-lg hover:bg-[#0691A8] transition-colors duration-300">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3H6l3 3m0 0h6"></path>
                </svg>
                <span class="text-sm font-medium">Choose File</span>
              </div>
              <input
                id="file-upload"
                ref="fileInput"
                type="file"
                accept=".json"
                class="hidden"
                @change="handleFileSelect"
              />
            </div>
          </div>

          <!-- Selected File Info -->
          <div v-if="selectedFile" class="mt-6 p-4 bg-gradient-to-r from-[#08AAC7]/5 to-[#0691A8]/5 rounded-xl border border-[#08AAC7]/20">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="bg-white rounded-lg p-2">
                  <svg class="w-5 h-5 text-[#08AAC7]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <div>
                  <p class="font-semibold text-gray-900">{{ selectedFile.name }}</p>
                  <p class="text-sm text-gray-600">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
              </div>
              <button
                @click="selectedFile = null"
                class="p-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors duration-300"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Report Settings -->
          <div class="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-200">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-sm font-semibold text-gray-900">Report Settings</h3>
                <p class="text-xs text-gray-600">Choose the template, sections, and output preferences.</p>
              </div>
              <button
                type="button"
                @click="resetReportSettings"
                class="text-xs font-medium text-[#0691A8] hover:text-[#057A8F]"
              >
                Reset
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label class="block">
                <span class="text-xs font-semibold text-gray-700">Template</span>
                <select
                  v-model="selectedTemplate"
                  class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#08AAC7] bg-white text-sm"
                >
                  <option v-for="template in templateOptions" :key="template.id" :value="template.id">
                    {{ template.label }}
                  </option>
                </select>
              </label>

              <label class="block">
                <span class="text-xs font-semibold text-gray-700">Output Format</span>
                <select
                  v-model="outputFormat"
                  class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#08AAC7] bg-white text-sm"
                >
                  <option value="pdf">PDF</option>
                  <option value="word">Word</option>
                  <option value="excel">Excel</option>
                  <option value="json">JSON</option>
                </select>
              </label>

              <label class="block">
                <span class="text-xs font-semibold text-gray-700">Report Length</span>
                <select
                  v-model="reportLength"
                  class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#08AAC7] bg-white text-sm"
                >
                  <option value="short">One page</option>
                  <option value="standard">Three pages</option>
                  <option value="long">Comprehensive</option>
                  <option value="custom">Custom</option>
                </select>
              </label>

              <label class="block">
                <span class="text-xs font-semibold text-gray-700">Detail Level</span>
                <select
                  v-model="detailLevel"
                  class="mt-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#08AAC7] bg-white text-sm"
                >
                  <option value="brief">Brief</option>
                  <option value="balanced">Balanced</option>
                  <option value="detailed">Detailed</option>
                </select>
              </label>
            </div>

            <div class="mt-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-gray-700">Included Sections</span>
                <div class="flex gap-2 text-xs">
                  <button type="button" class="text-[#0691A8] hover:text-[#057A8F]" @click="selectAllSections">Select all</button>
                  <button type="button" class="text-gray-500 hover:text-gray-700" @click="clearSections">Clear</button>
                </div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto pr-1">
                <label
                  v-for="section in sectionOptions"
                  :key="section.key"
                  class="flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer"
                  :class="selectedSections.includes(section.key) ? 'border-[#08AAC7] bg-[#08AAC7]/5' : 'border-gray-200 bg-white hover:border-[#08AAC7]/40'"
                >
                  <input
                    v-model="selectedSections"
                    type="checkbox"
                    :value="section.key"
                    class="mt-1 h-4 w-4 rounded border-gray-300 text-[#08AAC7] focus:ring-[#08AAC7]"
                  />
                  <span class="flex-1 min-w-0">
                    <div class="flex items-center justify-between gap-3 w-full">
                      <div class="min-w-0">
                        <span class="block text-sm font-medium text-gray-900 truncate">{{ section.title }}</span>
                        <span class="block text-xs text-gray-600 break-words whitespace-normal">{{ section.description }}</span>
                      </div>
                      <button type="button" @click.prevent="openSectionEditor(section)" class="ml-3 text-xs text-[#0691A8] hover:text-[#057A8F] shrink-0">
                        Edit
                      </button>
                    </div>
                  </span>
                </label>
              </div>
            </div>
          </div>

          <!-- Analysis Prompt (required) -->
          <div class="mt-6">
            <label for="analysis-prompt" class="block text-sm font-semibold text-gray-900 mb-2">
              Analysis prompt <span class="text-red-500">*</span>
            </label>
            <p class="text-sm text-gray-600 mb-3">
              Start from a template, then add or remove details in the prompt or section list before generating the report.
            </p>
            <div class="flex flex-wrap gap-2 mb-3">
              <button
                v-for="template in reportPromptTemplates"
                :key="template.id"
                type="button"
                @click="applyPromptTemplate(template)"
                class="px-3 py-1.5 text-xs font-medium rounded-lg border border-[#08AAC7]/30 text-[#0691A8] bg-[#08AAC7]/5 hover:bg-[#08AAC7]/10 transition-colors"
              >
                {{ template.label }}
              </button>
            </div>
            <textarea
              id="analysis-prompt"
              v-model="analysisPrompt"
              rows="14"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#08AAC7] focus:border-transparent text-sm"
              placeholder="Describe the report structure and focus areas for the AI analysis."
            />
            <p class="text-xs text-gray-500 mt-2 text-right">{{ analysisPrompt.length }} characters</p>
          </div>

          <!-- Upload Button -->
          <div class="mt-6">
            <button
              @click="handleUpload"
              :disabled="!selectedFile || !analysisPrompt.trim() || analyticsStore.loading.upload"
              class="w-full px-6 py-4 bg-gradient-to-r from-[#08AAC7] to-[#0691A8] text-white rounded-xl hover:from-[#0691A8] hover:to-[#057A8F] transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              <span v-if="!analyticsStore.loading.upload" class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
                Generate Report
              </span>
              <span v-else class="flex items-center justify-center">
                <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                <span>Processing...</span>
              </span>
            </button>
          </div>
        </div>

        <!-- Section Editor Modal -->
        <div v-if="editingSectionKey" class="fixed inset-0 z-40 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/50" @click="closeSectionEditor"></div>
          <div class="relative max-w-lg w-full bg-white rounded-lg shadow-lg p-6 z-50">
            <h3 class="text-lg font-semibold mb-3">Edit section</h3>
            <label class="block mb-2 text-sm">Title</label>
            <input v-model="editTitle" class="w-full p-2 border rounded mb-3" />
            <label class="block mb-2 text-sm">Description</label>
            <textarea v-model="editDescription" rows="4" class="w-full p-2 border rounded mb-4"></textarea>
            <div class="flex justify-end gap-3">
              <button class="px-4 py-2 border rounded" @click="closeSectionEditor">Cancel</button>
              <button class="px-4 py-2 bg-[#08AAC7] text-white rounded" @click="saveSectionEdits" :disabled="savingSection">
                <span v-if="savingSection">Saving...</span>
                <span v-else>Save</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Information Panel -->
      <div class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <div class="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="bg-gradient-to-r from-green-500 to-emerald-600 rounded-lg p-2">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Data Requirements</h3>
              <p class="text-gray-600 text-sm">Supported formats and specifications</p>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="space-y-6">
            <!-- File Format -->
            <div class="bg-gradient-to-r from-[#08AAC7]/5 to-[#0691A8]/5 rounded-xl p-4 border border-[#08AAC7]/20">
              <div class="flex items-center space-x-3 mb-3">
                <div class="bg-white rounded-lg p-2">
                  <svg class="w-5 h-5 text-[#08AAC7]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 4H4a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V6a2 2 0 00-2-2h10a2 2 0 00-2-2v-2a2 2 0 00-2 2z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900">JSON Format</h4>
                  <p class="text-sm text-gray-600">Structured data format</p>
                </div>
              </div>
              <ul class="text-sm text-gray-600 space-y-2 ml-8">
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7L7 21"></path>
                  </svg>
                  <span>Any valid JSON (objects, arrays, nested data)</span>
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>Maximum file size: 50MB</span>
                </li>
              </ul>
            </div>

            <!-- Required Data -->
            <div class="bg-gray-50 rounded-xl p-4">
              <div class="flex items-center space-x-3 mb-3">
                <div class="bg-gray-200 rounded-lg p-2">
                  <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900">Required Data</h4>
                  <p class="text-sm text-gray-600">Essential financial information</p>
                </div>
              </div>
              <ul class="text-sm text-gray-600 space-y-2 ml-8">
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>Financial statements (income, balance sheet)</span>
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>Key performance indicators</span>
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <span>Risk metrics and compliance data</span>
                </li>
              </ul>
            </div>

            <!-- AI Analysis -->
            <div class="bg-gradient-to-r from-purple-500/10 to-indigo-600/10 rounded-xl p-4 border border-purple-500/20">
              <div class="flex items-center space-x-3 mb-3">
                <div class="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-lg p-2">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 5h3.586A1 1 0 001.071.293l5.414 5.414a1 1 0 001.293-.293 1 1 0 00.293-.293 1 1 0 00.293-.293 1 1 0 00.293-.293 1 1 0 00-.293-.293H9.664a1 1 0 00-.293.293L4.2 4.2a1 1 0 00-.293-.293 1 1 0 00-.293-.293 1 1 0 00-.293-.293L2.586 2.586A1 1 0 001.293 2.415V19a1 1 0 001.293 1.585l5.414 5.414a1 1 0 001.293-.293 1 1 0 00.293-.293 1 1 0 00.293-.293H19a1 1 0 001.293-1.585V6.415a1 1 0 00-.293-.293L15.414 1.586a1 1 0 001.293-.293 1 1 0 00.293-.293L19 6.415V19a1 1 0 001.293 1.585z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-gray-900">AI Analysis</h4>
                  <p class="text-sm text-gray-600">OpenAI-powered report from your prompt</p>
                </div>
              </div>
              <ul class="text-sm text-gray-600 space-y-2 ml-8">
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-purple-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  <span>Management report template (8 sections) pre-filled</span>
                </li>
                <li class="flex items-start">
                  <svg class="w-4 h-4 text-purple-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                  </svg>
                  <span>Focus areas you specify (risk, liquidity, KPIs, etc.)</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- World-Class Status Messages -->
    <div class="mt-8">
      <!-- Upload Progress -->
      <div v-if="analyticsStore.uploadStatus === 'processing'" class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 border-b border-blue-700">
          <div class="flex items-center space-x-3">
            <div class="bg-white/20 backdrop-blur-sm rounded-lg p-2">
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div>
              <h3 class="text-lg font-bold text-white">Generating Your Report</h3>
              <p class="text-blue-100 text-sm">AI is building your report from your prompt</p>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-sm font-medium text-gray-700 mb-2">
                <span>Processing File</span>
                <span class="text-[#08AAC7] font-bold">{{ analyticsStore.taskProgress }}%</span>
              </div>
              <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-[#08AAC7] to-[#0691A8] rounded-full transition-all duration-700 ease-out"
                  :style="{ width: analyticsStore.taskProgress + '%' }"
                ></div>
              </div>
            </div>
            <p class="text-sm text-gray-600">
              This may take a minute while we analyze your data against your requirements...
            </p>
          </div>
        </div>
      </div>

      <!-- Upload Success -->
      <div v-if="analyticsStore.uploadStatus === 'completed'" class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <div class="bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-4 border-b border-green-700">
          <div class="flex items-center space-x-3">
            <div class="bg-white/20 backdrop-blur-sm rounded-lg p-2">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-white">Analysis Complete!</h3>
              <p class="text-green-100 text-sm">Your financial report has been generated successfully</p>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="flex items-center mb-6">
            <div class="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-4 mr-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Success!</h3>
              <p class="text-gray-600">
                {{ analyticsStore.errors.upload ? 'File saved, but AI analysis needs attention.' : 'Your financial report is ready for review' }}
              </p>
            </div>
          </div>
          <div v-if="analyticsStore.errors.upload" class="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-900">
            {{ analyticsStore.errors.upload }}
          </div>
          <div class="mt-4">
            <router-link
              :to="`/reports/${analyticsStore.currentReport}`"
              class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
              View Report
            </router-link>
          </div>
        </div>
      </div>

      <!-- Upload Error -->
      <div v-if="analyticsStore.uploadStatus === 'failed'" class="relative bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl border border-gray-100 overflow-hidden hover:shadow-2xl transition-all duration-300">
        <div class="bg-gradient-to-r from-red-600 to-orange-600 px-6 py-4 border-b border-red-700">
          <div class="flex items-center space-x-3">
            <div class="bg-white/20 backdrop-blur-sm rounded-lg p-2">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-white">Upload Failed</h3>
              <p class="text-red-100 text-sm">{{ analyticsStore.errors.upload || 'An error occurred during upload.' }}</p>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="flex items-center mb-6">
            <div class="bg-gradient-to-r from-red-500 to-orange-600 rounded-xl p-4 mr-4">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-900">Upload Failed</h3>
              <p class="text-gray-600">We couldn't process your file</p>
            </div>
          </div>
          <div class="mt-4 flex space-x-3">
            <button
              @click="analyticsStore.clearCurrentUpload(); analysisPrompt = ''"
              class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-300 font-medium"
            >
              Try Again
            </button>
            <button
              @click="selectedFile = null"
              class="px-6 py-3 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-lg hover:from-red-600 hover:to-orange-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl"
            >
              Clear File
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalyticsStore } from '@/stores/analytics'
import { api } from '@/services/api'
import {
  FINANCIAL_DASHBOARD_REPORT_PROMPT,
  REPORT_PROMPT_TEMPLATES,
} from '@/constants/reportPrompts'
import {
  DocumentArrowUpIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const analyticsStore = useAnalyticsStore()

// Reactive state
const selectedFile = ref<File | null>(null)
const analysisPrompt = ref(FINANCIAL_DASHBOARD_REPORT_PROMPT)
const reportPromptTemplates = REPORT_PROMPT_TEMPLATES
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const promptConfig = ref<Record<string, any> | null>(null)
const selectedTemplate = ref('three_page_standard')
const reportLength = ref('standard')
const detailLevel = ref('balanced')
const outputFormat = ref('pdf')
const selectedSections = ref<string[]>([
  'executive_summary',
  'statistical_highlights',
  'financial_ratios',
  'risk_assessment',
  'recommendations',
])

const templateOptions = computed(() => {
  const templates = promptConfig.value?.templates || {}
  return Object.entries(templates).map(([id, template]: [string, any]) => ({
    id,
    label: template?.name || id.replace(/_/g, ' '),
    sections: Array.isArray(template?.sections) ? template.sections : [],
  }))
})

const applyTemplateSections = (templateId: string) => {
  const template = templateOptions.value.find((item) => item.id === templateId)
  if (template?.sections?.length) {
    selectedSections.value = [...template.sections]
  }
}

const sectionOptions = computed(() => {
  const sections = promptConfig.value?.section_library || {}
  return Object.entries(sections).map(([key, section]: [string, any]) => ({
    key,
    title: section?.title || key.replace(/_/g, ' '),
    description: section?.description || '',
  }))
})

// Editing state for section titles/descriptions
const editingSectionKey = ref<string | null>(null)
const editTitle = ref('')
const editDescription = ref('')
const savingSection = ref(false)

const openSectionEditor = (section: { key: string; title: string; description: string }) => {
  editingSectionKey.value = section.key
  editTitle.value = section.title || ''
  editDescription.value = section.description || ''
}

const closeSectionEditor = () => {
  editingSectionKey.value = null
  editTitle.value = ''
  editDescription.value = ''
}

const saveSectionEdits = async () => {
  if (!editingSectionKey.value) return
  savingSection.value = true
  try {
    // Get current config
    const cfgResp = await api.getReportPromptConfig()
    const cfg = cfgResp.data && cfgResp.data.config ? cfgResp.data.config : {}
    cfg.section_library = cfg.section_library || {}
    cfg.section_library[editingSectionKey.value] = cfg.section_library[editingSectionKey.value] || {}
    cfg.section_library[editingSectionKey.value].title = editTitle.value
    cfg.section_library[editingSectionKey.value].description = editDescription.value

    // Persist
    await api.updateReportPromptConfig(cfg)

    // Refresh local promptConfig
    const refreshed = await api.getReportPromptConfig()
    promptConfig.value = refreshed.data?.config || promptConfig.value
    closeSectionEditor()
  } catch (err) {
    // show error in UI
    console.error('Failed to save section edits', err)
    // Optionally set a top-level error state
  } finally {
    savingSection.value = false
  }
}

const applyPromptTemplate = (template: { prompt: string; id: string; sections?: string[] }) => {
  analysisPrompt.value =
    template.prompt || FINANCIAL_DASHBOARD_REPORT_PROMPT
  if (templateOptions.value.some((item) => item.id === template.id)) {
    selectedTemplate.value = template.id
  }
  if (template.sections?.length) {
    selectedSections.value = [...template.sections]
  }
}

const selectAllSections = () => {
  selectedSections.value = sectionOptions.value.map((section) => section.key)
}

const clearSections = () => {
  selectedSections.value = []
}

const resetReportSettings = () => {
  selectedTemplate.value = 'three_page_standard'
  reportLength.value = 'standard'
  detailLevel.value = 'balanced'
  outputFormat.value = 'pdf'
  applyTemplateSections('three_page_standard')
}

// Methods
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
  }
}

const handleDrop = (event: DragEvent) => {
  dragOver.value = false
  const files = event.dataTransfer?.files
  if (files && files[0]) {
    selectedFile.value = files[0]
  }
}

const openFilePicker = () => {
  fileInput.value?.click()
}

const handleUpload = async () => {
  if (!selectedFile.value || !analysisPrompt.value.trim()) return

  try {
    const reportOptions = {
      template: selectedTemplate.value,
      sections: selectedSections.value,
      include_sections: selectedSections.value,
      exclude_sections: sectionOptions.value
        .map((section) => section.key)
        .filter((sectionKey) => !selectedSections.value.includes(sectionKey)),
      length: reportLength.value,
      detail_level: detailLevel.value,
      output_format: outputFormat.value,
    }

    const data = await analyticsStore.uploadFile(
      selectedFile.value,
      analysisPrompt.value,
      '',
      reportOptions,
    )
    const id = data?.id || data?.report_id || analyticsStore.currentReport
    if (id && analyticsStore.uploadStatus === 'completed') {
      router.push(`/reports/${id}`)
    }
  } catch {
    // Error shown in upload status panel via analyticsStore.errors.upload
  }
}

// No mock data function - using real API endpoints only

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const loadPromptConfig = async () => {
  try {
    const config = await analyticsStore.fetchReportPromptConfig()
    promptConfig.value = config

    // If backend provides a system prompt template, use it as the analysis prompt
    if (promptConfig.value?.system_prompt_template) {
      analysisPrompt.value = promptConfig.value.system_prompt_template
    }

    const defaultTemplate = templateOptions.value.find((template) => template.id === 'three_page_standard')
      || templateOptions.value[0]
    if (defaultTemplate) {
      selectedTemplate.value = defaultTemplate.id
      if (defaultTemplate.sections?.length) {
        selectedSections.value = [...defaultTemplate.sections]
      }
    }
  } catch (error) {
    console.error('Failed to load prompt config:', error)
  }
}

onMounted(() => {
  loadPromptConfig()
})

watch(selectedTemplate, (templateId) => {
  applyTemplateSections(templateId)
})
</script>
