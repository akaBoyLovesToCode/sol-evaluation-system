import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref({
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    role: 'admin',
    name: 'Admin User'
  })
  const token = ref('dev-token')
  
  const isAuthenticated = computed(() => true)
  
  const hasRole = (roles) => {
    if (!user.value) return false
    if (typeof roles === 'string') roles = [roles]
    return roles.includes(user.value.role)
  }
  
  const canApprove = computed(() => true)
  
  const isAdmin = computed(() => true)
  const isGroupLeader = computed(() => true)
  const isPartLeader = computed(() => true)
  
  const login = async () => {
    return { success: true }
  }
  
  const logout = () => {
    // Do nothing in dev mode
  }
  
  const checkAuth = async () => {
    return true
  }
  
  const updateProfile = async (profileData) => {
    user.value = { ...user.value, ...profileData }
    return { success: true }
  }
  
  const changePassword = async () => {
    return { success: true }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    hasRole,
    canApprove,
    isAdmin,
    isGroupLeader,
    isPartLeader,
    login,
    logout,
    checkAuth,
    updateProfile,
    changePassword
  }
}) 