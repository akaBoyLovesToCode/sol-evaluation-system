export default {
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.js$': 'babel-jest',
  },
  moduleFileExtensions: ['vue', 'js', 'json', 'jsx'],
  testMatch: ['**/tests/unit/**/*.spec.js'],
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@testing-library))',
  ],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js',
    '!src/router/index.js',
    '!**/node_modules/**',
  ],
  coverageReporters: ['text', 'lcov'],
  globals: {
    '@vue/vue3-jest': {
      pug: {
        doctype: 'html'
      }
    }
  },
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons']
  }
}