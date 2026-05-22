import create from 'zustand'

interface AuthState{
  user: any | null
  accessToken: string | null
  setUser: (u:any|null)=>void
  setToken: (t:string|null)=>void
}

export const useAuthStore = create<AuthState>((set)=>({
  user: null,
  accessToken: null,
  setUser: (u)=>set({user:u}),
  setToken: (t)=>set({accessToken:t})
}))
