import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

// Attach auth token from localStorage if available
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('qs_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})
// Response interceptor to handle token refresh automatically
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as any
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('qs_refresh') : null
      if (refreshToken) {
        try {
          const refreshRes = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refreshToken })
          const { access_token, refresh_token } = refreshRes.data
          if (access_token) {
            localStorage.setItem('qs_token', access_token)
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          if (refresh_token) {
            localStorage.setItem('qs_refresh', refresh_token)
          }
          return api(originalRequest)
        } catch (e) {
          // Refresh failed – clear stored tokens
          localStorage.removeItem('qs_token')
          localStorage.removeItem('qs_refresh')
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
export { API_BASE }
