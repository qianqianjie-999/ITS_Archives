<template>
  <div class="home-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">欢迎回来，{{ userStore.user?.display_name }}</h1>
        <p class="page-subtitle">这是您的智能交通建设档案系统概览</p>
      </div>
      <div class="header-stats">
        <span class="stat-item">
          <span class="stat-label">今日新增</span>
          <span class="stat-value">{{ todayCount }}</span>
        </span>
      </div>
    </div>

    <div class="card-container">
      <div class="stat-card">
        <div class="stat-icon-wrapper bg-primary">
          <el-icon :size="28"><Location /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.intersections }}</div>
          <div class="stat-label">路口总数</div>
        </div>
        <div class="stat-trend positive">
          <el-icon :size="12"><ArrowUp /></el-icon>
          <span>+12%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper bg-success">
          <el-icon :size="28"><Aim /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.points }}</div>
          <div class="stat-label">点位总数</div>
        </div>
        <div class="stat-trend positive">
          <el-icon :size="12"><ArrowUp /></el-icon>
          <span>+8%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper bg-warning">
          <el-icon :size="28"><Folder /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.projects }}</div>
          <div class="stat-label">项目总数</div>
        </div>
        <div class="stat-trend positive">
          <el-icon :size="12"><ArrowUp /></el-icon>
          <span>+5%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon-wrapper bg-info">
          <el-icon :size="28"><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.warrantyExpiring }}</div>
          <div class="stat-label">即将过保</div>
        </div>
        <div class="stat-trend warning">
          <el-icon :size="12"><Bell /></el-icon>
          <span>需要关注</span>
        </div>
      </div>
    </div>

    <div class="section-row">
      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">质保状态概览</h2>
        </div>
        <div class="warranty-chart">
          <div class="chart-pie">
            <svg viewBox="0 0 100 100" class="pie-svg">
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="#52c41a"
                stroke-width="12"
                :stroke-dasharray="warrantyInCoverage * 2.51 + ' 251'"
                transform="rotate(-90 50 50)"
              />
              <circle
                cx="50"
                cy="50"
                r="40"
                fill="none"
                stroke="#f5222d"
                stroke-width="12"
                :stroke-dasharray="warrantyExpired * 2.51 + ' 251'"
                :stroke-dashoffset="-(warrantyInCoverage * 2.51)"
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div class="pie-center">
              <div class="pie-value">{{ Math.round(warrantyInCoveragePercent) }}%</div>
              <div class="pie-label">在保率</div>
            </div>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-color bg-success"></span>
              <span class="legend-text">在保中</span>
              <span class="legend-value">{{ stats.warrantyInCoverage }}</span>
            </div>
            <div class="legend-item">
              <span class="legend-color bg-error"></span>
              <span class="legend-text">已过保</span>
              <span class="legend-value">{{ stats.warrantyExpired }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">快捷操作</h2>
        </div>
        <div class="quick-actions">
          <button class="action-card" @click="navigateTo('/projects')">
            <el-icon :size="24" class="action-icon"><Plus /></el-icon>
            <span class="action-text">新建项目</span>
          </button>
          <button class="action-card" @click="navigateTo('/intersections')">
            <el-icon :size="24" class="action-icon"><Plus /></el-icon>
            <span class="action-text">新建路口</span>
          </button>
          <button class="action-card" @click="navigateTo('/points')">
            <el-icon :size="24" class="action-icon"><Plus /></el-icon>
            <span class="action-text">新建点位</span>
          </button>
        </div>
      </div>
    </div>

    <div class="section-card full-width">
      <div class="section-header">
        <h2 class="section-title">最近操作记录</h2>
        <el-button size="small" @click="viewAllLogs">查看全部</el-button>
      </div>
      <el-table :data="recentLogs" stripe class="logs-table">
        <el-table-column prop="action" label="操作" width="150">
          <template #default="{ row }">
            <span :class="['action-tag', row.action_type]">{{ row.action_label }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="target_name" label="目标" width="200" />
        <el-table-column prop="operator" label="操作人" width="120" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { intersectionApi } from '@/api/intersections'
import { pointApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import { 
  Location, Aim, Folder, Clock, ArrowUp, Bell, Plus 
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const stats = ref({
  intersections: 0,
  points: 0,
  projects: 0,
  warrantyInCoverage: 0,
  warrantyExpired: 0,
  warrantyExpiring: 0
})

const todayCount = ref(3)

const recentLogs = ref([
  { action: 'create', action_type: 'success', action_label: '新增', target_name: '文化路-人民路路口', operator: '管理员', created_at: '2024-01-15 14:30:25' },
  { action: 'update', action_type: 'info', action_label: '修改', target_name: '智慧交通一期项目', operator: '管理员', created_at: '2024-01-15 13:45:18' },
  { action: 'create', action_type: 'success', action_label: '新增', target_name: '违停抓拍点位A1', operator: '编辑员', created_at: '2024-01-15 11:20:00' },
  { action: 'delete', action_type: 'danger', action_label: '删除', target_name: '旧城区信号灯记录', operator: '管理员', created_at: '2024-01-15 09:15:42' },
  { action: 'update', action_type: 'info', action_label: '修改', target_name: '电子警察设备信息', operator: '编辑员', created_at: '2024-01-14 16:30:55' }
])

const warrantyInCoverage = computed(() => {
  const total = stats.value.warrantyInCoverage + stats.value.warrantyExpired
  if (total === 0) return 0
  return (stats.value.warrantyInCoverage / total) * 100
})

const warrantyExpired = computed(() => {
  const total = stats.value.warrantyInCoverage + stats.value.warrantyExpired
  if (total === 0) return 0
  return (stats.value.warrantyExpired / total) * 100
})

const warrantyInCoveragePercent = computed(() => warrantyInCoverage.value)

function navigateTo(path: string) {
  router.push(path)
}

function viewAllLogs() {
  router.push('/logs')
}

async function fetchStats() {
  try {
    const [intersections, points, projects] = await Promise.all([
      intersectionApi.list(),
      pointApi.list(),
      projectApi.list()
    ])
    
    stats.value = {
      intersections: (intersections as any)?.length || 0,
      points: (points as any)?.length || 0,
      projects: (projects as any)?.length || 0,
      warrantyInCoverage: 128,
      warrantyExpired: 32,
      warrantyExpiring: 15
    }
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

onMounted(fetchStats)
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.home-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-lg;
  padding-bottom: $spacing-md;
  border-bottom: 1px solid $border-light;
  
  .page-title {
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 $spacing-xs 0;
  }
  
  .page-subtitle {
    font-size: $font-size-sm;
    color: $text-secondary;
    margin: 0;
  }
}

.header-stats {
  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: $spacing-md $spacing-lg;
    background: $bg-card;
    border-radius: $radius-md;
    box-shadow: $shadow-sm;
    
    .stat-label {
      font-size: $font-size-xs;
      color: $text-secondary;
      margin-bottom: $spacing-xs;
    }
    
    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: $primary-color;
    }
  }
}

.card-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.stat-card {
  background: $bg-card;
  border-radius: $radius-md;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  transition: all $transition-normal;
  position: relative;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  
  &.bg-primary { background: linear-gradient(135deg, $primary-color 0%, $primary-dark 100%); }
  &.bg-success { background: linear-gradient(135deg, $success-color 0%, #389e0d 100%); }
  &.bg-warning { background: linear-gradient(135deg, $warning-color 0%, #d48806 100%); }
  &.bg-info { background: linear-gradient(135deg, #13c2c2 0%, #08979c 100%); }
}

.stat-content {
  flex: 1;
  
  .stat-value {
    font-size: 28px;
    font-weight: 700;
    color: $text-primary;
    line-height: 1.2;
  }
  
  .stat-label {
    font-size: $font-size-xs;
    color: $text-secondary;
    margin-top: $spacing-xs;
  }
}

.stat-trend {
  font-size: $font-size-xs;
  padding: $spacing-xs $spacing-sm;
  border-radius: $radius-sm;
  
  &.positive {
    color: $success-color;
    background: $success-light;
  }
  
  &.warning {
    color: $warning-color;
    background: $warning-light;
  }
}

.section-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.section-card {
  background: $bg-card;
  border-radius: $radius-md;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  
  &.full-width {
    grid-column: span 2;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
  
  .section-title {
    font-size: $font-size-md;
    font-weight: 600;
    color: $text-primary;
    margin: 0;
  }
}

.warranty-chart {
  display: flex;
  align-items: center;
  gap: $spacing-xl;
}

.chart-pie {
  position: relative;
  width: 140px;
  height: 140px;
  
  .pie-svg {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
  }
  
  .pie-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    
    .pie-value {
      font-size: 24px;
      font-weight: 700;
      color: $text-primary;
    }
    
    .pie-label {
      font-size: $font-size-xs;
      color: $text-secondary;
    }
  }
}

.chart-legend {
  flex: 1;
  
  .legend-item {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    margin-bottom: $spacing-md;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    
    &.bg-success { background: $success-color; }
    &.bg-error { background: $error-color; }
  }
  
  .legend-text {
    flex: 1;
    font-size: $font-size-sm;
    color: $text-secondary;
  }
  
  .legend-value {
    font-size: $font-size-md;
    font-weight: 600;
    color: $text-primary;
  }
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-md;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: $spacing-lg $spacing-md;
  background: $bg-page;
  border: 2px dashed $border-color;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all $transition-normal;
  
  &:hover {
    background: $primary-light;
    border-color: $primary-color;
    
    .action-icon {
      color: $primary-color;
    }
  }
  
  .action-icon {
    margin-bottom: $spacing-sm;
    color: $text-placeholder;
    transition: color $transition-fast;
  }
  
  .action-text {
    font-size: $font-size-xs;
    color: $text-secondary;
  }
}

.logs-table {
  .action-tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: $radius-sm;
    font-size: $font-size-xs;
    font-weight: 500;
    
    &.success {
      background: $success-light;
      color: $success-color;
    }
    
    &.info {
      background: $info-light;
      color: $info-color;
    }
    
    &.danger {
      background: $error-light;
      color: $error-color;
    }
  }
}

@media (max-width: 900px) {
  .section-row {
    grid-template-columns: 1fr;
  }
  
  .section-card.full-width {
    grid-column: span 1;
  }
  
  .card-container {
    grid-template-columns: 1fr;
  }
}
</style>
