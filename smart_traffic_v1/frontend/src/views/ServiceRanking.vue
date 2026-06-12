<template>
  <div class="service-ranking-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">点位设备服役期限排名</h1>
        <p class="page-subtitle">按服役年限从长到短排列 · 全部设备一览</p>
      </div>
    </div>

    <div class="summary-bar">
    <div class="summary-item">
      <span class="sum-label">统计设备数</span>
      <span class="sum-value">{{ filteredList.length }}</span>
    </div>
    <div class="summary-item">
      <span class="sum-label">最长服役</span>
      <span class="sum-value">{{ longestDuration }}年</span>
    </div>
    <div class="summary-item">
      <span class="sum-label">平均服役</span>
      <span class="sum-value">{{ averageDuration }}年</span>
    </div>
  </div>

    <div class="filter-bar">
      <el-row :gutter="12">
        <el-col :span="6">
          <el-select v-model="filterType" placeholder="设备类型" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="信号灯" value="信号灯" />
            <el-option label="电子警察" value="电子警察" />
            <el-option label="违停球" value="违停球" />
            <el-option label="卡口" value="卡口" />
            <el-option label="结构化相机" value="结构化相机" />
            <el-option label="后端设备" value="后端设备" />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-input v-model="searchKeyword" placeholder="搜索设备名称..." clearable @input="handleFilter">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
      </el-row>
    </div>

    <div class="ranking-table-container">
      <el-table :data="pagedList" stripe v-loading="loading" border>
        <el-table-column label="排名" width="80" align="center">
          <template #default="{ $index }">
            <div class="rank-badge" :class="getRankingClass((currentPage - 1) * pageSize + $index)">
              {{ (currentPage - 1) * pageSize + $index + 1 }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="设备名称" min-width="150" />
        <el-table-column prop="type" label="设备类型" width="120" />
        <el-table-column prop="acceptanceDate" label="验收日期" width="120" />
        <el-table-column label="服役年限" width="140" align="center">
          <template #default="{ row }">
            <span class="duration-highlight">{{ row.duration }} 年</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredList.length"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { intersectionApi } from '@/api/intersections'
import { pointApi, checkpointPointApi, backendDeviceApi, skyNetApi } from '@/api/points'

const loading = ref(false)
const allData = ref<any[]>([])
const searchKeyword = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const filteredList = computed(() => {
  let list = [...allData.value]
  
  if (filterType.value) {
    list = list.filter(item => item.type === filterType.value)
  }
  
  if (searchKeyword.value) {
    list = list.filter(item => 
      item.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  
  return list
})

const pagedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredList.value.slice(start, end)
})

const longestDuration = computed(() => {
  if (allData.value.length === 0) return '0.0';
  return allData.value[0].duration;
});

const averageDuration = computed(() => {
  if (allData.value.length === 0) return '0.0';
  const total = allData.value.reduce((sum, item) => sum + parseFloat(item.duration), 0);
  return (total / allData.value.length).toFixed(1);
});

function getRankingClass(index: number) {
  if (index === 0) return 'rank-gold'
  if (index === 1) return 'rank-silver'
  if (index === 2) return 'rank-bronze'
  return ''
}

function handleFilter() {
  currentPage.value = 1
}

function handleSizeChange(val: number) {
  pageSize.value = val
}

function handleCurrentChange(val: number) {
  currentPage.value = val
}

async function fetchAllData() {
  loading.value = true
  try {
    const [trafficLights, electronicPolices, parkingEnforcements, checkpoints, skyNetPoints, backendDevices] = await Promise.all([
      intersectionApi.getTrafficLightsAll(),
      intersectionApi.getElectronicPolicesAll(),
      pointApi.getParkingEnforcementsAll(),
      checkpointPointApi.getCheckpointsAll(),
      skyNetApi.getSkyNetsAll(),
      backendDeviceApi.list({ per_page: 0 })
    ])
    
    // 去重处理：按路口ID或点位ID去重，保留质保到期日期最靠近现在的记录
    const tlData = deduplicateByIntersection(trafficLights.data || [])
    const epData = deduplicateByIntersection(electronicPolices.data || [])
    const peData = deduplicateByPoint(parkingEnforcements.data || [])
    const cpData = deduplicateByPoint(checkpoints.data || [])
    const snData = deduplicateByPoint(skyNetPoints.data || [])
    
    const data: any[] = []
    const today = new Date()
    
    // 处理信号灯
    tlData.forEach((item: any) => {
      const acceptDate = item.acceptance_date || (item.project_info?.acceptance_date)
      if (!acceptDate) return
      const d = new Date(acceptDate)
      if (d > today) return
      const years = (today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24 * 365)
      if (years > 0) {
        data.push({
          id: item.id,
          name: item.intersection_name || item.name || '未知',
          type: '信号灯',
          acceptanceDate: acceptDate,
          duration: years.toFixed(1)
        })
      }
    })
    
    // 处理电子警察
    epData.forEach((item: any) => {
      const acceptDate = item.acceptance_date || (item.project_info?.acceptance_date)
      if (!acceptDate) return
      const d = new Date(acceptDate)
      if (d > today) return
      const years = (today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24 * 365)
      if (years > 0) {
        data.push({
          id: item.id,
          name: item.intersection_name || item.name || '未知',
          type: '电子警察',
          acceptanceDate: acceptDate,
          duration: years.toFixed(1)
        })
      }
    })
    
    // 处理违停球
    peData.forEach((item: any) => {
      const acceptDate = item.acceptance_date || (item.project_info?.acceptance_date)
      if (!acceptDate) return
      const d = new Date(acceptDate)
      if (d > today) return
      const years = (today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24 * 365)
      if (years > 0) {
        data.push({
          id: item.id,
          name: item.point_name || item.name || '未知',
          type: '违停球',
          acceptanceDate: acceptDate,
          duration: years.toFixed(1)
        })
      }
    })
    
    // 处理卡口
    cpData.forEach((item: any) => {
      const acceptDate = item.acceptance_date || (item.project_info?.acceptance_date)
      if (!acceptDate) return
      const d = new Date(acceptDate)
      if (d > today) return
      const years = (today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24 * 365)
      if (years > 0) {
        data.push({
          id: item.id,
          name: item.point_name || item.name || '未知',
          type: '卡口',
          acceptanceDate: acceptDate,
          duration: years.toFixed(1)
        })
      }
    })
    
    // 处理结构化相机
    snData.forEach((item: any) => {
      const acceptDate = item.acceptance_date || (item.project_info?.acceptance_date)
      if (!acceptDate) return
      const d = new Date(acceptDate)
      if (d > today) return
      const years = (today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24 * 365)
      if (years > 0) {
        data.push({
          id: item.id,
          name: item.point_name || item.name || '未知',
          type: '结构化相机',
          acceptanceDate: acceptDate,
          duration: years.toFixed(1)
        })
      }
    })
    
    // 处理后端设备
    const bdData = backendDevices.data || []
    bdData.forEach((item: any) => {
      const acceptDate = item.acceptance_date || (item.project_info?.acceptance_date)
      if (!acceptDate) return
      const d = new Date(acceptDate)
      if (d > today) return
      const years = (today.getTime() - d.getTime()) / (1000 * 60 * 60 * 24 * 365)
      if (years > 0) {
        data.push({
          id: item.id,
          name: item.name || '未知',
          type: '后端设备',
          acceptanceDate: acceptDate,
          duration: years.toFixed(1)
        })
      }
    })
    
    // 按服役年限降序排序
    data.sort((a, b) => parseFloat(b.duration) - parseFloat(a.duration))
    
    allData.value = data
  } catch (error) {
    console.error('获取数据失败', error)
  } finally {
    loading.value = false
  }
}

function deduplicateByIntersection(items: any[]): any[] {
  const map = new Map<number, any>()
  items.forEach(item => {
    const id = item.intersection_id
    if (!id) return
    if (!map.has(id)) {
      map.set(id, item)
    } else {
      const existing = map.get(id)
      if (shouldReplace(existing, item)) {
        map.set(id, item)
      }
    }
  })
  return Array.from(map.values())
}

function deduplicateByPoint(items: any[]): any[] {
  const map = new Map<number, any>()
  items.forEach(item => {
    const id = item.point_id || item.id
    if (!id) return
    if (!map.has(id)) {
      map.set(id, item)
    } else {
      const existing = map.get(id)
      if (shouldReplace(existing, item)) {
        map.set(id, item)
      }
    }
  })
  return Array.from(map.values())
}

function shouldReplace(existing: any, newItem: any): boolean {
  const existingDate = existing.warranty_expire_date
  const newDate = newItem.warranty_expire_date
  
  if (!existingDate) return !!newDate
  if (!newDate) return false
  
  const now = new Date().getTime()
  const existingTime = new Date(existingDate).getTime()
  const newTime = new Date(newDate).getTime()
  
  const existingDiff = Math.abs(existingTime - now)
  const newDiff = Math.abs(newTime - now)
  
  return newDiff < existingDiff
}

onMounted(() => {
  fetchAllData()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.service-ranking-page {
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
  margin-bottom: 20px;

  .page-title {
    font-size: 22px;
    font-weight: 700;
    color: $text-primary;
    margin: 0;
  }

  .page-subtitle {
    font-size: 13px;
    color: $text-secondary;
    margin: 4px 0 0;
  }
}

.summary-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;

  .summary-item {
    flex: 1;
    background: $bg-card;
    border-radius: $radius-md;
    padding: 16px 20px;
    box-shadow: $shadow-md;
    text-align: center;
    border: 1px solid $border-color;

    .sum-label {
      display: block;
      font-size: 12px;
      color: $text-secondary;
      margin-bottom: 4px;
    }

    .sum-value {
      font-size: 24px;
      font-weight: 700;
      color: $text-primary;
    }
  }
}

.filter-bar {
  background: $bg-card;
  padding: 12px 16px;
  border-radius: $radius-md;
  box-shadow: $shadow-md;
  margin-bottom: 16px;
  border: 1px solid $border-color;

  .el-select,
  .el-input {
    width: 100%;
  }
}

.ranking-table-container {
  background: $bg-card;
  border-radius: $radius-md;
  box-shadow: $shadow-md;
  border: 1px solid $border-color;
  overflow: hidden;
}

.rank-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--el-border-color);
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  margin: 0 auto;

  &.rank-gold {
    background: linear-gradient(135deg, #ffd700, #ffb700);
    color: white;
  }

  &.rank-silver {
    background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
    color: white;
  }

  &.rank-bronze {
    background: linear-gradient(135deg, #cd7f32, #b87333);
    color: white;
  }
}

.duration-highlight {
  font-weight: 700;
  color: $primary-color;
  font-size: 16px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
