<template>
  <div class="user-list">
    <div class="page-header">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理系统用户账户</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <div class="panel">
      <div class="panel-header">
        <h3 class="panel-title">用户列表</h3>
      </div>
      <div class="table-container">
        <el-table :data="users" border :loading="loading">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="display_name" label="显示名称" />
          <el-table-column prop="role" label="角色">
            <template #default="scope">
              <el-tag :type="getRoleTagType(scope.row.role)">
                {{ getRoleLabel(scope.row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
                {{ scope.row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="last_login" label="最后登录">
            <template #default="scope">
              {{ scope.row.last_login ? formatDate(scope.row.last_login) : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="openEditDialog(scope.row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(scope.row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="用户名" prop="username" v-if="!editing">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码" v-if="!editing || showPassword">
          <el-input type="password" v-model="form.password" placeholder="留空则不修改密码" />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="form.display_name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="管理员" value="admin" />
            <el-option label="编辑员" value="editor" />
            <el-option label="查看员" value="viewer" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item v-if="editing">
          <el-checkbox v-model="showPassword">修改密码</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { userApi, type User, type UserCreate, type UserUpdate } from '@/api/users'

const users = ref<User[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editing = ref(false)
const showPassword = ref(false)

const form = reactive({
  id: 0,
  username: '',
  password: '',
  display_name: '',
  role: 'viewer' as 'admin' | 'editor' | 'viewer',
  is_active: true
})

const dialogTitle = computed(() => editing.value ? '编辑用户' : '添加用户')

const roleLabels: Record<string, string> = {
  admin: '管理员',
  editor: '编辑员',
  viewer: '查看员'
}

function getRoleLabel(role: string) {
  return roleLabels[role] || role
}

function getRoleTagType(role: string) {
  if (role === 'admin') return 'danger'
  if (role === 'editor') return 'warning'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function fetchUsers() {
  loading.value = true
  try {
    users.value = await userApi.list()
  } catch (error) {
    console.error('获取用户列表失败', error)
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  editing.value = false
  showPassword.value = false
  form.id = 0
  form.username = ''
  form.password = ''
  form.display_name = ''
  form.role = 'viewer'
  form.is_active = true
  dialogVisible.value = true
}

function openEditDialog(user: User) {
  editing.value = true
  showPassword.value = false
  form.id = user.id
  form.username = user.username
  form.password = ''
  form.display_name = user.display_name || ''
  form.role = user.role
  form.is_active = user.is_active
  dialogVisible.value = true
}

async function saveUser() {
  try {
    if (!editing.value) {
      const createData: UserCreate = {
        username: form.username,
        password: form.password,
        display_name: form.display_name || undefined,
        role: form.role
      }
      await userApi.create(createData)
    } else {
      const updateData: UserUpdate = {
        display_name: form.display_name || undefined,
        role: form.role,
        is_active: form.is_active
      }
      if (showPassword.value && form.password) {
        updateData.password = form.password
      }
      await userApi.update(form.id, updateData)
    }
    dialogVisible.value = false
    await fetchUsers()
  } catch (error) {
    console.error('保存用户失败', error)
  }
}

function confirmDelete(user: User) {
  if (confirm(`确定要删除用户 "${user.username}" 吗？`)) {
    deleteUser(user.id)
  }
}

async function deleteUser(id: number) {
  try {
    await userApi.delete(id)
    await fetchUsers()
  } catch (error) {
    console.error('删除用户失败', error)
  }
}

fetchUsers()
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.user-list {
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  .page-title { font-size: 22px; font-weight: 600; color: $text-primary; margin: 0; }
  .page-subtitle { font-size: 14px; color: $text-secondary; margin: 4px 0 0; }
}

.panel {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  padding: 20px;
}

.panel-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
  .panel-title { font-size: 15px; font-weight: 600; color: #1a1a2e; margin: 0; }
}

.table-container {
  overflow-x: auto;
}

.el-table {
  --el-table-header-text-color: #8c8c8c;
  --el-table-row-hover-bg-color: #fafafa;
}

.el-button {
  & + .el-button {
    margin-left: 8px;
  }
}
</style>