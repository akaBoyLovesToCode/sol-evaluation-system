<template>
  <el-config-provider :locale="elLocale">
    <div id="app" class="app-root">
      <header class="topbar">
        <div class="topbar-left">
          <span class="topbar-mark">Sol.</span>
          <div class="topbar-title">
            <span class="topbar-product">S.T.A.R.</span>
          </div>
        </div>
        <div class="topbar-right">
          <el-dropdown class="lang-dropdown" trigger="click" @command="changeLanguage">
            <button
              class="lang-chip"
              type="button"
              :aria-label="`Switch language: ${currentLanguage}`"
            >
              <span class="lang-dot" aria-hidden="true"></span>
              <span>{{ currentLanguage }}</span>
            </button>
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
// Element Plus locales for config provider
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

</script>

<style>
.app-root {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
  color: #1f2937;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 0;
  padding: 0 20px;
  background: #ffffff;
  border-bottom: 1px solid #d8dee8;
  box-shadow: none;
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-mark,
.lang-chip {
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d8dee8;
  background: #ffffff;
  color: #344054;
  border-radius: 6px;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
  font-weight: 650;
  line-height: 1;
  box-shadow: none;
}

.topbar-mark {
  width: 36px;
  padding: 0;
  background: #172554;
  border-color: #172554;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
}

.lang-chip:hover {
  background: #f8fafc;
  border-color: #b9c3d3;
  color: #1f2937;
}

.topbar-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
  min-width: 0;
}

.topbar-product {
  color: #111827;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.topbar-section {
  color: #667085;
  font-size: 12px;
  font-weight: 600;
}

.lang-chip {
  gap: 6px;
  min-width: 82px;
  padding: 0 9px;
}

.lang-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #155eef;
}

.lang-dropdown {
  display: inline-flex;
  align-items: center;
}

.content {
  padding: 16px 20px 20px;
}
</style>
