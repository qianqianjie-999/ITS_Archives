<template>
  <div class="statistics-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">数据统计报表</h1>
        <p class="page-subtitle">全量设备数据汇总 · 按类型分Tab展示</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </div>

    <div class="summary-bar">
      <div class="summary-item">
        <span class="sum-label">设备总计</span>
        <span class="sum-value">{{ totalCount }}</span>
      </div>
      <div class="summary-item green">
        <span class="sum-label">在保设备</span>
        <span class="sum-value">{{ inWarrantyCount }}</span>
      </div>
      <div class="summary-item red">
        <span class="sum-label">过保设备</span>
        <span class="sum-value">{{ expiredCount }}</span>
      </div>
      <div class="summary-item blue">
        <span class="sum-label">涉及项目</span>
        <span class="sum-value">{{ projectCount }}</span>
      </div>
    </div>

    <div class="filter-bar">
      <el-row :gutter="12">
        <el-col :span="6">
          <el-select v-model="filterWarranty" placeholder="质保状态" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="在保" value="在保" />
            <el-option label="过保" value="过保" />
            <el-option label="无项目" value="无项目" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select v-model="filterProject" placeholder="归属项目" clearable filterable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-input v-model="searchKeyword" placeholder="搜索设备名称、路口名称..." clearable @input="handleFilter">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
      </el-row>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="信号灯" name="traffic_light">
        <el-table :data="pagedData.traffic_light" stripe v-loading="loading" border size="small">
          <el-table-column prop="intersection_name" label="路口名称" min-width="130" fixed />
          <el-table-column prop="intersection_type" label="路口类型" width="100" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="signal_type" label="信号机类型" width="110" />
          <el-table-column prop="signal_count" label="信号机数量" width="100" align="center" />
          <el-table-column prop="left_arrow_count" label="左转箭头灯" width="100" align="center" />
          <el-table-column prop="straight_arrow_count" label="直行箭头灯" width="100" align="center" />
          <el-table-column prop="right_arrow_count" label="右转箭头灯" width="100" align="center" />
          <el-table-column prop="full_screen_count" label="满屏灯" width="80" align="center" />
          <el-table-column prop="non_motor_count" label="非机动灯" width="90" align="center" />
          <el-table-column prop="pedestrian_count" label="人行灯" width="80" align="center" />
          <el-table-column prop="radar_count" label="车流量雷达" width="100" align="center" />
          <el-table-column prop="guide_screen_count" label="诱导屏" width="80" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="电子警察" name="electronic_police">
        <el-table :data="pagedData.electronic_police" stripe v-loading="loading" border size="small">
          <el-table-column prop="intersection_name" label="路口名称" min-width="130" fixed />
          <el-table-column prop="intersection_type" label="路口类型" width="100" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="capture_type" label="抓拍类型" width="100" />
          <el-table-column prop="terminal_server_count" label="终端服务器" width="100" align="center" />
          <el-table-column prop="forward_capture_count" label="正向抓拍" width="90" align="center" />
          <el-table-column prop="reverse_capture_count" label="反向抓拍" width="90" align="center" />
          <el-table-column prop="led_light_count" label="LED灯" width="80" align="center" />
          <el-table-column prop="strobe_light_count" label="爆闪灯" width="80" align="center" />
          <el-table-column prop="ptz_count" label="监控球机" width="90" align="center" />
          <el-table-column prop="signal_detector_count" label="信号检测器" width="100" align="center" />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="违停球" name="parking_enforcement">
        <el-table :data="pagedData.parking_enforcement" stripe v-loading="loading" border size="small">
          <el-table-column prop="point_name" label="点位名称" min-width="130" fixed />
          <el-table-column prop="camera_area" label="抓拍区域" min-width="120" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="camera_count" label="抓拍机数量" width="100" align="center" />
          <el-table-column prop="parking_sign_count" label="违停标牌" width="90" align="center" />
          <el-table-column prop="monitor_sign_count" label="监控标牌" width="90" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="卡口" name="checkpoint">
        <el-table :data="pagedData.checkpoint" stripe v-loading="loading" border size="small">
          <el-table-column prop="point_name" label="点位名称" min-width="130" fixed />
          <el-table-column prop="point_type" label="卡口类型" width="150" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="camera_count" label="抓拍机数量" width="100" align="center" />
          <el-table-column prop="strobe_light_count" label="爆闪灯数量" width="100" align="center" />
          <el-table-column prop="radar_count" label="测速雷达" width="90" align="center" />
          <el-table-column prop="sign_count" label="标牌数量" width="90" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="后端设备" name="backend_device">
        <el-table :data="pagedData.backend_device" stripe v-loading="loading" border size="small">
          <el-table-column prop="name" label="设备名称" min-width="140" fixed />
          <el-table-column prop="type" label="设备类型" width="130" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="location" label="安装位置" min-width="110" />
          <el-table-column prop="ip_address" label="IP地址" width="130" />
          <el-table-column prop="port" label="端口" width="80" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <div class="pager">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="currentTabTotal"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import { intersectionApi } from '@/api/intersections'
import { pointApi, checkpointPointApi, backendDeviceApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import apiClient from '@/api'

const loading = ref(false)
const activeTab = ref('traffic_light')
const currentPage = ref(1)
const pageSize = ref(20)

const filterWarranty = ref('')
const filterProject = ref('')
const searchKeyword = ref('')

const projects = ref<any[]>([])
const trafficLights = ref<any[]>([])
const electronicPolices = ref<any[]>([])
const parkingEnforcements = ref<any[]>([])
const checkpoints = ref<any[]>([])
const backendDevices = ref<any[]>([])

function tagType(status: string) {
  if (status === '在保') return 'success'
  if (status === '过保') return 'danger'
  return 'info'
}

function applyFilter(list: any[]) {
  return list.filter(item => {
    if (filterWarranty.value && item.warranty_status !== filterWarranty.value) return false
    if (filterProject.value && item.project_id !== filterProject.value) return false
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      const haystack = [item.name, item.intersection_name, item.point_name, item.project_name, item.intersection_type, item.type]
        .filter(Boolean).join(' ').toLowerCase()
      if (!haystack.includes(kw)) return false
    }
    return true
  })
}

const filteredData = computed(() => {
  return {
    traffic_light: applyFilter(trafficLights.value),
    electronic_police: applyFilter(electronicPolices.value),
    parking_enforcement: applyFilter(parkingEnforcements.value),
    checkpoint: applyFilter(checkpoints.value),
    backend_device: applyFilter(backendDevices.value)
  }
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  const result: Record<string, any[]> = {}
  for (const [key, data] of Object.entries(filteredData.value)) {
    result[key] = data.slice(start, end)
  }
  return result
})

const currentTabTotal = computed(() => {
  const tab = activeTab.value
  return (filteredData.value as any)[tab]?.length || 0
})

const totalCount = computed(() => {
  return trafficLights.value.length + electronicPolices.value.length +
    parkingEnforcements.value.length + checkpoints.value.length + backendDevices.value.length
})

const inWarrantyCount = computed(() => {
  return [...trafficLights.value, ...electronicPolices.value, ...parkingEnforcements.value,
    ...checkpoints.value, ...backendDevices.value]
    .filter(i => i.warranty_status === '在保').length
})

const expiredCount = computed(() => {
  return [...trafficLights.value, ...electronicPolices.value, ...parkingEnforcements.value,
    ...checkpoints.value, ...backendDevices.value]
    .filter(i => i.warranty_status === '过保').length
})

const projectCount = computed(() => {
  const ids = new Set<number>()
  ;[...trafficLights.value, ...electronicPolices.value, ...parkingEnforcements.value,
    ...checkpoints.value, ...backendDevices.value]
    .forEach(i => { if (i.project_id) ids.add(i.project_id) })
  return ids.size
})

function handleFilter() { currentPage.value = 1 }
function handleTabChange() { currentPage.value = 1 }
function handleSizeChange() { currentPage.value = 1 }
function handleCurrentChange() {}

async function fetchData() {
  loading.value = true
  try {
    const [
      p, tl, ep, pe, cp, bd
    ] = await Promise.all([
      projectApi.list(),
      intersectionApi.getTrafficLightsAll(),
      intersectionApi.getElectronicPolicesAll(),
      pointApi.getParkingEnforcementsAll(),
      checkpointPointApi.getCheckpointsAll(),
      backendDeviceApi.list()
    ])
    projects.value = (p as any[]) || []
    trafficLights.value = (tl as any[]) || []
    electronicPolices.value = (ep as any[]) || []
    parkingEnforcements.value = (pe as any[]) || []
    checkpoints.value = (cp as any[]) || []
    backendDevices.value = (bd as any[]) || []
  } catch (error) {
    console.error('获取数据失败', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

async function exportData() {
  try {
    ElMessage.info('正在导出数据...')
    const response = await apiClient.get('/export/statistics', { responseType: 'blob' }) as unknown as Blob
    const url = window.URL.createObjectURL(new Blob([response]))
    const a = document.createElement('a')
    a.href = url
    a.download = `智能交通设备统计_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败', error)
    ElMessage.error('导出失败')
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.statistics-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 20px;
  .page-title { font-size: 22px; font-weight: 700; color: $text-primary; margin: 0; }
  .page-subtitle { font-size: 13px; color: $text-secondary; margin: 4px 0 0; }
}

.summary-bar {
  display: flex; gap: 16px; margin-bottom: 16px;
  .summary-item {
    flex: 1; background: #fff; border-radius: 10px; padding: 16px 20px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05); text-align: center;
    .sum-label { display: block; font-size: 12px; color: #8c8c8c; margin-bottom: 4px; }
    .sum-value { font-size: 24px; font-weight: 700; color: #1a1a2e; }
    &.green .sum-value { color: #52c41a; }
    &.red .sum-value { color: #ff4d4f; }
    &.blue .sum-value { color: #1890ff; }
  }
}

.filter-bar {
  background: #fff; padding: 12px 16px; border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05); margin-bottom: 16px;
  .el-select, .el-input { width: 100%; }
}

.pager {
  display: flex; justify-content: flex-end; margin-top: 16px;
  padding: 12px 16px; background: #fff; border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
</style>
