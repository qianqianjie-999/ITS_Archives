<template>
  <div class="dashboard-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>智能交通建设档案系统</h1>
          <div class="user-info">
            <span>{{ userStore.user?.display_name }}</span>
            <el-tag size="small" type="info">{{ userStore.user?.role === 'admin' ? '管理员' : userStore.user?.role === 'editor' ? '编辑' : '查看' }}</el-tag>
            <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
          </div>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu :default-active="activeMenu" router>
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/intersections">
              <el-icon><Location /></el-icon>
              <span>路口管理</span>
            </el-menu-item>
            <el-menu-item index="/points">
              <el-icon><Aim /></el-icon>
              <span>点位管理</span>
            </el-menu-item>
            <el-menu-item index="/projects">
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </el-menu-item>
            <el-menu-item v-if="userStore.isAdmin" index="/logs">
              <el-icon><Document /></el-icon>
              <span>操作日志</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

async function handleLogout() {
  await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
}

.el-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 20px;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.el-aside {
  background: #f5f7fa;
}

.el-main {
  background: #f0f2f5;
  padding: 20px;
}
</style>