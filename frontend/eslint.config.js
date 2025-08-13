import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import prettierConfig from 'eslint-config-prettier'
import globals from 'globals'

export default [
  // 1. Base JavaScript rules
  js.configs.recommended,

  // 2. Vue recommended ruleset
  ...pluginVue.configs['flat/recommended'],

  // 3. Global ignore patterns
  {
    ignores: ['node_modules/**', 'dist/**', 'build/**', '*.min.js', 'offline-store/**'],
  },

  // 4. Main rules configuration (for all JS/Vue files)
  {
    files: ['**/*.{js,mjs,cjs,vue}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      'no-unused-vars': ['warn', { args: 'after-used', ignoreRestSiblings: true }],
      'no-prototype-builtins': 'error',
      'no-case-declarations': 'error',
      'vue/multi-word-component-names': 'off',
      'vue/no-unused-vars': 'warn',
      'vue/component-definition-name-casing': ['error', 'PascalCase'],
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    },
  },

  // 5. Configuration for Test Files
  {
    files: ['**/*.test.js', '**/*.spec.js', '**/__tests__/**', 'tests/**/*.js'],
    languageOptions: {
      globals: {
        ...globals.jest,
      },
    },
  }, // <--- 在这里加上逗号！

  // 6. Prettier Configuration (must be last)
  prettierConfig,
]
