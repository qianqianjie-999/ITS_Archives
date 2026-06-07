<template>
  <div class="home-page">
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
        <div class="stat-glow" :style="{ background: card.gradient }"></div>
      </div>
    </div>

    <div class="content-row">
      <div class="panel panel-warranty">
        <div class="panel-header">
          <div class="panel-title-box">
            <el-icon :size="18" class="panel-icon"><DataAnalysis /></el-icon>
            <h3 class="panel-title">质保状态分布</h3>
          </div>
        </div>
        <div class="warranty-content">
          <div class="warranty-pie">
            <svg viewBox="0 0 160 160" class="pie-svg">
              <circle cx="80" cy="80" r="65" fill="none" stroke="#1e293b" stroke-width="20" />
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
            <div class="legend-row total-row">
              <span class="legend-label">点位总计</span>
              <span class="legend-count">{{ warrantyTotal.total }}</span>
            </div>
          </div>
        </div>
        <div class="warranty-detail">
          <div class="detail-row" v-for="item in warrantyDetails" :key="item.label">
            <div class="detail-label">{{ item.label }}</div>
            <div class="detail-stats">
              <span class="detail-stat">在保: {{ item.inCoverage }}</span>
              <span class="detail-stat">过保: {{ item.expired }}</span>
              <span class="detail-stat">总数: {{ item.total }}</span>
              <span class="detail-rate" :style="{ color: item.rate > 60 ? '#52c41a' : '#fa8c16' }">
                在保率: {{ item.rate }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel panel-actions">
        <div class="panel-header">
          <div class="panel-title-box">
            <el-icon :size="18" class="panel-icon"><PieChart /></el-icon>
            <h3 class="panel-title">快捷入口</h3>
          </div>
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
          <div class="panel-title-box">
            <el-icon :size="18" class="panel-icon"><DataAnalysis /></el-icon>
            <h3 class="panel-title">各类型点位统计</h3>
          </div>
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
          <div class="panel-title-box">
            <el-icon :size="18" class="panel-icon"><Clock /></el-icon>
            <h3 class="panel-title">质保到期提醒</h3>
          </div>
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

    <div class="content-row">
      <div class="panel panel-ranking">
        <div class="panel-header">
          <div class="panel-title-box">
            <el-icon :size="18" class="panel-icon"><DataAnalysis /></el-icon>
            <h3 class="panel-title">点位设备服役期限排名</h3>
          </div>
          <div class="panel-action" @click="goToRanking">
            <span class="action-text">更多</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
        <div class="ranking-list" v-if="serviceRanking.length">
          <div class="ranking-row" v-for="(item, index) in serviceRanking.slice(0, 6)" :key="item.id">
            <div class="ranking-num" :class="getRankingClass(index)">{{ index + 1 }}</div>
            <div class="ranking-info">
              <span class="ranking-name">{{ item.name }}</span>
              <span class="ranking-type">{{ item.type }}</span>
            </div>
            <div class="ranking-duration">
              <span class="duration-value">{{ item.duration }}</span>
              <span class="duration-unit">年</span>
            </div>
          </div>
        </div>
        <div class="empty-state" v-else>
          <el-icon :size="40"><Clock /></el-icon>
          <p>暂无设备服役数据</p>
        </div>
      </div>

      <div class="panel panel-projects">
        <div class="panel-header">
          <div class="panel-title-box">
            <el-icon :size="18" class="panel-icon"><Folder /></el-icon>
            <h3 class="panel-title">最近项目</h3>
          </div>
        </div>
        <div class="project-list" v-if="recentProjects.length">
          <div class="project-row" v-for="p in recentProjects.slice(0, 6)" :key="p.id">
            <div class="project-info">
              <span class="project-name">{{ p.name }}</span>
              <span class="project-date">{{ p.acceptance_date }}</span>
            </div>
            <el-tag :type="getProjectTagType(p.warranty_status)" size="small">{{ p.warranty_status }}</el-tag>
          </div>
        </div>
        <div class="empty-state" v-else>
          <el-icon :size="40"><DocumentAdd /></el-icon>
          <p>暂无项目数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { intersectionApi } from '@/api/intersections'
import { pointApi, checkpointPointApi, backendDeviceApi, skyNetApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import {
  Location, Camera, Folder, Monitor, Clock, Bell,
  DocumentAdd, Plus, SuccessFilled, DataAnalysis, PieChart, ArrowRight
} from '@element-plus/icons-vue'

const router = useRouter()

const stats = ref({
  intersections: 0,
  trafficLights: 0,
  electronicPolices: 0,
  parkingEnforcements: 0,
  checkpoints: 0,
  skyNetPoints: 0,
  projects: 0,
  backendDevices: 0
})

const warrantyTotal = ref({ inCoverage: 0, expired: 0, total: 0 })
const warrantyByType = ref<any[]>([])
const expiringDevices = ref<any[]>([])
const serviceRanking = ref<any[]>([])
const recentProjects = ref<any[]>([])

const warrantyDetails = computed(() => {
  return warrantyByType.value.map(item => {
    const rate = item.total > 0 ? Math.round((item.inCoverage / item.total) * 100) : 0
    return {
      ...item,
      rate
    }
  })
})

const statCards = computed(() => {
  const s = stats.value
  return [
    { key: 'intersections', label: '路口总数', value: s.intersections, icon: Location, gradient: 'linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 212, 255, 0.05))', class: '', badge: '信号灯+电警', badgeColor: '#00d4ff' },
    { key: 'trafficLights', label: '信号灯点位', value: s.trafficLights, icon: Clock, gradient: 'linear-gradient(135deg, rgba(82, 196, 26, 0.2), rgba(82, 196, 26, 0.05))', class: '', badge: '在路口中', badgeColor: '#52c41a' },
    { key: 'electronicPolices', label: '电子警察点位', value: s.electronicPolices, icon: Camera, gradient: 'linear-gradient(135deg, rgba(114, 46, 209, 0.2), rgba(114, 46, 209, 0.05))', class: '', badge: '在路口中', badgeColor: '#722ed1' },
    { key: 'parkingEnforcements', label: '违停球点位', value: s.parkingEnforcements, icon: Bell, gradient: 'linear-gradient(135deg, rgba(250, 140, 22, 0.2), rgba(250, 140, 22, 0.05))', class: '', badge: '违停点位', badgeColor: '#fa8c16' },
    { key: 'checkpoints', label: '卡口点位', value: s.checkpoints, icon: Folder, gradient: 'linear-gradient(135deg, rgba(19, 194, 194, 0.2), rgba(19, 194, 194, 0.05))', class: '', badge: '卡口点位', badgeColor: '#13c2c2' },
    { key: 'skyNetPoints', label: '结构化相机', value: s.skyNetPoints, icon: Camera, gradient: 'linear-gradient(135deg, rgba(235, 45, 150, 0.2), rgba(235, 45, 150, 0.05))', class: '', badge: '劝导相机', badgeColor: '#eb2f96' },
    { key: 'backendDevices', label: '后端设备', value: s.backendDevices, icon: Monitor, gradient: 'linear-gradient(135deg, rgba(47, 84, 235, 0.2), rgba(47, 84, 235, 0.05))', class: '', badge: '机房设备', badgeColor: '#2f54eb' },
    { key: 'projects', label: '项目总数', value: s.projects, icon: DocumentAdd, gradient: 'linear-gradient(135deg, rgba(114, 46, 209, 0.2), rgba(114, 46, 209, 0.05))', class: '', badge: '已录入', badgeColor: '#722ed1' }
  ]
})

const deviceBars = computed(() => {
  const max = Math.max(
    stats.value.trafficLights,
    stats.value.electronicPolices,
    stats.value.parkingEnforcements,
    stats.value.checkpoints,
    stats.value.skyNetPoints,
    stats.value.backendDevices,
    1
  )
  return [
    { label: '信号灯', value: stats.value.trafficLights, color: '#52c41a', percent: (stats.value.trafficLights / max) * 100 },
    { label: '电子警察', value: stats.value.electronicPolices, color: '#722ed1', percent: (stats.value.electronicPolices / max) * 100 },
    { label: '违停球', value: stats.value.parkingEnforcements, color: '#fa8c16', percent: (stats.value.parkingEnforcements / max) * 100 },
    { label: '卡口', value: stats.value.checkpoints, color: '#13c2c2', percent: (stats.value.checkpoints / max) * 100 },
    { label: '结构化相机', value: stats.value.skyNetPoints, color: '#eb2f96', percent: (stats.value.skyNetPoints / max) * 100 },
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
  { path: '/statistics', label: '统计报表', icon: Plus, color: 'linear-gradient(135deg, #00d4ff, #00a8cc)' },
  { path: '/sky-net', label: '结构化相机', icon: Camera, color: 'linear-gradient(135deg, #52c41a, #389e0d)' },
  { path: '/memos', label: '备忘录', icon: DocumentAdd, color: 'linear-gradient(135deg, #722ed1, #531dab)' },
  { path: '/users', label: '用户管理', icon: DocumentAdd, color: 'linear-gradient(135deg, #13c2c2, #08979c)' }
]

function navigateTo(path: string) {
  router.push(path)
}

function goToRanking() {
  router.push('/service-ranking')
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

function collectServiceDuration(list: any[], nameField: string, typeLabel: string) {
  const today = new Date()
  list.forEach((item: any) => {
    const acceptDate = item.acceptance_date || (item.project_info?.acceptance_date)
    if (!acceptDate) return
    const d = new Date(acceptDate)
    if (d > today) return
    const years = (today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24 * 365)
    if (years > 0) {
      serviceRanking.value.push({
        id: item.id,
        name: item[nameField] || item.name,
        type: typeLabel,
        duration: years.toFixed(1)
      })
    }
  })
}

function getRankingClass(index: number) {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

function getProjectTagType(status: string) {
  if (status === '在保') return 'success'
  if (status === '过保') return 'danger'
  return 'info'
}

async function fetchStats() {
  try {
    const [
      intersections, trafficLights, electronicPolices,
      parkingEnforcements, checkpoints, skyNetPoints, projects, backendDevices
    ] = await Promise.all([
      intersectionApi.list({ per_page: 0 }),
      intersectionApi.getTrafficLightsAll(),
      intersectionApi.getElectronicPolicesAll(),
      pointApi.getParkingEnforcementsAll(),
      checkpointPointApi.getCheckpointsAll(),
      skyNetApi.getSkyNetsAll(),
      projectApi.list({ per_page: 0 }),
      backendDeviceApi.list({ per_page: 0 })
    ])

    const tl = trafficLights.data || []
    const ep = electronicPolices.data || []
    const pe = parkingEnforcements.data || []
    const cp = checkpoints.data || []
    const sn = skyNetPoints.data || []
    const bd = backendDevices.data || []
    const pr = projects.data || []

    stats.value = {
      intersections: intersections.data?.length || 0,
      trafficLights: tl.length,
      electronicPolices: ep.length,
      parkingEnforcements: pe.length,
      checkpoints: cp.length,
      skyNetPoints: sn.length,
      projects: pr.length,
      backendDevices: bd.length
    }

    const t1 = countWarranty(tl)
    const t2 = countWarranty(ep)
    const t3 = countWarranty(pe)
    const t4 = countWarranty(cp)
    const t5 = countWarranty(sn)
    const t6 = countWarranty(bd)

    warrantyByType.value = [
      { label: '信号灯', inCoverage: t1.inCoverage, expired: t1.expired, total: tl.length },
      { label: '电子警察', inCoverage: t2.inCoverage, expired: t2.expired, total: ep.length },
      { label: '违停球', inCoverage: t3.inCoverage, expired: t3.expired, total: pe.length },
      { label: '卡口', inCoverage: t4.inCoverage, expired: t4.expired, total: cp.length },
      { label: '结构化相机', inCoverage: t5.inCoverage, expired: t5.expired, total: sn.length },
      { label: '后端设备', inCoverage: t6.inCoverage, expired: t6.expired, total: bd.length }
    ]

    warrantyTotal.value = {
      inCoverage: t1.inCoverage + t2.inCoverage + t3.inCoverage + t4.inCoverage + t5.inCoverage + t6.inCoverage,
      expired: t1.expired + t2.expired + t3.expired + t4.expired + t5.expired + t6.expired,
      total: (t1.inCoverage + t1.expired) + (t2.inCoverage + t2.expired) + (t3.inCoverage + t3.expired) + (t4.inCoverage + t4.expired) + (t5.inCoverage + t5.expired) + (t6.inCoverage + t6.expired)
    }

    expiringDevices.value = []
    collectExpiring(tl, 'intersection_name', '信号灯')
    collectExpiring(ep, 'intersection_name', '电子警察')
    collectExpiring(pe, 'point_name', '违停球')
    collectExpiring(cp, 'point_name', '卡口')
    collectExpiring(sn, 'point_name', '结构化相机')
    collectExpiring(bd, 'name', '后端设备')
    expiringDevices.value.sort((a, b) => (a.expire > b.expire ? 1 : -1))

    serviceRanking.value = []
    collectServiceDuration(tl, 'intersection_name', '信号灯')
    collectServiceDuration(ep, 'intersection_name', '电子警察')
    collectServiceDuration(pe, 'point_name', '违停球')
    collectServiceDuration(cp, 'point_name', '卡口')
    collectServiceDuration(sn, 'point_name', '结构化相机')
    collectServiceDuration(bd, 'name', '后端设备')
    serviceRanking.value.sort((a, b) => (parseFloat(b.duration) - parseFloat(a.duration)))

    recentProjects.value = pr.sort((a: any, b: any) => {
      const dateA = new Date(a.acceptance_date || a.created_at || 0)
      const dateB = new Date(b.acceptance_date || b.created_at || 0)
      return dateB.getTime() - dateA.getTime()
    })
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

onMounted(fetchStats)
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.home-page {
  width: 100%;
  min-height: 100%;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 20px;
}

.stat-card {
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: $radius-lg;
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all $transition-normal;
  position: relative;
  overflow: hidden;

  &:hover {
    transform: translateY(-3px);
    border-color: rgba($primary-color, 0.3);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);

    .stat-glow {
      opacity: 1;
    }
  }
}

.stat-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  opacity: 0;
  transition: opacity $transition-normal;
}

.stat-icon-box {
  width: 52px;
  height: 52px;
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-body {
  flex: 1;
  min-width: 0;
}

.stat-num {
  font-size: 26px;
  font-weight: 700;
  color: $text-primary;
  line-height: 1.2;
}

.stat-name {
  font-size: 12px;
  color: $text-secondary;
  margin-top: 2px;
}

.stat-badge {
  position: absolute;
  top: 8px;
  right: 12px;
  font-size: 11px;
  font-weight: 500;
}

.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
}

.panel {
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: $radius-lg;
  padding: 20px;
  transition: all $transition-normal;

  &:hover {
    border-color: rgba($primary-color, 0.2);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  .panel-title-box {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
  }

  .panel-icon {
    color: $primary-color;
  }

  .panel-title {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
    margin: 0;
  }

  .panel-action {
    display: flex;
    align-items: center;
    gap: 4px;
    cursor: pointer;
    color: $text-secondary;
    transition: color 0.2s;
    font-size: 13px;

    &:hover {
      color: $primary-color;
    }
  }
}

.warranty-content {
  display: flex;
  align-items: center;
  gap: 32px;
}

.warranty-pie {
  position: relative;
  width: 160px;
  height: 160px;
  flex-shrink: 0;

  .pie-svg {
    width: 100%;
    height: 100%;
  }

  .pie-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;

    .pie-percent {
      font-size: 22px;
      font-weight: 700;
      color: $text-primary;
    }

    .pie-desc {
      font-size: 11px;
      color: $text-secondary;
    }
  }
}

.warranty-legend {
  flex: 1;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;

  &:not(:last-child) {
    border-bottom: 1px solid $border-color;
  }

  &.total-row {
    margin-top: 8px;
    border-top: 2px solid $border-color;
    padding-top: 10px;
    border-bottom: none;
  }
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 13px;
  color: $text-secondary;
}

.legend-count {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
}

.warranty-detail {
  margin-top: 16px;
  border-top: 1px solid $border-color;
  padding-top: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  
  &:not(:last-child) {
    border-bottom: 1px solid $border-color;
  }
}

.detail-label {
  font-size: 13px;
  font-weight: 500;
  color: $text-primary;
}

.detail-stats {
  display: flex;
  gap: 16px;
  align-items: center;
}

.detail-stat {
  font-size: 12px;
  color: $text-secondary;
}

.detail-rate {
  font-size: 13px;
  font-weight: 600;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all $transition-fast;
  background: rgba($primary-color, 0.03);
  border: 1px solid transparent;

  &:hover {
    background: rgba($primary-color, 0.08);
    border-color: rgba($primary-color, 0.2);
    transform: scale(1.04);
  }
}

.quick-icon {
  width: 44px;
  height: 44px;
  border-radius: $radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.quick-label {
  font-size: 12px;
  color: $text-secondary;
  font-weight: 500;
}

.device-bars {
  padding: 4px 0;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;

  &:last-child {
    margin-bottom: 0;
  }
}

.bar-label {
  width: 60px;
  font-size: 12px;
  color: $text-secondary;
  text-align: right;
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 10px;
  background: $border-color;
  border-radius: 5px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  min-width: 4px;
}

.bar-num {
  width: 32px;
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  text-align: right;
}

.expiry-list {
  max-height: 260px;
  overflow-y: auto;
}

.expiry-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;

  &:not(:last-child) {
    border-bottom: 1px solid $border-color;
  }
}

.expiry-info {
  display: flex;
  flex-direction: column;
}

.expiry-name {
  font-size: 13px;
  color: $text-primary;
  font-weight: 500;
}

.expiry-type {
  font-size: 11px;
  color: $text-secondary;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: $text-secondary;

  p {
    margin-top: 8px;
    font-size: 13px;
  }
}

.ranking-list,
.project-list {
  max-height: 260px;
  overflow-y: auto;
}

.ranking-row,
.project-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;

  &:not(:last-child) {
    border-bottom: 1px solid $border-color;
  }
}

.ranking-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: $border-color;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: $text-secondary;

  &.rank-gold {
    background: linear-gradient(135deg, #ffd700, #ffb700);
    color: #fff;
  }

  &.rank-silver {
    background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
    color: #fff;
  }

  &.rank-bronze {
    background: linear-gradient(135deg, #cd7f32, #b87333);
    color: #fff;
  }
}

.ranking-info,
.project-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.ranking-name,
.project-name {
  font-size: 13px;
  color: $text-primary;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ranking-type,
.project-date {
  font-size: 11px;
  color: $text-secondary;
}

.ranking-duration {
  display: flex;
  align-items: baseline;
  gap: 2px;

  .duration-value {
    font-size: 16px;
    font-weight: 700;
    color: $text-primary;
  }

  .duration-unit {
    font-size: 11px;
    color: $text-secondary;
  }
}
</style>