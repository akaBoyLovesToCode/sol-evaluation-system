<template>
  <div class="profile-page">
    <div class="page-header">
      <h1>{{ $t("profile.title") }}</h1>
      <p>{{ $t("profile.description") }}</p>
    </div>

    <el-row :gutter="20">
      <!-- Personal Information Card -->
      <el-col :xs="24" :md="12">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <h2>{{ $t("profile.personalInfo") }}</h2>
              <el-button
                type="primary"
                :icon="Edit"
                circle
                @click="editPersonalInfo = !editPersonalInfo"
              />
            </div>
          </template>

          <el-form
            ref="personalInfoForm"
            :model="personalInfo"
            :rules="personalInfoRules"
            label-position="top"
            :disabled="!editPersonalInfo"
          >
            <el-form-item :label="$t('profile.fullName')" prop="fullName">
              <el-input
                v-model="personalInfo.fullName"
                :placeholder="$t('profile.placeholders.fullName')"
              />
            </el-form-item>

            <el-form-item :label="$t('profile.email')" prop="email">
              <el-input
                v-model="personalInfo.email"
                :placeholder="$t('profile.placeholders.email')"
              />
            </el-form-item>

            <el-form-item :label="$t('profile.department')" prop="department">
              <el-input
                v-model="personalInfo.department"
                :placeholder="$t('profile.placeholders.department')"
              />
            </el-form-item>

            <el-form-item :label="$t('profile.position')" prop="position">
              <el-input
                v-model="personalInfo.position"
                :placeholder="$t('profile.placeholders.position')"
              />
            </el-form-item>

            <el-form-item :label="$t('profile.role')">
              <el-input v-model="personalInfo.role" disabled />
            </el-form-item>

            <el-form-item v-if="editPersonalInfo">
              <el-button type="primary" @click="updatePersonalInfo">
                {{ $t("profile.updateProfile") }}
              </el-button>
              <el-button @click="cancelPersonalInfoEdit">
                {{ $t("common.cancel") }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Account Settings Card -->
      <el-col :xs="24" :md="12">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <h2>{{ $t("profile.accountSettings") }}</h2>
            </div>
          </template>

          <h3>{{ $t("profile.changePassword") }}</h3>
          <el-form
            ref="passwordForm"
            :model="passwordData"
            :rules="passwordRules"
            label-position="top"
          >
            <el-form-item
              :label="$t('profile.currentPassword')"
              prop="currentPassword"
            >
              <el-input
                v-model="passwordData.currentPassword"
                type="password"
                :placeholder="$t('profile.placeholders.currentPassword')"
                show-password
              />
            </el-form-item>

            <el-form-item :label="$t('profile.newPassword')" prop="newPassword">
              <el-input
                v-model="passwordData.newPassword"
                type="password"
                :placeholder="$t('profile.placeholders.newPassword')"
                show-password
              />
            </el-form-item>

            <el-form-item
              :label="$t('profile.confirmPassword')"
              prop="confirmPassword"
            >
              <el-input
                v-model="passwordData.confirmPassword"
                type="password"
                :placeholder="$t('profile.placeholders.confirmPassword')"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="changePassword">
                {{ $t("profile.changePassword") }}
              </el-button>
            </el-form-item>

            <div class="password-requirements">
              <p>{{ $t("profile.passwordRequirements") }}</p>
            </div>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useAuthStore } from "../stores/auth";
import { Edit } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const authStore = useAuthStore();
const editPersonalInfo = ref(false);

// Form references
const personalInfoForm = ref(null);
const passwordForm = ref(null);

// Personal info form data
const personalInfo = reactive({
  fullName: "",
  email: "",
  department: "",
  position: "",
  role: "",
});

// Password form data
const passwordData = reactive({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
});

// Form validation rules
const personalInfoRules = {
  fullName: [
    {
      required: true,
      message: t("validation.required", { field: t("profile.fullName") }),
      trigger: "blur",
    },
    {
      min: 2,
      max: 50,
      message: t("validation.length", { min: 2, max: 50 }),
      trigger: "blur",
    },
  ],
  email: [
    {
      required: true,
      message: t("validation.required", { field: t("profile.email") }),
      trigger: "blur",
    },
    {
      type: "email",
      message: "Please enter a valid email address",
      trigger: "blur",
    },
  ],
};

const passwordRules = {
  currentPassword: [
    {
      required: true,
      message: t("validation.required", {
        field: t("profile.currentPassword"),
      }),
      trigger: "blur",
    },
  ],
  newPassword: [
    {
      required: true,
      message: t("validation.required", { field: t("profile.newPassword") }),
      trigger: "blur",
    },
    { min: 8, message: t("validation.minLength", { min: 8 }), trigger: "blur" },
    {
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
      message: t("profile.passwordRequirements"),
      trigger: "blur",
    },
  ],
  confirmPassword: [
    {
      required: true,
      message: t("validation.required", {
        field: t("profile.confirmPassword"),
      }),
      trigger: "blur",
    },
    {
      validator: (_, value, callback) => {
        if (value !== passwordData.newPassword) {
          callback(new Error(t("profile.passwordMismatch")));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

// Load user data
onMounted(async () => {
  if (!authStore.user) {
    await authStore.checkAuth();
  }

  if (authStore.user) {
    personalInfo.fullName = authStore.user.fullName || "";
    personalInfo.email = authStore.user.email || "";
    personalInfo.department = authStore.user.department || "";
    personalInfo.position = authStore.user.position || "";
    personalInfo.role = authStore.user.role || "";
  }
});

// Update personal information
const updatePersonalInfo = async () => {
  if (!personalInfoForm.value) return;

  await personalInfoForm.value.validate(async (valid) => {
    if (valid) {
      const result = await authStore.updateProfile({
        fullName: personalInfo.fullName,
        email: personalInfo.email,
        department: personalInfo.department,
        position: personalInfo.position,
      });

      if (result.success) {
        ElMessage.success(t("profile.updateSuccess"));
        editPersonalInfo.value = false;
      } else {
        ElMessage.error(result.message || t("profile.updateError"));
      }
    }
  });
};

// Cancel personal info edit
const cancelPersonalInfoEdit = () => {
  if (authStore.user) {
    personalInfo.fullName = authStore.user.fullName || "";
    personalInfo.email = authStore.user.email || "";
    personalInfo.department = authStore.user.department || "";
    personalInfo.position = authStore.user.position || "";
  }
  editPersonalInfo.value = false;
};

// Change password
const changePassword = async () => {
  if (!passwordForm.value) return;

  await passwordForm.value.validate(async (valid) => {
    if (valid) {
      if (passwordData.newPassword !== passwordData.confirmPassword) {
        ElMessage.error(t("profile.passwordMismatch"));
        return;
      }

      const result = await authStore.changePassword({
        currentPassword: passwordData.currentPassword,
        newPassword: passwordData.newPassword,
      });

      if (result.success) {
        ElMessage.success(t("profile.passwordChangeSuccess"));
        // Reset form
        passwordData.currentPassword = "";
        passwordData.newPassword = "";
        passwordData.confirmPassword = "";
        passwordForm.value.resetFields();
      } else {
        ElMessage.error(result.message || t("profile.passwordChangeError"));
      }
    }
  });
};
</script>

<style scoped>
.profile-page {
  padding: 0;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #2c3e50;
}

.page-header p {
  margin: 0;
  color: #7f8c8d;
}

.profile-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 16px;
  font-weight: 600;
}

.password-requirements {
  margin-top: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
}
</style>
