import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [ElementPlusResolver({ importStyle: 'css', resolveIcons: true })],
      dts: false,
    }),
    AutoImport({
      resolvers: [ElementPlusResolver({ importStyle: 'css', resolveIcons: true })],
      dts: false,
    }),
    visualizer({
      filename: 'stats.html',
      template: 'treemap',
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('echarts')) return 'vendor-echarts'
            if (id.includes('element-plus') || id.includes('@element-plus'))
              return 'vendor-element-plus'
            if (
              id.includes('/vue') ||
              id.includes('vue-router') ||
              id.includes('pinia') ||
              id.includes('vue-i18n')
            ) {
              return 'vendor-vue'
            }
            return 'vendor'
          }
        },
      },
    },
  },
})
