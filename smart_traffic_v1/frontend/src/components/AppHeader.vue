<template>
  <header class="app-header">
    <div class="header-left">
      <button class="sidebar-toggle" @click="$emit('toggleSidebar')">
        <el-icon :size="20"><Menu /></el-icon>
      </button>
      <div class="logo">
        <el-icon :size="24" class="logo-icon"><MapLocation /></el-icon>
        <span class="logo-text">智能交通档案系统</span>
      </div>
    </div>
    
    <div class="header-right">
      <div class="header-actions">
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
          <el-avatar :size="36" :icon="User">
            {{ userStore.user?.display_name?.charAt(0) }}
          </el-avatar>
          <div class="user-detail">
            <span class="user-name">{{ userStore.user?.display_name }}</span>
            <span class="user-role">{{ roleText }}</span>
          </div>
        </div>
        <el-dropdown trigger="click">
          <el-icon :size="16" class="dropdown-icon"><ArrowDown /></el-icon>
          <template #dropdown>
            <el-dropdown-menu>
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
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { Menu, MapLocation, Bell, Setting, ArrowDown, User, ArrowRight } from '@element-plus/icons-vue'

defineEmits(['toggleSidebar'])

const router = useRouter()
const userStore = useUserStore()

const notificationCount = ref(0)

const roleText = computed(() => {
  switch (userStore.user?.role) {
    case 'admin': return '管理员'
    case 'editor': return '编辑'
    default: return '查看'
  }
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
  height: 64px;
  padding: 0 $spacing-lg;
  background: $bg-card;
  border-bottom: 1px solid $border-light;
  box-shadow: $shadow-sm;
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
    background: $bg-hover;
    color: $text-primary;
  }
}

.logo {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  
  .logo-icon {
    color: $primary-color;
  }
  
  .logo-text {
    font-size: $font-size-md;
    font-weight: 600;
    color: $text-primary;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
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
    background: $bg-hover;
    color: $text-primary;
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
  border-left: 1px solid $border-light;
  
  .user-info {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
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
      color: $text-secondary;
    }
  }
  
  .dropdown-icon {
    color: $text-secondary;
    cursor: pointer;
    
    &:hover {
      color: $text-primary;
    }
  }
}
</style>
