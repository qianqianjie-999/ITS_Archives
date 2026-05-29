<template>
  <div class="home-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">智能交通建设档案系统</h1>
        <p class="page-subtitle">{{ currentDate }} · 欢迎回来，{{ userStore.user?.display_name || userStore.user?.username }}</p>
      </div>
    </div>

    <div class="card-grid">
      <div class="stat-card" v-for="card in statCards" :key="card.key" :class="card.class">
        <div class="stat-icon-box" :style="{ background: card.gradient }">
          <el-icon :size="26"><component :is="card.icon" /></el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-num">{{ card.value }}</div>
          <div class="stat-name">{{ card.label }}</div>
        </div>
        <div class="stat-badge" :style="{ color: card.badgeColor }">{{ card.badge }}</div>
      </div>
    </div>

    <div class="content-row">
      <div class="panel panel-warranty">
        <div class="panel-header">
          <h3 class="panel-title">质保状态分布</h3>
        </div>
        <div class="warranty-content">
          <div class="warranty-pie">
            <svg viewBox="0 0 160 160" class="pie-svg">
              <circle cx="80" cy="80" r="65" fill="none" stroke="#f0f0f0" stroke-width="20" />
              <circle
                cx="80" cy="80" r="65" fill="none"
                stroke="#52c41a" stroke-width="20"
                :stroke-dasharray="pieInWarranty + ' ' + (408.4 - pieInWarranty)"
                stroke-dashoffset="0"
                transform="rotate(-90 80 80)"
              />
              <circle
                cx="80" cy="80" r="65" fill="none"
                stroke="#ff4d4f" stroke-width="20"
                :stroke-dasharray="pieExpired + ' ' + (408.4 - pieExpired)"
                :stroke-dashoffset="-(pieInWarranty || 0)"
                transform="rotate(-90 80 80)"
              />
              <circle
                cx="80" cy="80" r="65" fill="none"
                stroke="#bfbfbf" stroke-width="20"
                :stroke-dasharray="pieNone + ' ' + (408.4 - pieNone)"
                :stroke-dashoffset="-((pieInWarranty || 0) + (pieExpired || 0))"
                transform="rotate(-90 80 80)"
              />
            </svg>
            <div class="pie-center">
              <div class="pie-percent">{{ warrantyRate }}%</div>
              <div class="pie-desc">在保率</div>
            </div>
          </div>
          <div class="warranty-legend">
            <div class="legend-row">
              <span class="legend-dot" style="background:#52c41a"></span>
              <span class="legend-label">在保中</span>
              <span class="legend-count">{{ warrantyTotal.inCoverage }}</span>
            </div>
            <div class="legend-row">
              <span class="legend-dot" style="background:#ff4d4f"></span>
              <span class="legend-label">已过保</span>
              <span class="legend-count">{{ warrantyTotal.expired }}</span>
            </div>
            <div class="legend-row">
              <span class="legend-dot" style="background:#bfbfbf"></span>
              <span class="legend-label">无项目</span>
              <span class="legend-count">{{ warrantyTotal.noProject }}</span>
            </div>
            <div class="legend-row total-row">
              <span class="legend-label">设备总计</span>
              <span class="legend-count">{{ warrantyTotal.total }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel panel-actions">
        <div class="panel-header">
          <h3 class="panel-title">快捷入口</h3>
        </div>
        <div class="quick-grid">
          <div class="quick-item" v-for="q in quickLinks" :key="q.path" @click="navigateTo(q.path)">
            <div class="quick-icon" :style="{ background: q.color }">
              <el-icon :size="22"><component :is="q.icon" /></el-icon>
            </div>
            <span class="quick-label">{{ q.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-row">
      <div class="panel panel-device">
        <div class="panel-header">
          <h3 class="panel-title">各类型设备统计</h3>
        </div>
        <div class="device-bars">
          <div class="bar-row" v-for="bar in deviceBars" :key="bar.label">
            <div class="bar-label">{{ bar.label }}</div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: bar.percent + '%', background: bar.color }"></div>
            </div>
            <div class="bar-num">{{ bar.value }}</div>
          </div>
        </div>
      </div>

      <div class="panel panel-summary">
        <div class="panel-header">
          <h3 class="panel-title">质保到期提醒</h3>
        </div>
        <div class="expiry-list" v-if="expiringDevices.length">
          <div class="expiry-row" v-for="d in expiringDevices.slice(0, 6)" :key="d.id">
            <div class="expiry-info">
              <span class="expiry-name">{{ d.name }}</span>
              <span class="expiry-type">{{ d.type }}</span>
            </div>
            <el-tag :type="d.urgent ? 'danger' : 'warning'" size="small">{{ d.expire }}</el-tag>
          </div>
        </div>
        <div class="empty-state" v-else>
          <el-icon :size="40"><SuccessFilled /></el-icon>
          <p>所有设备均在保期内</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { intersectionApi } from '@/api/intersections'
import { pointApi, checkpointPointApi, backendDeviceApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import {
  Location, Camera, Folder, Monitor, Clock, Bell,
  DocumentAdd, Plus, SuccessFilled
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
})

const stats = ref({
  intersections: 0,
  trafficLights: 0,
  electronicPolices: 0,
  parkingEnforcements: 0,
  checkpoints: 0,
  projects: 0,
  backendDevices: 0
})

const warrantyTotal = ref({ inCoverage: 0, expired: 0, noProject: 0, total: 0 })
const expiringDevices = ref<any[]>([])

const statCards = computed(() => {
  const s = stats.value
  return [
    { key: 'intersections', label: '路口总数', value: s.intersections, icon: Location, gradient: 'linear-gradient(135deg, #1890ff, #096dd9)', class: '', badge: '信号灯+电警', badgeColor: '#1890ff' },
    { key: 'trafficLights', label: '信号灯设备', value: s.trafficLights, icon: Clock, gradient: 'linear-gradient(135deg, #52c41a, #389e0d)', class: '', badge: '在路口中', badgeColor: '#52c41a' },
    { key: 'electronicPolices', label: '电子警察设备', value: s.electronicPolices, icon: Camera, gradient: 'linear-gradient(135deg, #722ed1, #531dab)', class: '', badge: '在路口中', badgeColor: '#722ed1' },
    { key: 'parkingEnforcements', label: '违停球设备', value: s.parkingEnforcements, icon: Bell, gradient: 'linear-gradient(135deg, #fa8c16, #d46b08)', class: '', badge: '违停点位', badgeColor: '#fa8c16' },
    { key: 'checkpoints', label: '卡口设备', value: s.checkpoints, icon: Folder, gradient: 'linear-gradient(135deg, #13c2c2, #08979c)', class: '', badge: '卡口点位', badgeColor: '#13c2c2' },
    { key: 'projects', label: '项目总数', value: s.projects, icon: DocumentAdd, gradient: 'linear-gradient(135deg, #eb2f96, #c41d7f)', class: '', badge: '已录入', badgeColor: '#eb2f96' },
    { key: 'backendDevices', label: '后端设备', value: s.backendDevices, icon: Monitor, gradient: 'linear-gradient(135deg, #2f54eb, #1d39c4)', class: '', badge: '机房设备', badgeColor: '#2f54eb' }
  ]
})

const deviceBars = computed(() => {
  const max = Math.max(
    stats.value.trafficLights,
    stats.value.electronicPolices,
    stats.value.parkingEnforcements,
    stats.value.checkpoints,
    stats.value.backendDevices,
    1
  )
  return [
    { label: '信号灯', value: stats.value.trafficLights, color: '#52c41a', percent: (stats.value.trafficLights / max) * 100 },
    { label: '电子警察', value: stats.value.electronicPolices, color: '#722ed1', percent: (stats.value.electronicPolices / max) * 100 },
    { label: '违停球', value: stats.value.parkingEnforcements, color: '#fa8c16', percent: (stats.value.parkingEnforcements / max) * 100 },
    { label: '卡口', value: stats.value.checkpoints, color: '#13c2c2', percent: (stats.value.checkpoints / max) * 100 },
    { label: '后端设备', value: stats.value.backendDevices, color: '#2f54eb', percent: (stats.value.backendDevices / max) * 100 }
  ]
})

const circumference = 408.4

const pieInWarranty = computed(() => {
  if (!warrantyTotal.value.total) return 0
  return (warrantyTotal.value.inCoverage / warrantyTotal.value.total) * circumference
})

const pieExpired = computed(() => {
  if (!warrantyTotal.value.total) return 0
  return (warrantyTotal.value.expired / warrantyTotal.value.total) * circumference
})

const pieNone = computed(() => {
  if (!warrantyTotal.value.total) return 0
  return (warrantyTotal.value.noProject / warrantyTotal.value.total) * circumference
})

const warrantyRate = computed(() => {
  if (!warrantyTotal.value.total) return 0
  return Math.round((warrantyTotal.value.inCoverage / warrantyTotal.value.total) * 100)
})

const quickLinks = [
  { path: '/projects', label: '项目管理', icon: DocumentAdd, color: 'linear-gradient(135deg, #eb2f96, #c41d7f)' },
  { path: '/intersections', label: '路口管理', icon: Location, color: 'linear-gradient(135deg, #1890ff, #096dd9)' },
  { path: '/parking-enforcements', label: '违停管理', icon: Camera, color: 'linear-gradient(135deg, #fa8c16, #d46b08)' },
  { path: '/checkpoints', label: '卡口管理', icon: Folder, color: 'linear-gradient(135deg, #13c2c2, #08979c)' },
  { path: '/backend-devices', label: '后端设备', icon: Monitor, color: 'linear-gradient(135deg, #2f54eb, #1d39c4)' },
  { path: '/statistics', label: '统计报表', icon: Plus, color: 'linear-gradient(135deg, #595959, #262626)' }
]

function navigateTo(path: string) {
  router.push(path)
}

function countWarranty(list: any[], field = 'warranty_status') {
  let inCov = 0, exp = 0, noP = 0
  list.forEach((item: any) => {
    const status = item[field]
    if (status === '在保') inCov++
    else if (status === '过保') exp++
    else noP++
  })
  return { inCoverage: inCov, expired: exp, noProject: noP }
}

function collectExpiring(list: any[], nameField: string, typeLabel: string) {
  const today = new Date()
  const months3 = new Date(today.getFullYear(), today.getMonth() + 3, today.getDate())
  const months6 = new Date(today.getFullYear(), today.getMonth() + 6, today.getDate())
  list.forEach((item: any) => {
    const expireDate = item.warranty_expire_date || item.effective_warranty_expire_date
    if (!expireDate) return
    const d = new Date(expireDate)
    if (d <= today) return
    if (d <= months6) {
      expiringDevices.value.push({
        id: item.id,
        name: item[nameField] || item.name,
        type: typeLabel,
        expire: d.toISOString().split('T')[0],
        urgent: d <= months3
      })
    }
  })
}

async function fetchStats() {
  try {
    const [
      intersections, trafficLights, electronicPolices,
      parkingEnforcements, checkpoints, projects, backendDevices
    ] = await Promise.all([
      intersectionApi.list(),
      intersectionApi.getTrafficLightsAll(),
      intersectionApi.getElectronicPolicesAll(),
      pointApi.getParkingEnforcementsAll(),
      checkpointPointApi.getCheckpointsAll(),
      projectApi.list(),
      backendDeviceApi.list()
    ])

    const tl = (trafficLights as any[]) || []
    const ep = (electronicPolices as any[]) || []
    const pe = (parkingEnforcements as any[]) || []
    const cp = (checkpoints as any[]) || []
    const bd = (backendDevices as any[]) || []

    stats.value = {
      intersections: (intersections as any[])?.length || 0,
      trafficLights: tl.length,
      electronicPolices: ep.length,
      parkingEnforcements: pe.length,
      checkpoints: cp.length,
      projects: (projects as any[])?.length || 0,
      backendDevices: bd.length
    }

    const t1 = countWarranty(tl)
    const t2 = countWarranty(ep)
    const t3 = countWarranty(pe)
    const t4 = countWarranty(cp)
    const t5 = countWarranty(bd)

    warrantyTotal.value = {
      inCoverage: t1.inCoverage + t2.inCoverage + t3.inCoverage + t4.inCoverage + t5.inCoverage,
      expired: t1.expired + t2.expired + t3.expired + t4.expired + t5.expired,
      noProject: t1.noProject + t2.noProject + t3.noProject + t4.noProject + t5.noProject,
      total: tl.length + ep.length + pe.length + cp.length + bd.length
    }

    expiringDevices.value = []
    collectExpiring(tl, 'intersection_name', '信号灯')
    collectExpiring(ep, 'intersection_name', '电子警察')
    collectExpiring(pe, 'point_name', '违停球')
    collectExpiring(cp, 'point_name', '卡口')
    collectExpiring(bd, 'name', '后端设备')
    expiringDevices.value.sort((a, b) => (a.expire > b.expire ? 1 : -1))
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

onMounted(fetchStats)
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.home-page {
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 28px;
  .page-title { font-size: 26px; font-weight: 700; color: $text-primary; margin: 0; }
  .page-subtitle { font-size: 14px; color: $text-secondary; margin: 6px 0 0; }
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.25s ease;
  position: relative;
  overflow: hidden;
  &:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
}

.stat-icon-box {
  width: 52px; height: 52px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-body { flex: 1; min-width: 0; }
.stat-num { font-size: 26px; font-weight: 700; color: #1a1a2e; line-height: 1.2; }
.stat-name { font-size: 12px; color: #8c8c8c; margin-top: 2px; }
.stat-badge { position: absolute; top: 8px; right: 12px; font-size: 11px; font-weight: 500; }

.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
  @media (max-width: 900px) { grid-template-columns: 1fr; }
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

.warranty-content {
  display: flex; align-items: center; gap: 32px;
}

.warranty-pie {
  position: relative; width: 160px; height: 160px; flex-shrink: 0;
  .pie-svg { width: 100%; height: 100%; }
  .pie-center {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    text-align: center;
    .pie-percent { font-size: 22px; font-weight: 700; color: #1a1a2e; }
    .pie-desc { font-size: 11px; color: #8c8c8c; }
  }
}

.warranty-legend { flex: 1; }
.legend-row {
  display: flex; align-items: center; gap: 8px; padding: 6px 0;
  &:not(:last-child) { border-bottom: 1px solid #f5f5f5; }
  &.total-row { margin-top: 8px; border-top: 2px solid #e8e8e8; padding-top: 10px; border-bottom: none; }
}
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-label { flex: 1; font-size: 13px; color: #595959; }
.legend-count { font-size: 16px; font-weight: 600; color: #1a1a2e; }

.quick-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;
}
.quick-item {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 16px 8px; border-radius: 10px;
  cursor: pointer; transition: all 0.2s;
  &:hover { background: #fafafa; transform: scale(1.04); }
}
.quick-icon {
  width: 44px; height: 44px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center; color: #fff;
}
.quick-label { font-size: 12px; color: #595959; font-weight: 500; }

.device-bars { padding: 4px 0; }
.bar-row {
  display: flex; align-items: center; gap: 10px; margin-bottom: 14px;
  &:last-child { margin-bottom: 0; }
}
.bar-label { width: 60px; font-size: 12px; color: #595959; text-align: right; flex-shrink: 0; }
.bar-track {
  flex: 1; height: 10px; background: #f0f0f0; border-radius: 5px; overflow: hidden;
}
.bar-fill {
  height: 100%; border-radius: 5px;
  transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  min-width: 4px;
}
.bar-num { width: 32px; font-size: 14px; font-weight: 600; color: #1a1a2e; text-align: right; }

.expiry-list { max-height: 260px; overflow-y: auto; }
.expiry-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0;
  &:not(:last-child) { border-bottom: 1px solid #f5f5f5; }
}
.expiry-info { display: flex; flex-direction: column; }
.expiry-name { font-size: 13px; color: #1a1a2e; font-weight: 500; }
.expiry-type { font-size: 11px; color: #8c8c8c; }

.empty-state {
  text-align: center; padding: 30px; color: #8c8c8c;
  p { margin-top: 8px; font-size: 13px; }
}
</style>
