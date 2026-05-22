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

export default api
export { API_BASE }
