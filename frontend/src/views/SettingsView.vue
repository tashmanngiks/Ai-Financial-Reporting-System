<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Modern Header -->
    <div class="bg-white text-gray-900 border-b border-gray-200 shadow-sm">
      <div class="container mx-auto px-6 py-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold">Settings</h1>
            <p class="text-gray-600 mt-2">Configure your Dura Capital Analytics platform</p>
          </div>
          <div class="flex items-center space-x-3">
            <div class="bg-gray-100 rounded-lg px-4 py-2">
              <span class="text-sm font-medium text-gray-700">System Status</span>
              <span class="ml-2 inline-flex items-center">
                <svg class="w-2 h-2 bg-green-500 rounded-full" fill="currentColor" viewBox="0 0 20 20">
                  <circle cx="10" cy="10" r="10"/>
                </svg>
                <span class="ml-1 text-sm text-gray-600">Operational</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8">
      <!-- Quick Actions Bar -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-8">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              @click="activeTab = 'system'"
              :class="activeTab === 'system' ? 'bg-white text-primary-700 border-primary-200 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-4 py-2 rounded-lg font-medium transition-colors border border-transparent"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1.31 1.31 0 01.952-.804l1.432-1.432a1 1 0 00-.474-1.474L5.31 9.397zM11.25 12.25a.75.75 0 100 1.5.75.75 0 000-1.5z"/>
              </svg>
              System Configuration
            </button>
            <button
              @click="activeTab = 'preferences'"
              :class="activeTab === 'preferences' ? 'bg-white text-primary-700 border-primary-200 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-4 py-2 rounded-lg font-medium transition-colors border border-transparent"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 3.5a1.5 1.5 0 013 0V4a1 1 0 001 1h3a1 1 0 001-1v-.5a1.5 1.5 0 013 0V4a1 1 0 001-1h3a1 1 0 001-1v-.5a1.5 1.5 0 013 0V4a1 1 0 001-1h3a1 1 0 001-1v-.5a1.5 1.5 0 013 0V4a1 1 0 001-1h3a1 1 0 001-1v-.5a1.5 1.5 0 013 0z"/>
              </svg>
              User Preferences
            </button>
            <button
              @click="activeTab = 'data'"
              :class="activeTab === 'data' ? 'bg-white text-primary-700 border-primary-200 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-4 py-2 rounded-lg font-medium transition-colors border border-transparent"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
              </svg>
              Data Management
            </button>
            <button
              @click="activeTab = 'advanced'"
              :class="activeTab === 'advanced' ? 'bg-white text-primary-700 border-primary-200 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
              class="px-4 py-2 rounded-lg font-medium transition-colors border border-transparent"
            >
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 7H7v6h6V7z"/>
                <path d="M7 9a2 2 0 11-4 0 2 2 0 014 0zM12.65 17a1 1 0 00.707-.293l.354-.353a1 1 0 00-1.414-1.414l-.353.353a1 1 0 00-.707.293z"/>
              </svg>
              Advanced
            </button>
          </div>
          <div class="flex items-center space-x-3">
            <span class="text-sm text-gray-500">Last saved:</span>
            <span class="text-sm font-medium text-gray-900">{{ lastSaved || 'Never' }}</span>
          </div>
        </div>
      </div>

      <!-- Settings Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Sidebar - Settings Navigation -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Quick Settings</h3>
            <div class="space-y-3">
              <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-gray-900">AI Features</div>
                    <div class="text-sm text-gray-500">{{ settings.enableAI ? 'Enabled' : 'Disabled' }}</div>
                  </div>
                  <div class="p-2 rounded-full" :class="settings.enableAI ? 'bg-green-100' : 'bg-gray-200'">
                    <svg class="w-4 h-4" :class="settings.enableAI ? 'text-green-600' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4zm1-9a1 1 0 10-2 0v1a1 1 0 002 0V3z"/>
                    </svg>
                  </div>
                </div>
              </div>
              <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-gray-900">Notifications</div>
                    <div class="text-sm text-gray-500">{{ preferences.emailNotifications ? 'On' : 'Off' }}</div>
                  </div>
                  <div class="p-2 rounded-full" :class="preferences.emailNotifications ? 'bg-green-100' : 'bg-gray-200'">
                    <svg class="w-4 h-4" :class="preferences.emailNotifications ? 'text-green-600' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6z"/>
                    </svg>
                  </div>
                </div>
              </div>
              <div class="p-3 rounded-lg bg-gray-50 border border-gray-200">
                <div class="flex items-center justify-between">
                  <div>
                    <div class="font-medium text-gray-900">Data Retention</div>
                    <div class="text-sm text-gray-500">{{ settings.retentionDays }} days</div>
                  </div>
                  <div class="p-2 rounded-full bg-white">
                    <svg class="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M7 9a2 2 0 012-2h6a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content Area -->
        <div class="lg:col-span-2 p-6 rounded-lg" style="background-color: #E3F2FD;">
          <!-- System Configuration Tab -->
          <div v-if="activeTab === 'system'" class="space-y-6">
            <!-- API Configuration -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200">
              <div class="px-6 py-4 border-b border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-white rounded-lg mr-3 shadow-sm">
                    <svg class="w-6 h-6 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1.31 1.31 0 01.952-.804l1.432-1.432a1 1 0 00-.474-1.474L5.31 9.397zM11.25 12.25a.75.75 0 100 1.5.75.75 0 000-1.5z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">API Configuration</h3>
                    <p class="text-sm text-gray-600">Configure API endpoints and authentication</p>
                  </div>
                </div>
              </div>
              <div class="p-6 space-y-6">
                <div>
                  <label for="api-url" class="block text-sm font-medium text-gray-700 mb-2">API Base URL</label>
                  <div class="relative">
                    <input
                      id="api-url"
                      v-model="settings.apiUrl"
                      type="url"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                      placeholder="http://localhost:8000/api"
                    />
                    <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                      <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13.586 3.586a2 2 0 112.828 0l-2.829 2.829a2 2 0 01-2.828 2.828v1.657l1.414 1.414a1 1 0 101.414 1.414l1.414-1.414a1 1 0 00-1.414-1.414l-1.414 1.414H12a2 2 0 01-2 2v-6a2 2 0 012-2h6z"/>
                      </svg>
                    </div>
                  </div>
                </div>
                <div>
                  <label for="timeout" class="block text-sm font-medium text-gray-700 mb-2">Request Timeout (seconds)</label>
                  <input
                    id="timeout"
                    v-model.number="settings.timeout"
                    type="number"
                    min="5"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    placeholder="30"
                  />
                </div>
              </div>
            </div>

            <!-- AI Configuration -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200">
              <div class="px-6 py-4 border-b border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-white rounded-lg mr-3 shadow-sm">
                    <svg class="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 7H7v6h6V7z"/>
                      <path d="M7 9a2 2 0 11-4 0 2 2 0 014 0zM10 13a2 2 0 100 4 2 2 0 000-4z"/>
                      <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM3 7a1 1 0 000 2h2a1 1 0 100-2H3zM17 7a1 1 0 100 2h2a1 1 0 100-2h-2zM3 11a1 1 0 100 2h2a1 1 0 100-2H3zM17 11a1 1 0 100 2h2a1 1 0 100-2h-2z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">AI Configuration</h3>
                    <p class="text-sm text-gray-600">Configure AI-powered insights and analysis</p>
                  </div>
                </div>
              </div>
            <div class="p-6">
              <form @submit.prevent class="space-y-6">
                <div>
                  <label for="openai-api-key" class="block text-sm font-medium text-gray-700 mb-2">OpenAI API Key</label>
                  <div class="relative">
                    <input
                      id="openai-api-key"
                      v-model="settings.openaiApiKey"
                      :type="showApiKey ? 'text' : 'password'"
                      :autocomplete="showApiKey ? 'off' : 'new-password'"
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors pr-12"
                      placeholder="sk-..."
                    />
                    <button
                      type="button"
                      @click="showApiKey = !showApiKey"
                      class="absolute inset-y-0 right-0 flex items-center pr-3"
                    >
                      <svg v-if="showApiKey" class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4zm1-9a1 1 0 10-2 0v1a1 1 0 002 0V3z"/>
                      </svg>
                      <svg v-else class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4zm1-9a1 1 0 10-2 0v1a1 1 0 002 0V3z"/>
                      </svg>
                    </button>
                  </div>
                  <p class="text-sm text-gray-500 mt-2">
                    Used for generating AI insights. Leave empty to disable AI features.
                  </p>
                </div>
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <label for="enable-ai" class="flex items-center cursor-pointer">
                      <input
                        id="enable-ai"
                        v-model="settings.enableAI"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 w-4 h-4"
                      />
                      <span class="ml-3 text-sm font-medium text-gray-700">Enable AI Features</span>
                    </label>
                    <p class="text-sm text-gray-500 mt-1">Enable AI-powered financial analysis</p>
                  </div>
                  <div class="p-3 rounded-full" :class="settings.enableAI ? 'bg-green-100' : 'bg-gray-200'">
                    <svg class="w-6 h-6" :class="settings.enableAI ? 'text-green-600' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0L4-4a1 1 0 00-1.414-1.414L10 10.586z"/>
                    </svg>
                  </div>
                </div>
              </form>
            </div>
          </div>
          </div>

          <!-- User Preferences Tab -->
          <div v-if="activeTab === 'preferences'" class="space-y-6">
            <!-- Display Settings -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200">
              <div class="px-6 py-4 border-b border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-white rounded-lg mr-3 shadow-sm">
                    <svg class="w-6 h-6 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-1.414 1.414a1 1 0 101.414 1.414l1.414-1.414zm-9.9 2.121a1 1 0 10-1.414 1.415l1.414-1.415a1 1 0 011.414 0l-1.414 1.414zM3 11a1 1 0 011 1v1a1 1 0 11-2 0v-1A1 1 0 011-1zm14 0a1 1 0 011 1v1a1 1 0 11-2 0v-1A1 1 0 011-1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1A1 1 0 011-1z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">User Preferences</h3>
                    <p class="text-sm text-gray-600">Customize your experience and interface</p>
                  </div>
                </div>
              </div>
              <div class="p-6 space-y-6">
                <div>
                  <label for="page-size" class="block text-sm font-medium text-gray-700 mb-2">Default page size</label>
                  <select id="page-size" v-model="preferences.pageSize" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                    <option value="10">10 items per page</option>
                    <option value="20">20 items per page</option>
                    <option value="50">50 items per page</option>
                    <option value="100">100 items per page</option>
                  </select>
                </div>
                <div>
                  <label for="date-format" class="block text-sm font-medium text-gray-700 mb-2">Date format</label>
                  <select id="date-format" v-model="preferences.dateFormat" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  </select>
                </div>
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <label for="email-notifications" class="flex items-center cursor-pointer">
                      <input
                        id="email-notifications"
                        v-model="preferences.emailNotifications"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 w-4 h-4"
                      />
                      <span class="ml-3 text-sm font-medium text-gray-700">Email notifications</span>
                    </label>
                    <p class="text-sm text-gray-500 mt-1">Receive email updates about your reports</p>
                  </div>
                  <div class="p-3 rounded-full" :class="preferences.emailNotifications ? 'bg-green-100' : 'bg-gray-200'">
                    <svg class="w-6 h-6" :class="preferences.emailNotifications ? 'text-green-600' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6z"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Data Management Tab -->
          <div v-if="activeTab === 'data'" class="space-y-6">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200">
              <div class="px-6 py-4 border-b border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-white rounded-lg mr-3 shadow-sm">
                    <svg class="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">Data Management</h3>
                    <p class="text-sm text-gray-600">Manage data retention and export settings</p>
                  </div>
                </div>
              </div>
              <div class="p-6 space-y-6">
                <div>
                  <label for="retention-days" class="block text-sm font-medium text-gray-700 mb-2">Delete reports older than</label>
                  <div class="flex space-x-2">
                    <input
                      id="retention-days"
                      v-model.number="settings.retentionDays"
                      type="number"
                      min="1"
                      max="365"
                      class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                      placeholder="90"
                    />
                    <select id="retention-unit" v-model="settings.retentionUnit" class="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors">
                      <option value="days">days</option>
                      <option value="weeks">weeks</option>
                      <option value="months">months</option>
                    </select>
                  </div>
                </div>
                <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <label for="auto-cleanup" class="flex items-center cursor-pointer">
                      <input
                        id="auto-cleanup"
                        v-model="settings.autoCleanup"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 focus:ring-primary-500 w-4 h-4"
                      />
                      <span class="ml-3 text-sm font-medium text-gray-700">Auto cleanup</span>
                    </label>
                    <p class="text-sm text-gray-500 mt-1">Automatically delete old reports</p>
                  </div>
                  <div class="p-3 rounded-full" :class="settings.autoCleanup ? 'bg-green-100' : 'bg-gray-200'">
                    <svg class="w-6 h-6" :class="settings.autoCleanup ? 'text-green-600' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M7 9a2 2 0 11-4 0 2 2 0 014 0zM12.65 17a1 1 0 00.707-.293l.354-.353a1 1 0 00-1.414-1.414l-.353.353a1 1 0 00-.707.293z"/>
                    </svg>
                  </div>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    @click="exportAllData"
                    class="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 transition-colors"
                    :disabled="loading.export"
                  >
                    <svg v-if="!loading.export" class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M3 17a1 1 0 011-1h12a1 1 0 011 1v1a1 1 0 11-2 0v-1A1 1 0 011-1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1A1 1 0 011 1zm14 0a1 1 0 011 1v1a1 1 0 11-2 0v-1A1 1 0 011-1z"/>
                    </svg>
                    <span v-if="!loading.export">Export All Data</span>
                    <span v-else class="flex items-center">
                      <div class="animate-spin w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
                      Exporting...
                    </span>
                  </button>
                  <button
                    @click="clearAllData"
                    class="flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 transition-colors"
                    :disabled="loading.clear"
                  >
                    <svg v-if="!loading.clear" class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 2a1 1 0 000 2h6a1 1 0 000-2H9z"/>
                      <path d="M7 9a2 2 0 11-4 0 2 2 0 014 0zM12.65 17a1 1 0 00.707-.293l.354-.353a1 1 0 00-1.414-1.414l-.353.353a1 1 0 00-.707.293z"/>
                    </svg>
                    <span v-if="!loading.clear">Clear All Data</span>
                    <span v-else class="flex items-center">
                      <div class="animate-spin w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
                      Clearing...
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Advanced Tab -->
          <div v-if="activeTab === 'advanced'" class="space-y-6">
            <div class="bg-white rounded-lg shadow-sm border border-gray-200">
              <div class="px-6 py-4 border-b border-gray-200">
                <div class="flex items-center">
                  <div class="p-2 bg-white rounded-lg mr-3 shadow-sm">
                    <svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 7H7v6h6V7z"/>
                      <path d="M7 9a2 2 0 11-4 0 2 2 0 014 0zM12.65 17a1 1 0 00.707-.293l.354-.353a1 1 0 00-1.414-1.414l-.353.353a1 1 0 00-.707.293z"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-gray-900">Advanced Settings</h3>
                    <p class="text-sm text-gray-600">System configuration and information</p>
                  </div>
                </div>
              </div>
              <div class="p-6 space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="p-4 bg-gray-50 rounded-lg">
                    <dt class="text-sm font-medium text-gray-500">Version</dt>
                    <dd class="mt-1 text-sm text-gray-900">v1.0.0</dd>
                  </div>
                  <div class="p-4 bg-gray-50 rounded-lg">
                    <dt class="text-sm font-medium text-gray-500">Environment</dt>
                    <dd class="mt-1 text-sm text-gray-900">Development</dd>
                  </div>
                  <div class="p-4 bg-gray-50 rounded-lg">
                    <dt class="text-sm font-medium text-gray-500">Database</dt>
                    <dd class="mt-1 text-sm text-gray-900">SQLite</dd>
                  </div>
                  <div class="p-4 bg-gray-50 rounded-lg">
                    <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                    <dd class="mt-1 text-sm text-gray-900">{{ new Date().toLocaleDateString() }}</dd>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
      </div>

      <!-- Save Actions -->
      <div class="flex justify-end space-x-3 mt-8">
        <button
          @click="resetSettings"
          class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 transition-colors"
        >
          Reset to Defaults
        </button>
        <button
          @click="saveSettings"
          class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 transition-colors"
          :disabled="loading.save"
        >
          <span v-if="!loading.save">Save Settings</span>
          <span v-else class="flex items-center">
            <div class="animate-spin w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
            Saving...
          </span>
        </button>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

// Reactive state
const loading = reactive({
  save: false,
  export: false,
  clear: false
})

const activeTab = ref('system')
const showApiKey = ref(false)
const lastSaved = ref('')

const settings = reactive({
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) / 1000 || 30,
  openaiApiKey: '',
  enableAI: import.meta.env.VITE_ENABLE_AI_FEATURES === 'true',
  retentionDays: 90,
  retentionUnit: 'days',
  autoCleanup: false,
  defaultExportFormat: 'json',
  includeRawData: false
})

const preferences = reactive({
  darkMode: false,
  pageSize: 20,
  dateFormat: 'MM/DD/YYYY',
  emailNotifications: true,
  taskNotifications: true
})

// Methods
const saveSettings = async () => {
  loading.save = true
  try {
    // Save settings to localStorage
    localStorage.setItem('analytics_settings', JSON.stringify(settings))
    localStorage.setItem('analytics_preferences', JSON.stringify(preferences))
    lastSaved.value = new Date().toLocaleString()
    // Persist the last-saved timestamp so it survives navigation/reloads
    try {
      localStorage.setItem('analytics_last_saved', lastSaved.value)
    } catch (e) {
      // ignore storage errors
    }

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('Failed to save settings:', error)
  } finally {
    loading.save = false
  }
}

const resetSettings = () => {
  if (confirm('Are you sure you want to reset all settings to defaults?')) {
    // Reset to default values
    Object.assign(settings, {
      apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
      timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) / 1000 || 30,
      openaiApiKey: '',
      enableAI: import.meta.env.VITE_ENABLE_AI_FEATURES === 'true',
      retentionDays: 90,
      retentionUnit: 'days',
      autoCleanup: false,
      defaultExportFormat: 'json',
      includeRawData: false
    })

    Object.assign(preferences, {
      darkMode: false,
      pageSize: 20,
      dateFormat: 'MM/DD/YYYY',
      emailNotifications: true,
      taskNotifications: true
    })

    localStorage.removeItem('analytics_settings')
    localStorage.removeItem('analytics_preferences')
    localStorage.removeItem('analytics_last_saved')
    lastSaved.value = ''
  }
}

const exportAllData = async () => {
  loading.export = true
  try {
    // Simulate export process
    await new Promise(resolve => setTimeout(resolve, 2000))
  } catch (error) {
    console.error('Export failed:', error)
  } finally {
    loading.export = false
  }
}

const clearAllData = async () => {
  if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
    loading.clear = true
    try {
      // Simulate data clearing
      await new Promise(resolve => setTimeout(resolve, 2000))
    } catch (error) {
      console.error('Clear failed:', error)
    } finally {
      loading.clear = false
    }
  }
}

// Load saved settings on mount
const loadSettings = () => {
  try {
    const savedSettings = localStorage.getItem('analytics_settings')
    const savedPreferences = localStorage.getItem('analytics_preferences')
    const savedLast = localStorage.getItem('analytics_last_saved')

    if (savedSettings) {
      Object.assign(settings, JSON.parse(savedSettings))
    }

    if (savedPreferences) {
      Object.assign(preferences, JSON.parse(savedPreferences))
    }

    if (savedLast) {
      lastSaved.value = savedLast
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

// Initialize
loadSettings()
</script>
