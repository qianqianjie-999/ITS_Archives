<template>
  <header class="app-header">
    <div class="header-left">
      <button class="sidebar-toggle" @click="$emit('toggleSidebar')">
        <el-icon :size="20"><Menu /></el-icon>
      </button>
      <div class="logo">
        <div class="logo-icon-box">
          <el-icon :size="20" class="logo-icon"><MapLocation /></el-icon>
        </div>
        <span class="logo-text">汶上县智能交通档案系统</span>
      </div>
    </div>

    <div class="header-right">
      <div class="header-time">
        <el-icon :size="14"><Clock /></el-icon>
        <span>{{ currentTime }}</span>
      </div>

      <div class="header-actions">
        <button class="action-btn" title="帮助" @click="showHelp = true">
          <el-icon :size="18"><QuestionFilled /></el-icon>
        </button>
        <button class="action-btn" @click="showNotification">
          <el-icon :size="18"><Bell /></el-icon>
          <span class="badge" v-if="notificationCount > 0">{{ notificationCount }}</span>
        </button>
        <button class="action-btn" @click="showSettings">
          <el-icon :size="18"><Setting /></el-icon>
        </button>
      </div>

      <div class="user-menu">
        <div class="user-info">
          <div class="avatar-box">
            <el-avatar :size="34" :icon="User">
              {{ userStore.user?.display_name?.charAt(0) }}
            </el-avatar>
            <div class="status-dot"></div>
          </div>
          <div class="user-detail">
            <span class="user-name">{{ userStore.user?.display_name }}</span>
            <span class="user-role">{{ roleText }}</span>
          </div>
        </div>
        <el-dropdown trigger="click">
          <el-icon :size="16" class="dropdown-icon"><ArrowDown /></el-icon>
          <template #dropdown>
            <el-dropdown-menu class="dark-dropdown">
              <el-dropdown-item @click="goToProfile">
                <el-icon><User /></el-icon>
                <span>个人资料</span>
              </el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">
                <el-icon><ArrowRight /></el-icon>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
  <HelpDialog v-model="showHelp" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { Menu, MapLocation, Bell, Setting, ArrowDown, User, ArrowRight, Clock, QuestionFilled } from '@element-plus/icons-vue'
import HelpDialog from '@/components/HelpDialog.vue'

defineEmits(['toggleSidebar'])

const router = useRouter()
const userStore = useUserStore()

const notificationCount = ref(0)
const currentTime = ref('')
const showHelp = ref(false)

const roleText = computed(() => {
  switch (userStore.user?.role) {
    case 'admin': return '管理员'
    case 'editor': return '编辑'
    default: return '查看'
  }
})

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

let timeInterval: number

onMounted(() => {
  updateTime()
  timeInterval = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})

function showNotification() {
  ElMessageBox.alert('暂无新通知', '通知')
}

function showSettings() {
  ElMessageBox.alert('设置功能开发中', '设置')
}

function goToProfile() {
  ElMessageBox.alert('个人资料功能开发中', '个人资料')
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.logout()
    router.push('/login')
  } catch {
    // 用户取消
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 48px;
  padding: 0 $spacing-md;
  width: 100%;
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
  border-bottom: 1px solid $border-color;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.25);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.sidebar-toggle {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: $radius-sm;
  cursor: pointer;
  color: $text-secondary;
  transition: all $transition-fast;

  &:hover {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: $spacing-sm;

  .logo-icon-box {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, rgba($primary-color, 0.2) 0%, rgba($primary-color, 0.05) 100%);
    border: 1px solid rgba($primary-color, 0.3);
    border-radius: $radius-sm;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-icon {
    color: $primary-color;
  }

  .logo-text {
    font-size: $font-size-md;
    font-weight: 600;
    color: $text-primary;
    letter-spacing: 1px;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
}

.header-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: $font-size-xs;
  color: $text-secondary;
  padding: $spacing-xs $spacing-sm;
  background: rgba($primary-color, 0.05);
  border-radius: $radius-sm;
  border: 1px solid rgba($primary-color, 0.1);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.action-btn {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: $radius-sm;
  cursor: pointer;
  color: $text-secondary;
  transition: all $transition-fast;

  &:hover {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
  }

  .badge {
    position: absolute;
    top: 4px;
    right: 4px;
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    font-size: 10px;
    font-weight: 600;
    color: #fff;
    background: $error-color;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.user-menu {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-xs $spacing-sm;
  border-left: 1px solid $border-color;

  .user-info {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }

  .avatar-box {
    position: relative;

    .status-dot {
      position: absolute;
      bottom: 0;
      right: 0;
      width: 10px;
      height: 10px;
      background: $success-color;
      border: 2px solid #0f172a;
      border-radius: 50%;
    }
  }

  .user-detail {
    display: flex;
    flex-direction: column;

    .user-name {
      font-size: $font-size-sm;
      font-weight: 500;
      color: $text-primary;
    }

    .user-role {
      font-size: $font-size-xs;
      color: $primary-color;
    }
  }

  .dropdown-icon {
    color: $text-secondary;
    cursor: pointer;
    transition: all $transition-fast;

    &:hover {
      color: $primary-color;
    }
  }
}

:deep(.dark-dropdown) {
  background: #111827 !important;
  border: 1px solid $border-color;

  .el-dropdown-menu__item {
    color: $text-primary;

    &:hover {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }
}
</style>