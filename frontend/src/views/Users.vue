<template>
  <div class="users-page">
    <div class="page-header">
      <div class="header-left">
        <h1>{{ $t("users.title") }}</h1>
        <p>{{ $t("users.description") }}</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateUserDialog">
          <el-icon><Plus /></el-icon>
          {{ $t("users.addUser") }}
        </el-button>
      </div>
    </div>

    <!-- User Search and Filter -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item :label="$t('users.username')">
          <el-input
            v-model="searchForm.username"
            :placeholder="$t('users.placeholders.username')"
            clearable
          />
        </el-form-item>
        <el-form-item :label="$t('users.role')">
          <el-select
            v-model="searchForm.role"
            :placeholder="$t('users.placeholders.role')"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="role in roles"
              :key="role.value"
              :label="$t(`users.roles.${role.value}`)"
              :value="role.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('users.status')">
          <el-select
            v-model="searchForm.status"
            :placeholder="$t('users.placeholders.status')"
            clearable
            style="width: 120px"
          >
            <el-option :label="$t('users.active')" value="active" />
            <el-option :label="$t('users.inactive')" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="searchUsers">
            <el-icon><Search /></el-icon>
            {{ $t("common.search") }}
          </el-button>
          <el-button @click="resetSearch">
            <el-icon><Refresh /></el-icon>
            {{ $t("common.reset") }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- User Table -->
    <el-card class="table-card" v-loading="loading">
      <el-table
        :data="users"
        style="width: 100%"
        border
        :header-cell-style="{ textAlign: 'center' }"
        :cell-style="{ textAlign: 'center' }"
      >
        <el-table-column
          prop="username"
          :label="$t('users.username')"
          min-width="120"
        />
        <el-table-column
          prop="full_name"
          :label="$t('users.fullName')"
          min-width="150"
        />
        <el-table-column
          prop="email"
          :label="$t('users.email')"
          min-width="200"
        />
        <el-table-column
          prop="department"
          :label="$t('users.department')"
          min-width="150"
        />
        <el-table-column
          prop="position"
          :label="$t('users.position')"
          min-width="150"
        />
        <el-table-column :label="$t('users.role')" min-width="120">
          <template #default="scope">
            <el-tag :type="getRoleTagType(scope.row.role)">
              {{ $t(`users.roles.${scope.row.role}`) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('users.status')" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{
                scope.row.is_active ? $t("users.active") : $t("users.inactive")
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          :label="$t('common.operations')"
          width="250"
          fixed="right"
        >
          <template #default="scope">
            <el-button size="small" type="primary" @click="editUser(scope.row)">
              {{ $t("common.edit") }}
            </el-button>
            <el-button
              size="small"
              :type="scope.row.is_active ? 'warning' : 'success'"
              :disabled="scope.row.role === 'admin'"
              @click="toggleUserStatus(scope.row)"
            >
              {{
                scope.row.is_active
                  ? $t("users.deactivate")
                  : $t("users.activate")
              }}
            </el-button>
            <el-button
              size="small"
              type="danger"
              :disabled="scope.row.role === 'admin'"
              @click="showDeleteUserDialog(scope.row)"
            >
              {{ $t("common.delete") }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalUsers"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create/Edit User Dialog -->
    <el-dialog
      v-model="userDialogVisible"
      :title="isEditing ? $t('users.editUser') : $t('users.createUser')"
      width="500px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-position="top"
      >
        <el-form-item :label="$t('users.username')" prop="username">
          <el-input
            v-model="userForm.username"
            :placeholder="$t('users.placeholders.username')"
            :disabled="isEditing"
          />
        </el-form-item>

        <el-form-item :label="$t('users.fullName')" prop="full_name">
          <el-input
            v-model="userForm.full_name"
            :placeholder="$t('users.placeholders.fullName')"
          />
        </el-form-item>

        <el-form-item :label="$t('users.email')" prop="email">
          <el-input
            v-model="userForm.email"
            :placeholder="$t('users.placeholders.email')"
          />
        </el-form-item>

        <el-form-item :label="$t('users.department')" prop="department">
          <el-input
            v-model="userForm.department"
            :placeholder="$t('users.placeholders.department')"
          />
        </el-form-item>

        <el-form-item :label="$t('users.position')" prop="position">
          <el-input
            v-model="userForm.position"
            :placeholder="$t('users.placeholders.position')"
          />
        </el-form-item>

        <el-form-item :label="$t('users.role')" prop="role">
          <el-select
            v-model="userForm.role"
            :placeholder="$t('users.placeholders.role')"
            style="width: 100%"
          >
            <el-option
              v-for="role in roles"
              :key="role.value"
              :label="$t(`users.roles.${role.value}`)"
              :value="role.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('users.status')">
          <el-switch
            v-model="userForm.is_active"
            :active-text="$t('users.active')"
            :inactive-text="$t('users.inactive')"
          />
        </el-form-item>

        <el-form-item
          v-if="!isEditing"
          :label="$t('users.password')"
          prop="password"
        >
          <el-input
            v-model="userForm.password"
            type="password"
            :placeholder="$t('users.placeholders.password')"
            show-password
          />
        </el-form-item>

        <el-form-item
          v-if="!isEditing"
          :label="$t('users.confirmPassword')"
          prop="confirmPassword"
        >
          <el-input
            v-model="userForm.confirmPassword"
            type="password"
            :placeholder="$t('users.placeholders.confirmPassword')"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="userDialogVisible = false">
            {{ $t("common.cancel") }}
          </el-button>
          <el-button type="primary" @click="saveUser">
            {{ $t("common.save") }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Delete User Confirmation Dialog -->
    <el-dialog
      v-model="deleteDialogVisible"
      :title="$t('users.confirmDelete')"
      width="400px"
    >
      <p>
        {{ $t("users.deleteWarning", { username: userToDelete?.username }) }}
      </p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">
            {{ $t("common.cancel") }}
          </el-button>
          <el-button type="danger" @click="confirmDeleteUser">
            {{ $t("common.delete") }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import api from '../utils/api'

const { t } = useI18n()

// Data
const loading = ref(false)
const users = ref([])
const totalUsers = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const userDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const isEditing = ref(false)
const userToDelete = ref(null)

// Search form
const searchForm = reactive({
  username: '',
  role: '',
  status: '',
})

// User form
const userForm = reactive({
  id: null,
  username: '',
  full_name: '',
  email: '',
  department: '',
  position: '',
  role: 'user',
  is_active: true,
  password: '',
  confirmPassword: '',
})

// Form reference
const userFormRef = ref(null)

// Available roles
const roles = [
  { value: 'user', label: t('users.roles.user') },
  { value: 'part_leader', label: t('users.roles.part_leader') },
  { value: 'group_leader', label: t('users.roles.group_leader') },
  { value: 'admin', label: t('users.roles.admin') },
]

// Form validation rules
const userFormRules = computed(() => ({
  username: [
    {
      required: true,
      message: t('validation.required', { field: t('users.username') }),
      trigger: 'blur',
    },
    {
      min: 3,
      max: 20,
      message: t('validation.length', { min: 3, max: 20 }),
      trigger: 'blur',
    },
  ],
  full_name: [
    {
      required: true,
      message: t('validation.required', { field: t('users.fullName') }),
      trigger: 'blur',
    },
    {
      min: 2,
      max: 50,
      message: t('validation.length', { min: 2, max: 50 }),
      trigger: 'blur',
    },
  ],
  email: [
    {
      required: true,
      message: t('validation.required', { field: t('users.email') }),
      trigger: 'blur',
    },
    { type: 'email', message: t('users.invalidEmail'), trigger: 'blur' },
  ],
  role: [
    {
      required: true,
      message: t('validation.required', { field: t('users.role') }),
      trigger: 'change',
    },
  ],
  password: !isEditing.value
    ? [
        {
          required: true,
          message: t('validation.required', { field: t('users.password') }),
          trigger: 'blur',
        },
        {
          min: 8,
          message: t('validation.minLength', { min: 8 }),
          trigger: 'blur',
        },
        {
          pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
          message: t('profile.passwordRequirements'),
          trigger: 'blur',
        },
      ]
    : [],
  confirmPassword: !isEditing.value
    ? [
        {
          required: true,
          message: t('validation.required', {
            field: t('users.confirmPassword'),
          }),
          trigger: 'blur',
        },
        {
          validator: (_, value, callback) => {
            if (value !== userForm.password) {
              callback(new Error(t('profile.passwordMismatch')))
            } else {
              callback()
            }
          },
          trigger: 'blur',
        },
      ]
    : [],
}))

// Fetch users on component mount
onMounted(() => {
  fetchUsers()
})

// Fetch users from API
const fetchUsers = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,
      username: searchForm.username || undefined,
      role: searchForm.role || undefined,
      is_active:
        searchForm.status === 'active'
          ? true
          : searchForm.status === 'inactive'
            ? false
            : undefined,
    }

    const response = await api.get('/users', { params })
    users.value = response.data.data.users
    totalUsers.value = response.data.data.total
  } catch (error) {
    ElMessage.error(t('users.fetchError'))
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

// Search users
const searchUsers = () => {
  currentPage.value = 1
  fetchUsers()
}

// Reset search form
const resetSearch = () => {
  searchForm.username = ''
  searchForm.role = ''
  searchForm.status = ''
  currentPage.value = 1
  fetchUsers()
}

// Handle page size change
const handleSizeChange = (size) => {
  pageSize.value = size
  fetchUsers()
}

// Handle current page change
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchUsers()
}

// Show create user dialog
const showCreateUserDialog = () => {
  isEditing.value = false
  resetUserForm()
  userDialogVisible.value = true
}

// Edit user
const editUser = (user) => {
  isEditing.value = true
  userForm.id = user.id
  userForm.username = user.username
  userForm.full_name = user.full_name || user.fullName
  userForm.email = user.email
  userForm.department = user.department || ''
  userForm.position = user.position || ''
  userForm.role = user.role
  userForm.is_active = user.is_active
  userForm.password = ''
  userForm.confirmPassword = ''
  userDialogVisible.value = true
}

// Reset user form
const resetUserForm = () => {
  userForm.id = null
  userForm.username = ''
  userForm.full_name = ''
  userForm.email = ''
  userForm.department = ''
  userForm.position = ''
  userForm.role = 'user'
  userForm.is_active = true
  userForm.password = ''
  userForm.confirmPassword = ''
}

// Save user (create or update)
const saveUser = async () => {
  if (!userFormRef.value) return

  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        loading.value = true

        const userData = {
          username: userForm.username,
          fullName: userForm.full_name,
          email: userForm.email,
          department: userForm.department,
          position: userForm.position,
          role: userForm.role,
          is_active: userForm.is_active,
        }

        if (!isEditing.value) {
          userData.password = userForm.password
        }

        if (isEditing.value) {
          await api.put(`/users/${userForm.id}`, userData)
          ElMessage.success(t('users.updateSuccess'))
        } else {
          await api.post('/users', userData)
          ElMessage.success(t('users.createSuccess'))
        }

        userDialogVisible.value = false
        fetchUsers()
      } catch (error) {
        const errorMessage =
          error.response?.data?.message ||
          error.response?.data?.error ||
          (isEditing.value ? t('users.updateError') : t('users.createError'))
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}

// Toggle user status (activate/deactivate)
const toggleUserStatus = async (user) => {
  try {
    const action = user.is_active ? 'deactivate' : 'activate'

    await ElMessageBox.confirm(
      t(`users.${action}Warning`, { username: user.username }),
      t(`users.confirm${action.charAt(0).toUpperCase() + action.slice(1)}`),
      {
        confirmButtonText: t(`users.${action}`),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      },
    )

    await api.put(`/users/${user.id}/status`, {
      is_active: !user.is_active,
    })

    ElMessage.success(t(`users.${action}Success`))
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('users.statusUpdateError'))
    }
  }
}

// Show delete user dialog
const showDeleteUserDialog = (user) => {
  userToDelete.value = user
  deleteDialogVisible.value = true
}

// Confirm delete user
const confirmDeleteUser = async () => {
  try {
    await api.delete(`/users/${userToDelete.value.id}`)
    ElMessage.success(t('users.deleteSuccess'))
    deleteDialogVisible.value = false
    fetchUsers()
  } catch {
    ElMessage.error(t('users.deleteError'))
  }
}

// Get role tag type
const getRoleTagType = (role) => {
  const typeMap = {
    admin: 'danger',
    group_leader: 'warning',
    part_leader: 'success',
    user: 'info',
  }
  return typeMap[role] || 'info'
}
</script>

<style scoped>
.users-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #2c3e50;
}

.header-left p {
  margin: 0;
  color: #7f8c8d;
}

.filter-card {
  transform: none;
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.table-card {
  transform: none;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Remove transform effect on operation buttons */
.table-card :deep(.el-button) {
  transform: none;
  transition:
    background-color 0.3s ease,
    border-color 0.3s ease;
}

.table-card :deep(.el-button:hover) {
  transform: none;
}
</style>
