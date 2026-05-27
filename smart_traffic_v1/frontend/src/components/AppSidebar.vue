<template>
  <aside :class="['app-sidebar', { collapsed: isCollapsed }]">
    <div class="sidebar-menu">
      <el-menu
        :default-active="activeMenu"
        router
        :collapse="isCollapsed"
        :unique-opened="true"
        class="sidebar-nav"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </el-menu-item>

        <el-menu-item index="/intersections">
          <el-icon><Location /></el-icon>
          <span>路口管理</span>
        </el-menu-item>

        <el-menu-item index="/parking-enforcements">
          <el-icon><Camera /></el-icon>
          <span>违停管理</span>
        </el-menu-item>

        <el-menu-item index="/checkpoints">
          <el-icon><Camera /></el-icon>
          <span>卡口</span>
        </el-menu-item>

        <el-menu-item index="/backend-devices">
          <el-icon><Camera /></el-icon>
          <span>后端设备</span>
        </el-menu-item>

        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计报表</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="sidebar-footer">
      <button class="collapse-btn" @click="$emit('toggle')" :title="isCollapsed ? '展开菜单' : '收起菜单'">
        <el-icon :size="16"><component :is="isCollapsed ? ArrowRight : ArrowLeft" /></el-icon>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { House, Folder, Location, ArrowLeft, ArrowRight, Camera, DataAnalysis } from '@element-plus/icons-vue'

defineProps<{
  isCollapsed: boolean
}>()

defineEmits(['toggle'])

const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/intersections')) return '/intersections'
  if (path.startsWith('/parking-enforcements')) return '/parking-enforcements'
  if (path.startsWith('/checkpoints')) return '/checkpoints'
  if (path.startsWith('/backend-devices')) return '/backend-devices'
  if (path.startsWith('/projects')) return '/projects'
  if (path.startsWith('/statistics')) return '/statistics'
  return path
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.app-sidebar {
  width: 200px;
  min-width: 200px;
  height: calc(100vh - 64px);
  background: linear-gradient(180deg, #001529 0%, #091a2e 100%);
  color: #fff;
  transition: all $transition-normal;
  position: relative;
  overflow: hidden;

  &.collapsed {
    width: 64px;
    min-width: 64px;
  }
}

.sidebar-menu {
  padding: $spacing-md 0;
}

.sidebar-nav {
  background: transparent;
  border-right: none;

  .el-menu-item {
    color: rgba(255, 255, 255, 0.7);
    margin: 0 $spacing-sm;
    border-radius: $radius-md;
    transition: all $transition-fast;

    &:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
    }

    &.is-active {
      background: rgba(24, 144, 255, 0.3);
      color: #fff;

      .el-menu-item__icon {
        color: $primary-color;
      }
    }

    .el-menu-item__icon {
      color: rgba(255, 255, 255, 0.7);
      margin-right: $spacing-sm;

      &:hover {
        color: #fff;
      }
    }
  }
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: $spacing-md;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.collapse-btn {
  width: 100%;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: $radius-sm;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all $transition-fast;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
  }
}
</style>