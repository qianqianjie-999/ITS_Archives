<template>
  <div class="dashboard-container">
    <AppHeader @toggleSidebar="sidebarCollapsed = !sidebarCollapsed" />
    <div class="dashboard-body">
      <AppSidebar :isCollapsed="sidebarCollapsed" @toggle="sidebarCollapsed = !sidebarCollapsed" />
      <main class="dashboard-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'

const sidebarCollapsed = ref(false)
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.dashboard-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: $bg-page;
}

.dashboard-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.dashboard-content {
  flex: 1;
  padding: $spacing-lg;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity $transition-normal;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
