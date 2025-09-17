<template>
  <el-config-provider :locale="elLocale">
  <div id="app" class="app-root">
    <header class="topbar">
      <div class="left">
        <el-button class="back-btn" text :icon="ArrowLeft" @click="goBack" />
      </div>
      <div class="right">
        <el-select v-model="localeValue" size="small" class="lang-select" @change="saveLocale">
          <el-option label="中文" value="zh" />
          <el-option label="English" value="en" />
          <el-option label="한국어" value="ko" />
        </el-select>
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
import { ArrowLeft } from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import enLocale from 'element-plus/es/locale/lang/en'
import koLocale from 'element-plus/es/locale/lang/ko'

const { locale } = useI18n()
const localeValue = ref(localStorage.getItem('locale') || 'zh')

const saveLocale = (val) => {
  localStorage.setItem('locale', val)
  // Update i18n global locale reactively
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

.left, .right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn :deep(.el-icon) {
  font-size: 18px;
}
.lang-select {
  min-width: 120px;
}

.content {
  padding: 20px;
}
</style>
