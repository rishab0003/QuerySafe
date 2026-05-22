"use client"
import { create } from 'zustand'

/* ─── Auth Store ──────────────────────────────────────────── */
export interface AuthUser {
  id: string
  email: string
  full_name?: string
  department: string
  role: string
  approval_status?: string
  is_active?: boolean
}

interface AuthState {
  token: string | null
  user: AuthUser | null
  setToken: (t: string | null) => void
  setUser: (u: AuthUser | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== 'undefined' ? (localStorage.getItem('qs_token') || null) : null,
  user: null,
  setToken: (t) => {
    try { if (t) localStorage.setItem('qs_token', t); else localStorage.removeItem('qs_token') } catch (e) {}
    set({ token: t })
  },
  setUser: (u) => set({ user: u }),
  logout: () => {
    try {
      localStorage.removeItem('qs_token')
      localStorage.removeItem('qs_refresh')
      localStorage.removeItem('qs_temp_token')
    } catch (e) {}
    set({ token: null, user: null })
  }
}))

/* ─── Chat Store ──────────────────────────────────────────── */
export interface ChatMessage {
  id: string
  role: 'user' | 'agent'
  text: string
  sql?: string
  confidence?: number
  tablesUsed?: string[]
  reasoning?: string
  results?: any[]
  rowCount?: number
  queryTimeMs?: number
  timestamp: number
}

interface ChatState {
  messages: ChatMessage[]
  isLoading: boolean
  connectionId: string | null
  sessionId: string
  language: string
  addMessage: (msg: ChatMessage) => void
  setLoading: (v: boolean) => void
  setConnectionId: (id: string | null) => void
  setLanguage: (lang: string) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  connectionId: null,
  sessionId: `session_${Date.now()}`,
  language: 'english',
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setLoading: (v) => set({ isLoading: v }),
  setConnectionId: (id) => set({ connectionId: id }),
  setLanguage: (lang) => set({ language: lang }),
  clearMessages: () => set({ messages: [] }),
}))

/* ─── UI Store ────────────────────────────────────────────── */
interface UIState {
  sidebarOpen: boolean
  settingsOpen: boolean
  explainData: any | null
  toggleSidebar: () => void
  toggleSettings: () => void
  setExplainData: (d: any | null) => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  settingsOpen: false,
  explainData: null,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toggleSettings: () => set((s) => ({ settingsOpen: !s.settingsOpen })),
  setExplainData: (d) => set({ explainData: d }),
}))

export default useAuthStore
