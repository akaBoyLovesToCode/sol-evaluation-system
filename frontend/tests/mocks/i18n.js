// Mock for vue-i18n
export const createI18n = () => ({
  global: {
    t: (key, values) => {
      // Simple implementation that returns the key with values if provided
      if (values) {
        let result = key
        Object.keys(values).forEach(valueKey => {
          result = result.replace(`{${valueKey}}`, values[valueKey])
        })
        return result
      }
      return key
    },
    locale: 'en',
    fallbackLocale: 'en',
  },
})

// Mock useI18n composable
export const useI18n = () => ({
  t: (key, values) => {
    // Simple implementation that returns the key with values if provided
    if (values) {
      let result = key
      Object.keys(values).forEach(valueKey => {
        result = result.replace(`{${valueKey}}`, values[valueKey])
      })
      return result
    }
    return key
  },
  locale: 'en',
})