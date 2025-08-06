<template>
  <div class="layout-container">
    <el-container class="h-screen">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar">
        <div class="logo-container">
          <div v-if="!isCollapse" class="logo">{{ $t("system.name") }}</div>
          <div v-else class="logo-mini">EVAL</div>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :unique-opened="true"
          router
          class="sidebar-menu"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <template #title>{{ $t("menu.dashboard") }}</template>
          </el-menu-item>

          <el-menu-item index="/evaluations">
            <el-icon><Document /></el-icon>
            <template #title>{{ $t("menu.evaluations") }}</template>
          </el-menu-item>

          <el-menu-item index="/reports">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>{{ $t("menu.reports") }}</template>
          </el-menu-item>

          <el-menu-item index="/messages">
            <el-icon><Message /></el-icon>
            <template #title>{{ $t("menu.messages") }}</template>
            <el-badge
              :value="unreadCount"
              :hidden="unreadCount === 0"
              class="message-badge"
            />
          </el-menu-item>

          <el-menu-item index="/users" v-if="authStore.isGroupLeader">
            <el-icon><User /></el-icon>
            <template #title>{{ $t("menu.users") }}</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部栏 -->
        <el-header class="header">
          <div class="header-left">
            <el-button
              :icon="isCollapse ? Expand : Fold"
              @click="toggleSidebar"
              text
            />
            <el-breadcrumb separator="/">
              <el-breadcrumb-item
                v-for="item in breadcrumbs"
                :key="item.path"
                :to="item.path"
              >
                {{ item.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="header-right">
            <!-- 语言切换 -->
            <el-dropdown @command="changeLanguage">
              <el-button text>
                <el-icon><Setting /></el-icon>
                {{ currentLanguage }}
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="zh">中文</el-dropdown-item>
                  <el-dropdown-item command="en">English</el-dropdown-item>
                  <el-dropdown-item command="ko">한국어</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>

            <!-- 用户菜单 -->
            <el-dropdown @command="handleUserCommand">
              <div class="user-info">
                <el-avatar :size="32" :src="authStore.user?.avatar">
                  {{ authStore.user?.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="username">{{ authStore.user?.username }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    {{ $t("menu.profile") }}
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    {{ $t("menu.logout") }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useI18n } from "vue-i18n"
import { useAuthStore } from "../stores/auth"
import {
  House,
  Document,
  DataAnalysis,
  Message,
  User,
  Expand,
  Fold,
  Setting,
  ArrowDown,
  SwitchButton,
} from "@element-plus/icons-vue"

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const authStore = useAuthStore()

const isCollapse = ref(false)
const unreadCount = ref(0)

const activeMenu = computed(() => {
  const { matched } = route
  if (matched.length === 0) return "/"

  let path = matched[matched.length - 1].path
  if (path === "/evaluations/new" || path.startsWith("/evaluations/")) {
    return "/evaluations"
  }
  return path
})

const currentLanguage = computed(() => {
  const langMap = {
    zh: "中文",
    en: "English",
    ko: "한국어",
  }
  return langMap[locale.value] || "中文"
})

const breadcrumbs = computed(() => {
  const matched = route.matched.filter((item) => item.meta && item.meta.title)
  const breadcrumbs = []

  matched.forEach((item) => {
    breadcrumbs.push({
      path: item.path,
      title: t(item.meta.title),
    })
  })

  return breadcrumbs
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
  localStorage.setItem("sidebarCollapse", isCollapse.value)
}

const changeLanguage = (lang) => {
  locale.value = lang
  localStorage.setItem("locale", lang)
}

const handleUserCommand = (command) => {
  switch (command) {
    case "profile":
      router.push("/profile")
      break
    case "logout":
      authStore.logout()
      router.push("/login")
      break
  }
}

// 获取未读消息数量
const fetchUnreadCount = async () => {
  try {
    // TODO: 实现获取未读消息数量的API调用
    unreadCount.value = 0
  } catch (error) {
    console.error("Failed to fetch unread count:", error)
  }
}

onMounted(() => {
  // 恢复侧边栏状态
  const savedCollapse = localStorage.getItem("sidebarCollapse")
  if (savedCollapse !== null) {
    isCollapse.value = JSON.parse(savedCollapse)
  }

  // 获取未读消息数量
  fetchUnreadCount()
})

// 监听路由变化，更新未读消息数量
watch(
  () => route.path,
  () => {
    if (route.path === "/messages") {
      fetchUnreadCount()
    }
  },
)
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.sidebar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.08);
  border-radius: 0 20px 20px 0;
  margin: 8px 0;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.logo-container {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(248, 250, 252, 0.8);
}

.logo {
  color: #1e293b;
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  letter-spacing: 1px;
}

.logo-mini {
  color: #1e293b;
  font-size: 16px;
  font-weight: 700;
  text-align: center;
}

.sidebar-menu {
  border: none;
  background: transparent;
  padding: 16px 0;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #64748b;
  margin: 4px 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-weight: 500;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  min-height: 48px;
  padding: 0 16px;
}

/* 移除::before伪元素，避免背景冲突 */

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(59, 130, 246, 0.1) !important;
  color: #3b82f6;
  transform: translateX(4px);
}

.sidebar-menu :deep(.el-menu-item:hover .el-icon) {
  color: #3b82f6;
}

/* 确保菜单项内容正确对齐 */
.sidebar-menu :deep(.el-menu-item .el-menu-item__title) {
  flex: 1;
}

/* 重置Element Plus默认样式 */
.sidebar-menu :deep(.el-menu-item) {
  height: auto !important;
  line-height: normal !important;
}

.sidebar-menu :deep(.el-menu-item.is-active)::before {
  display: none;
}

/* 收起状态下的菜单项样式 */
.sidebar-menu.el-menu--collapse :deep(.el-menu-item) {
  padding: 0 !important;
  margin: 4px 8px !important;
  width: 48px !important;
  height: 48px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  position: relative !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item .el-icon) {
  margin-right: 0 !important;
  margin-left: 0 !important;
  font-size: 20px !important;
  position: absolute !important;
  left: 50% !important;
  top: 50% !important;
  transform: translate(-50%, -50%) !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item.is-active) {
  background: #3b82f6 !important;
  color: #fff !important;
  border-radius: 12px !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item.is-active .el-icon) {
  color: #fff !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item:hover) {
  background: rgba(59, 130, 246, 0.1) !important;
  color: #3b82f6 !important;
}

.sidebar-menu.el-menu--collapse :deep(.el-menu-item:hover .el-icon) {
  color: #3b82f6 !important;
}

/* 移除hover::before，使用直接背景 */

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #3b82f6 !important;
  color: #fff !important;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
}

.sidebar-menu :deep(.el-menu-item.is-active .el-icon) {
  color: #fff !important;
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 18px;
  transition: color 0.3s ease;
  flex-shrink: 0;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  margin: 8px 16px 0 16px;
  border-radius: 20px;
  height: 70px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-left .el-button {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.header-left .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-right .el-button {
  border-radius: 12px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.header-right .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px 16px;
  border-radius: 16px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.user-info:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.user-info .el-avatar {
  border: 2px solid rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.user-info:hover .el-avatar {
  border-color: #3b82f6;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
}

.username {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
}

.main-content {
  background: transparent;
  padding: 24px;
  margin: 0 16px 16px 0;
  border-radius: 20px;
  overflow-y: auto;
}

.main-content::-webkit-scrollbar {
  width: 8px;
}

.main-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb {
  background: #3b82f6;
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: #2563eb;
}

.message-badge {
  position: absolute;
  top: 8px;
  right: 8px;
}

.message-badge :deep(.el-badge__content) {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(240, 147, 251, 0.4);
}

/* 面包屑样式 */
.header-left :deep(.el-breadcrumb) {
  font-weight: 500;
}

.header-left :deep(.el-breadcrumb__item) {
  color: #7f8c8d;
}

.header-left :deep(.el-breadcrumb__item:last-child) {
  color: #2c3e50;
  font-weight: 600;
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.el-dropdown-menu__item) {
  border-radius: 8px;
  margin: 4px;
  transition: all 0.3s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background: rgba(59, 130, 246, 0.1);
  transform: translateX(4px);
}
</style>
