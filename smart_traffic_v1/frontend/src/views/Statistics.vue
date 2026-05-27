<template>
  <div class="statistics-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">数据统计报表</h1>
        <p class="page-subtitle">查看和管理所有设备数据</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </div>

    <div class="filter-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filterType" placeholder="设备类型" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="信号灯" value="traffic_light" />
            <el-option label="电子警察" value="electronic_police" />
            <el-option label="违停球" value="parking_enforcement" />
            <el-option label="卡口" value="checkpoint" />
            <el-option label="后端设备" value="backend_device" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterProject" placeholder="归属项目" clearable filterable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filterWarranty" placeholder="质保状态" clearable @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="在保" value="在保" />
            <el-option label="过保" value="过保" />
            <el-option label="无项目" value="无项目" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="searchKeyword" placeholder="搜索关键字" clearable @input="handleSearch">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
      </el-row>
    </div>

    <div class="stats-summary">
      <div class="summary-item">
        <span class="summary-label">总记录数</span>
        <span class="summary-value">{{ filteredData.length }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">在保设备</span>
        <span class="summary-value success">{{ warrantyStats.inCoverage }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">过保设备</span>
        <span class="summary-value danger">{{ warrantyStats.expired }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">涉及项目</span>
        <span class="summary-value">{{ projectStats }}</span>
      </div>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="信号灯" name="traffic_light">
        <el-table :data="paginatedData.traffic_light" stripe v-loading="loading">
          <el-table-column prop="intersection_name" label="路口名称" min-width="120" />
          <el-table-column prop="intersection_type" label="路口类型" width="100" />
          <el-table-column prop="project_name" label="归属项目" min-width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getWarrantyType(row.warranty_status)" size="small">
                {{ row.warranty_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="signal_type" label="信号机类型" width="100" />
          <el-table-column prop="signal_count" label="信号机数量" width="100" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="builder" label="建设单位" min-width="100" show-overflow-tooltip />
          <el-table-column prop="constructor" label="施工单位" min-width="100" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="电子警察" name="electronic_police">
        <el-table :data="paginatedData.electronic_police" stripe v-loading="loading">
          <el-table-column prop="intersection_name" label="路口名称" min-width="120" />
          <el-table-column prop="intersection_type" label="路口类型" width="100" />
          <el-table-column prop="project_name" label="归属项目" min-width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getWarrantyType(row.warranty_status)" size="small">
                {{ row.warranty_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="capture_type" label="抓拍类型" width="100" />
          <el-table-column prop="camera_count" label="抓拍数量" width="100" align="center" />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="builder" label="建设单位" min-width="100" show-overflow-tooltip />
          <el-table-column prop="constructor" label="施工单位" min-width="100" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="违停球" name="parking_enforcement">
        <el-table :data="paginatedData.parking_enforcement" stripe v-loading="loading">
          <el-table-column prop="point_name" label="点位名称" min-width="120" />
          <el-table-column prop="project_name" label="归属项目" min-width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getWarrantyType(row.warranty_status)" size="small">
                {{ row.warranty_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="camera_count" label="抓拍机数量" width="100" align="center" />
          <el-table-column prop="parking_sign_count" label="违停标牌" width="100" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="builder" label="建设单位" min-width="100" show-overflow-tooltip />
          <el-table-column prop="constructor" label="施工单位" min-width="100" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="卡口" name="checkpoint">
        <el-table :data="paginatedData.checkpoint" stripe v-loading="loading">
          <el-table-column prop="point_name" label="点位名称" min-width="120" />
          <el-table-column prop="checkpoint_type" label="卡口类型" width="120" />
          <el-table-column prop="project_name" label="归属项目" min-width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getWarrantyType(row.warranty_status)" size="small">
                {{ row.warranty_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="camera_count" label="抓拍机数量" width="100" align="center" />
          <el-table-column prop="strobe_light_count" label="爆闪灯数量" width="100" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="builder" label="建设单位" min-width="100" show-overflow-tooltip />
          <el-table-column prop="constructor" label="施工单位" min-width="100" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="后端设备" name="backend_device">
        <el-table :data="paginatedData.backend_device" stripe v-loading="loading">
          <el-table-column prop="name" label="设备名称" min-width="120" />
          <el-table-column prop="type" label="设备类型" width="120" />
          <el-table-column prop="project_name" label="归属项目" min-width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getWarrantyType(row.warranty_status)" size="small">
                {{ row.warranty_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="builder" label="建设单位" min-width="100" show-overflow-tooltip />
          <el-table-column prop="constructor" label="施工单位" min-width="100" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="全部" name="all">
        <el-table :data="paginatedData.all" stripe v-loading="loading">
          <el-table-column prop="device_type" label="设备类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ getDeviceTypeName(row.device_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="名称" min-width="120" />
          <el-table-column prop="location" label="位置" min-width="120" />
          <el-table-column prop="project_name" label="归属项目" min-width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getWarrantyType(row.warranty_status)" size="small">
                {{ row.warranty_status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="builder" label="建设单位" min-width="100" show-overflow-tooltip />
          <el-table-column prop="constructor" label="施工单位" min-width="100" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredData.length"
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
import { pointApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import apiClient from '@/api'

const loading = ref(false)
const activeTab = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)

const filterType = ref('')
const filterProject = ref('')
const filterWarranty = ref('')
const searchKeyword = ref('')

const projects = ref<any[]>([])
const trafficLights = ref<any[]>([])
const electronicPolices = ref<any[]>([])
const parkingEnforcements = ref<any[]>([])
const checkpoints = ref<any[]>([])
const backendDevices = ref<any[]>([])

const allData = computed(() => {
  const data: any[] = []

  trafficLights.value.forEach(item => {
    data.push({
      device_type: 'traffic_light',
      id: item.id,
      name: item.intersection_name + '-信号灯',
      location: item.intersection_name,
      intersection_name: item.intersection_name,
      intersection_type: item.intersection_type,
      project_name: item.project_name,
      project_id: item.project_id,
      warranty_status: item.warranty_status,
      signal_type: item.signal_type,
      signal_count: item.signal_count,
      power_source: item.power_source,
      builder: item.builder,
      constructor: item.constructor
    })
  })

  electronicPolices.value.forEach(item => {
    data.push({
      device_type: 'electronic_police',
      id: item.id,
      name: item.intersection_name + '-电子警察',
      location: item.intersection_name,
      intersection_name: item.intersection_name,
      intersection_type: item.intersection_type,
      project_name: item.project_name,
      project_id: item.project_id,
      warranty_status: item.warranty_status,
      capture_type: item.capture_type,
      camera_count: item.forward_capture_count + item.reverse_capture_count,
      network_source: item.network_source,
      builder: item.builder,
      constructor: item.constructor
    })
  })

  parkingEnforcements.value.forEach(item => {
    data.push({
      device_type: 'parking_enforcement',
      id: item.id,
      name: item.point_name,
      location: item.point_name,
      point_name: item.point_name,
      project_name: item.project_name,
      project_id: item.project_id,
      warranty_status: item.warranty_status,
      camera_count: item.camera_count,
      parking_sign_count: item.parking_sign_count,
      power_source: item.power_source,
      network_source: item.network_source,
      builder: item.builder,
      constructor: item.constructor
    })
  })

  checkpoints.value.forEach(item => {
    data.push({
      device_type: 'checkpoint',
      id: item.id,
      name: item.point_name,
      location: item.point_name,
      point_name: item.point_name,
      checkpoint_type: item.checkpoint_type,
      project_name: item.project_name,
      project_id: item.project_id,
      warranty_status: item.warranty_status,
      camera_count: item.camera_count,
      strobe_light_count: item.strobe_light_count,
      power_source: item.power_source,
      network_source: item.network_source,
      builder: item.builder,
      constructor: item.constructor
    })
  })

  backendDevices.value.forEach(item => {
    data.push({
      device_type: 'backend_device',
      id: item.id,
      name: item.name,
      location: item.project_name,
      type: item.type,
      project_name: item.project_name,
      project_id: item.project_id,
      warranty_status: item.warranty_status,
      builder: item.builder,
      constructor: item.constructor
    })
  })

  return data
})

const filteredData = computed(() => {
  let data = allData.value

  if (filterType.value) {
    data = data.filter(item => item.device_type === filterType.value)
  }

  if (filterProject.value) {
    data = data.filter(item => item.project_id === filterProject.value)
  }

  if (filterWarranty.value) {
    data = data.filter(item => item.warranty_status === filterWarranty.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(item =>
      item.name?.toLowerCase().includes(keyword) ||
      item.location?.toLowerCase().includes(keyword) ||
      item.project_name?.toLowerCase().includes(keyword) ||
      item.builder?.toLowerCase().includes(keyword)
    )
  }

  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value

  const typeFiltered = filterType.value
    ? filteredData.value.filter(item => item.device_type === filterType.value)
    : filteredData.value

  const types = ['traffic_light', 'electronic_police', 'parking_enforcement', 'checkpoint', 'backend_device']
  const result: Record<string, any[]> = { all: filteredData.value }

  types.forEach(type => {
    const typeData = filteredData.value.filter(item => item.device_type === type)
    result[type] = typeData.slice(start, end)
  })

  return result
})

const warrantyStats = computed(() => {
  const data = filteredData.value
  return {
    inCoverage: data.filter(item => item.warranty_status === '在保').length,
    expired: data.filter(item => item.warranty_status === '过保').length
  }
})

const projectStats = computed(() => {
  const projectIds = new Set(filteredData.value.map(item => item.project_id).filter(Boolean))
  return projectIds.size
})

function getWarrantyType(status: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    case '无项目': return 'info'
    default: return 'info'
  }
}

function getDeviceTypeName(type: string) {
  const names: Record<string, string> = {
    traffic_light: '信号灯',
    electronic_police: '电子警察',
    parking_enforcement: '违停球',
    checkpoint: '卡口',
    backend_device: '后端设备'
  }
  return names[type] || type
}

function handleFilterChange() {
  currentPage.value = 1
}

function handleSearch() {
  currentPage.value = 1
}

function handleTabChange() {
  currentPage.value = 1
}

function handleSizeChange() {
  currentPage.value = 1
}

function handleCurrentChange() {}

async function fetchData() {
  loading.value = true
  try {
    const [projectsData, trafficLightsData, electronicPolicesData, parkingEnforcementsData, checkpointsData, backendDevicesData] = await Promise.all([
      projectApi.list(),
      intersectionApi.getTrafficLightsAll(),
      intersectionApi.getElectronicPolicesAll(),
      pointApi.getParkingEnforcementsAll(),
      pointApi.getCheckpointsAll(),
      pointApi.listBackendDevices()
    ])

    projects.value = (projectsData as any) || []
    trafficLights.value = (trafficLightsData as any) || []
    electronicPolices.value = (electronicPolicesData as any) || []
    parkingEnforcements.value = (parkingEnforcementsData as any) || []
    checkpoints.value = (checkpointsData as any) || []
    backendDevices.value = (backendDevicesData as any) || []
  } catch (error) {
    console.error('获取数据失败', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

async function exportData() {
  try {
    ElMessage.info('正在导出数据，请稍候...')
    const response = await apiClient.get('/export/statistics', {
      responseType: 'blob'
    }) as unknown as Blob
    const url = window.URL.createObjectURL(new Blob([response]))
    const link = document.createElement('a')
    link.href = url
    const filename = `智能交通设备统计_${new Date().toISOString().split('T')[0]}.xlsx`
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
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

  .header-actions {
    display: flex;
    gap: $spacing-sm;
  }
}

.filter-container {
  background: $bg-card;
  padding: $spacing-md;
  border-radius: $radius-md;
  margin-bottom: $spacing-md;

  .el-select {
    width: 100%;
  }

  .el-input {
    width: 100%;
  }
}

.stats-summary {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-md;

  .summary-item {
    flex: 1;
    background: $bg-card;
    padding: $spacing-md;
    border-radius: $radius-md;
    text-align: center;

    .summary-label {
      display: block;
      font-size: $font-size-xs;
      color: $text-secondary;
      margin-bottom: $spacing-xs;
    }

    .summary-value {
      font-size: 24px;
      font-weight: 700;
      color: $text-primary;

      &.success {
        color: $success-color;
      }

      &.danger {
        color: $error-color;
      }
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: $spacing-md;
  padding: $spacing-md;
  background: $bg-card;
  border-radius: $radius-md;
}
</style>