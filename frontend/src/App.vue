<template>
  <el-config-provider :locale="elLocale">
    <div id="app" class="app-root">
      <header class="topbar">
        <div class="left">
          <el-button class="back-btn" text @click="goBack">
            <template #icon><ArrowLeft /></template>
          </el-button>
        </div>
        <div class="right">
          <el-dropdown class="lang-dropdown" @command="changeLanguage">
            <el-button text class="lang-button">
              <el-icon><Setting /></el-icon>
              <span class="lang-label">{{ currentLanguage }}</span>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh">中文</el-dropdown-item>
                <el-dropdown-item command="en">English</el-dropdown-item>
                <el-dropdown-item command="ko">한국어</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>
  </el-config-provider>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
// Icon components are globally registered via Element Plus
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import enLocale from 'element-plus/es/locale/lang/en'
import koLocale from 'element-plus/es/locale/lang/ko'

const { locale } = useI18n()
const localeValue = ref(localStorage.getItem('locale') || 'zh')

const changeLanguage = (val) => {
  localeValue.value = val
  localStorage.setItem('locale', val)
  locale.value = val
}

onMounted(() => {
  // Ensure i18n picks up stored locale on boot
  if (locale.value !== localeValue.value) {
    locale.value = localeValue.value
  }
})

const elLocale = computed(() => {
  switch (locale.value) {
    case 'en':
      return enLocale
    case 'ko':
      return koLocale
    default:
      return zhCn
  }
})

const currentLanguage = computed(() => {
  switch (locale.value) {
    case 'en':
      return 'English'
    case 'ko':
      return '한국어'
    default:
      return '中文'
  }
})

const goBack = () => {
  window.location.href = 'http://109.154.11.128'
}
</script>

<style>
.app-root {
  min-height: 100vh;
  background: #f5f6f8;
  display: flex;
  flex-direction: column;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 12px 20px;
  padding: 10px 14px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
}

.left,
.right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn :deep(.el-icon) {
  font-size: 18px;
}
.lang-dropdown .lang-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #606266;
}
.lang-dropdown .lang-button:hover {
  color: #303133;
}
.lang-label {
  font-weight: 500;
}

.content {
  padding: 20px;
}
</style>
