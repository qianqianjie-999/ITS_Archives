<template>
  <aside :class="['app-sidebar', { collapsed: isCollapsed }]">
    <div class="sidebar-bg"></div>
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

        <el-menu-item index="/sky-net">
          <el-icon><Odometer /></el-icon>
          <span>结构化相机</span>
        </el-menu-item>

        <el-menu-item index="/checkpoints">
          <el-icon><Monitor /></el-icon>
          <span>卡口</span>
        </el-menu-item>

        <el-menu-item index="/backend-devices">
          <el-icon><Setting /></el-icon>
          <span>后端设备</span>
        </el-menu-item>

        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>统计报表</span>
        </el-menu-item>

        <el-menu-item index="/service-ranking">
          <el-icon><Histogram /></el-icon>
          <span>服务排名</span>
        </el-menu-item>

        <el-menu-item index="/memos">
          <el-icon><Edit /></el-icon>
          <span>备忘录</span>
        </el-menu-item>

        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="sidebar-footer">
      <button class="collapse-btn" @click="$emit('toggle')" :title="isCollapsed ? '展开菜单' : '收起菜单'">
        <el-icon :size="16"><component :is="isCollapsed ? DArrowRight : DArrowLeft" /></el-icon>
        <span v-if="!isCollapsed" class="collapse-text">收起</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { House, Folder, Location, DArrowLeft, DArrowRight, Camera, DataAnalysis, User, Monitor, Setting, Odometer, Edit, Histogram } from '@element-plus/icons-vue'

defineProps<{
  isCollapsed: boolean
}>()

defineEmits(['toggle'])

const route = useRoute()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/intersections')) return '/intersections'
  if (path.startsWith('/parking-enforcements')) return '/parking-enforcements'
  if (path.startsWith('/sky-net')) return '/sky-net'
  if (path.startsWith('/checkpoints')) return '/checkpoints'
  if (path.startsWith('/backend-devices')) return '/backend-devices'
  if (path.startsWith('/projects')) return '/projects'
  if (path.startsWith('/statistics')) return '/statistics'
  if (path.startsWith('/memos')) return '/memos'
  if (path.startsWith('/users')) return '/users'
  if (path.startsWith('/service-ranking')) return '/service-ranking'
  return path
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.app-sidebar {
  width: 220px;
  min-width: 220px;
  height: calc(100vh - 64px);
  background: linear-gradient(180deg, #1c273d 0%, #1f2a40 100%);
  color: #fff;
  transition: all $transition-normal;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 200px;
    background: radial-gradient(ellipse at top left, rgba($primary-color, 0.1) 0%, transparent 50%);
    pointer-events: none;
  }

  &.collapsed {
    width: 72px;
    min-width: 72px;
  }
}

.sidebar-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300d4ff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.sidebar-menu {
  padding: $spacing-md 0;
  position: relative;
  z-index: 1;
}

.sidebar-nav {
  background: transparent;
  border-right: none;

  .el-menu-item {
    color: rgba(255, 255, 255, 0.6);
    margin: 4px $spacing-sm;
    padding-left: $spacing-md !important;
    border-radius: $radius-md;
    transition: all $transition-fast;
    height: 44px;
    line-height: 44px;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 0;
      background: $primary-color;
      border-radius: 0 2px 2px 0;
      transition: height 0.3s ease;
    }

    &:hover {
      background: rgba(255, 255, 255, 0.05);
      color: rgba(255, 255, 255, 0.9);

      &::before {
        height: 0;
      }
    }

    &.is-active {
      background: linear-gradient(90deg, rgba($primary-color, 0.2) 0%, rgba($primary-color, 0.05) 100%);
      color: #fff;

      &::before {
        height: 24px;
      }

      .el-menu-item__icon {
        color: $primary-color;
      }
    }

    .el-menu-item__icon {
      color: rgba(255, 255, 255, 0.5);
      margin-right: $spacing-sm;
      transition: all $transition-fast;
    }

    .el-menu-item__title {
      font-size: $font-size-sm;
      font-weight: 500;
    }
  }
}

.sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: $spacing-md;
  z-index: 1;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: $spacing-md;
    right: $spacing-md;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba($primary-color, 0.3), transparent);
  }
}

.collapse-btn {
  width: 100%;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  background: rgba($primary-color, 0.1);
  border: 1px solid rgba($primary-color, 0.2);
  border-radius: $radius-md;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all $transition-fast;

  .collapse-text {
    font-size: $font-size-sm;
  }

  &:hover {
    background: rgba($primary-color, 0.2);
    border-color: rgba($primary-color, 0.4);
    color: $primary-color;
  }
}
</style>