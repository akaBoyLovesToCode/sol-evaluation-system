<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo-placeholder">
          <div class="logo-text">EVAL</div>
        </div>
        <h1 class="title">{{ $t("login.title") }}</h1>
        <p class="subtitle">{{ $t("login.subtitle") }}</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            :placeholder="$t('login.username')"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            :placeholder="$t('login.password')"
            size="large"
            :prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="loginForm.remember">
            {{ $t("login.remember") }}
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            {{ $t("login.submit") }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { User, Lock, Setting } from "@element-plus/icons-vue";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const { t, locale } = useI18n();
const authStore = useAuthStore();

const loginFormRef = ref();
const loading = ref(false);

const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

const loginRules = {
  username: [
    {
      required: true,
      message: () => t("validation.required", { field: t("login.username") }),
      trigger: "blur",
    },
    {
      min: 3,
      max: 20,
      message: () => t("validation.length", { min: 3, max: 20 }),
      trigger: "blur",
    },
  ],
  password: [
    {
      required: true,
      message: () => t("validation.required", { field: t("login.password") }),
      trigger: "blur",
    },
    {
      min: 6,
      message: () => t("validation.minLength", { min: 6 }),
      trigger: "blur",
    },
  ],
};

const currentLanguage = computed(() => {
  const langMap = {
    zh: "中文",
    en: "English",
    ko: "한국어",
  };
  return langMap[locale.value] || "中文";
});

const handleLogin = async () => {
  if (!loginFormRef.value) return;

  try {
    await loginFormRef.value.validate();
    loading.value = true;

    const result = await authStore.login(
      {
        username: loginForm.username,
        password: loginForm.password,
      },
      t,
    );

    if (result.success) {
      ElMessage.success(t("login.success"));

      // 记住登录状态
      if (loginForm.remember) {
        localStorage.setItem("rememberLogin", "true");
      }

      // 等待一个tick确保状态更新完成
      await nextTick();

      // 使用replace而不是push，避免用户按返回键回到登录页
      router.replace("/");
    } else {
      ElMessage.error(result.message || t("login.failed"));
    }
  } catch (error) {
    console.error("Login validation failed:", error);
  } finally {
    loading.value = false;
  }
};

const changeLanguage = (lang) => {
  locale.value = lang;
  localStorage.setItem("locale", lang);
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle,
    rgba(255, 255, 255, 0.1) 0%,
    transparent 70%
  );
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%,
  100% {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  50% {
    transform: translate(-50%, -50%) rotate(180deg);
  }
}

.login-box {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.2);
  padding: 48px;
  width: 100%;
  max-width: 420px;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.login-box:hover {
  /* Remove x/y movement, keep shadow effect */
  box-shadow: 0 40px 80px rgba(0, 0, 0, 0.25);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-placeholder {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.logo-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 32px;
  border-radius: 16px;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 3px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.logo-text:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
}

.title {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px 0;
}

.subtitle {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
  opacity: 0.8;
}

.login-form {
  margin-bottom: 24px;
}

.login-form .el-form-item {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  /* Remove x/y movement, keep shadow effect */
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  border-color: #667eea;
}

.login-form :deep(.el-checkbox) {
  font-weight: 500;
  color: #2c3e50;
}

.login-form :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
}

.login-button {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.login-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
}

.login-button:active {
  transform: translateY(-1px);
}

.login-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.login-footer .el-button {
  color: #7f8c8d;
  border-radius: 12px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.login-footer .el-button:hover {
  color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

/* 下拉菜单样式 */
.login-footer :deep(.el-dropdown-menu) {
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-footer :deep(.el-dropdown-menu__item) {
  border-radius: 8px;
  margin: 4px;
  transition: all 0.3s ease;
}

.login-footer :deep(.el-dropdown-menu__item:hover) {
  background: linear-gradient(
    135deg,
    rgba(102, 126, 234, 0.1) 0%,
    rgba(118, 75, 162, 0.1) 100%
  );
  transform: translateX(4px);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-container {
    padding: 10px;
  }

  .login-box {
    padding: 30px 20px;
  }

  .title {
    font-size: 24px;
  }

  .subtitle {
    font-size: 14px;
  }
}
</style>
