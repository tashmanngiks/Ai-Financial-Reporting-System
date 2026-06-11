declare module '@/stores/auth' {
  export const useAuthStore: any
}

declare module '@/stores/analytics' {
  export const useAnalyticsStore: any
}

declare module '@/services/api' {
  export const api: any
  export const handleApiError: any
  const defaultExport: any
  export default defaultExport
}
