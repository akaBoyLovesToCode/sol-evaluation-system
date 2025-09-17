import axios from 'axios'
import { ElMessage } from 'element-plus'

// Helper function to get translations - will be dynamically imported
let getTranslation = null

// Initialize translation function
const initTranslation = async () => {
  if (!getTranslation) {
    try {
      const { createI18n } = await import('vue-i18n')
      const en = await import('../locales/en.json')
      const zh = await import('../locales/zh.json')
      const ko = await import('../locales/ko.json')

      const i18n = createI18n({
        legacy: false,
        locale: localStorage.getItem('locale') || 'zh',
        fallbackLocale: 'en',
        messages: {
          en: en.default,
          zh: zh.default,
          ko: ko.default,
        },
      })

      getTranslation = (key) => {
        // Update locale if it changed
        const currentLocale = localStorage.getItem('locale') || 'zh'
        if (i18n.global.locale.value !== currentLocale) {
          i18n.global.locale.value = currentLocale
        }
        return i18n.global.t(key)
      }
    } catch (error) {
      console.warn('Failed to initialize i18n for API:', error)
      // Fallback function
      getTranslation = (key) => {
        const fallbackMessages = {
          'api.errors.forbidden': '权限不足',
          'api.errors.notFound': '请求的资源不存在',
          'api.errors.serverError': '服务器内部错误',
          'api.errors.networkError': '网络连接失败',
          'api.errors.requestFailed': '请求失败',
        }
        return fallbackMessages[key] || key
      }
    }
  }
  return getTranslation
}

// Get translation with fallback
const t = (key) => {
  if (getTranslation) {
    return getTranslation(key)
  }
  // Fallback messages for immediate use
  const fallbackMessages = {
    'api.errors.forbidden': '权限不足',
    'api.errors.notFound': '请求的资源不存在',
    'api.errors.serverError': '服务器内部错误',
    'api.errors.networkError': '网络连接失败',
    'api.errors.requestFailed': '请求失败',
  }
  return fallbackMessages[key] || key
}

// Initialize translation on module load
initTranslation()

// Determine API base URL
const getApiBaseUrl = () => {
  // Try build-time environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }

  // Fallback: construct from current location for production
  if (window.location.hostname.includes('railway.app')) {
    return 'https://sol-evaluation-system.up.railway.app/api'
  }

  // Default for local development
  return '/api'
}

const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器（no auth headers）
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error),
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const { response, config } = error

    if (response) {
      switch (response.status) {
        case 403:
          ElMessage.error(t('api.errors.forbidden'))
          break
        case 404:
          ElMessage.error(t('api.errors.notFound'))
          break
        case 500:
          ElMessage.error(t('api.errors.serverError'))
          break
        default:
          ElMessage.error(response.data?.message || t('api.errors.requestFailed'))
      }
    } else {
      ElMessage.error(t('api.errors.networkError'))
    }

    return Promise.reject(error)
  },
)

export default api
