<template>
  <div class="intersection-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>路口列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showDialog = true">新增路口</el-button>
        </div>
      </template>

      <div class="filter-bar">
        <el-row :gutter="12">
          <el-col :span="10">
            <el-select v-model="filterWarranty" placeholder="质保状态" clearable>
              <el-option label="全部" value="" />
              <el-option label="在保" value="在保" />
              <el-option label="过保" value="过保" />
              <el-option label="混合状态" value="混合状态" />
              <el-option label="点位无关联项目" value="点位无关联项目" />
            </el-select>
          </el-col>
          <el-col :span="14">
            <el-input v-model="searchKeyword" placeholder="搜索路口名称、道路..." clearable>
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-col>
        </el-row>
      </div>

      <el-table :data="pagedIntersections" stripe v-loading="loading">
        <el-table-column label="序号" width="60">
          <template #default="{ $index }">
            {{ (currentPage - 1) * perPage + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="路口名称" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="east_west_road" label="东西路" />
        <el-table-column prop="north_south_road" label="南北路" />
        <el-table-column prop="latitude" label="纬度" width="120" />
        <el-table-column prop="longitude" label="经度" width="120" />
        <el-table-column label="质保状态" width="100" align="center">
          <template #default="{ row }">
            <div class="warranty-circle" :title="getWarrantyStatus(row.id)">
              <div class="half-circle left" :style="{ backgroundColor: getTlColor(row.id) }"></div>
              <div class="half-circle right" :style="{ backgroundColor: getEpColor(row.id) }"></div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="附件" width="80" align="center">
          <template #default="{ row }">
            <span :class="hasAttachment(row.id) ? 'status-dot green' : 'status-dot gray'" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToDetail(row.id)">
              详情
            </el-button>
            <el-button v-if="userStore.isEditor" type="success" size="small" @click="editIntersection(row)">
              编辑
            </el-button>
            <el-button v-if="userStore.isEditor" type="danger" size="small" @click="deleteIntersection(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="perPage"
          :total="filteredIntersections.length"
          layout="total, prev, pager, next"
          class="dark-pagination"
        />
      </div>
    </el-card>

    <el-dialog v-model="showDialog" :title="editIntersectionForm.id ? '编辑路口' : '新增路口'" width="400px">
      <el-form :model="editIntersectionForm" label-width="80px">
        <el-form-item label="路口名称" required>
          <el-input v-model="editIntersectionForm.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="editIntersectionForm.type" placeholder="请选择路口类型">
            <el-option label="十字路口" value="十字路口" />
            <el-option label="丁字路口" value="丁字路口" />
            <el-option label="行人过街" value="行人过街" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="东西路">
          <el-input v-model="editIntersectionForm.east_west_road" />
        </el-form-item>
        <el-form-item label="南北路">
          <el-input v-model="editIntersectionForm.north_south_road" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input v-model.number="editIntersectionForm.latitude" placeholder="例如：31.2304" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input v-model.number="editIntersectionForm.longitude" placeholder="例如：121.4737" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitIntersection">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { intersectionApi } from '@/api/intersections'
import { attachmentApi, type Attachment } from '@/api/attachments'
import { useUserStore } from '@/stores/user'
import type { Intersection } from '@/types'
import { eventBus } from '@/utils/eventBus'

const router = useRouter()
const userStore = useUserStore()
const allIntersections = ref<Intersection[]>([])
const allTrafficLights = ref<any[]>([])
const allElectronicPolices = ref<any[]>([])
const allAttachments = ref<Attachment[]>([])
const loading = ref(false)
const showDialog = ref(false)
const currentPage = ref(1)
const perPage = ref(15)
const searchKeyword = ref('')
const filterWarranty = ref('')

const filteredIntersections = computed(() => {
  return allIntersections.value.filter(i => {
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      const haystack = [i.name, i.type, i.east_west_road, i.north_south_road].filter(Boolean).join(' ').toLowerCase()
      if (!haystack.includes(kw)) return false
    }
    if (filterWarranty.value) {
      const status = (i as any).warranty_status
      if (status !== filterWarranty.value) return false
    }
    return true
  })
})

const pagedIntersections = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredIntersections.value.slice(start, start + perPage.value)
})

watch([searchKeyword, filterWarranty], () => {
  currentPage.value = 1
})

const editIntersectionForm = reactive<Partial<Intersection>>({
  id: undefined,
  name: '',
  type: '',
  east_west_road: '',
  north_south_road: '',
  latitude: undefined,
  longitude: undefined
})

function goToDetail(id: number) {
  router.push(`/intersections/${id}`)
}

function editIntersection(row: Intersection) {
  editIntersectionForm.id = row.id
  editIntersectionForm.name = row.name
  editIntersectionForm.type = row.type || ''
  editIntersectionForm.east_west_road = row.east_west_road || ''
  editIntersectionForm.north_south_road = row.north_south_road || ''
  showDialog.value = true
}

async function submitIntersection() {
  try {
    if (editIntersectionForm.id) {
      await intersectionApi.update(editIntersectionForm.id, editIntersectionForm)
      ElMessage.success('更新成功')
    } else {
      await intersectionApi.create(editIntersectionForm)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    editIntersectionForm.id = undefined
    editIntersectionForm.name = ''
    editIntersectionForm.type = ''
    editIntersectionForm.east_west_road = ''
    editIntersectionForm.north_south_road = ''
    fetchData()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '操作失败')
  }
}

async function deleteIntersection(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该路口吗？', '警告', { type: 'warning' })
    await intersectionApi.delete(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '删除失败')
    }
  }
}

async function fetchData() {
  loading.value = true
  try {
    const [intersections, trafficLights, electronicPolices, attachmentsRes] = await Promise.all([
      intersectionApi.list({ per_page: 0 }),
      intersectionApi.getTrafficLightsAll(),
      intersectionApi.getElectronicPolicesAll(),
      attachmentApi.list('intersection')
    ])
    allIntersections.value = intersections.data
    allTrafficLights.value = trafficLights.data || []
    allElectronicPolices.value = electronicPolices.data || []
    allAttachments.value = attachmentsRes.data || []
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

function hasAttachment(intersectionId: number): boolean {
  return allAttachments.value.some(a => a.related_entity_id === intersectionId)
}

function getIntersectionWarranty(intersectionId: number) {
  const trafficLights = allTrafficLights.value.filter(tl => tl.intersection_id === intersectionId)
  const electronicPolices = allElectronicPolices.value.filter(ep => ep.intersection_id === intersectionId)

  // 获取信号灯质保状态（取最晚日期）
  let tlStatus = '点位无关联项目'
  if (trafficLights.length > 0) {
    const validDates = trafficLights
      .map(tl => tl.warranty_expire_date)
      .filter(d => d)
    if (validDates.length > 0) {
      const latestDate = new Date(Math.max(...validDates.map(d => new Date(d).getTime())))
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      tlStatus = latestDate >= today ? '在保' : '过保'
    }
  }

  // 获取电子警察质保状态（取最晚日期）
  let epStatus = '点位无关联项目'
  if (electronicPolices.length > 0) {
    const validDates = electronicPolices
      .map(ep => ep.warranty_expire_date)
      .filter(d => d)
    if (validDates.length > 0) {
      const latestDate = new Date(Math.max(...validDates.map(d => new Date(d).getTime())))
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      epStatus = latestDate >= today ? '在保' : '过保'
    }
  }

  // 判断路口整体状态
  if ((tlStatus === '过保' && epStatus === '在保') || (tlStatus === '在保' && epStatus === '过保')) {
    return '混合状态'
  } else if (tlStatus === '在保' && epStatus === '在保') {
    return '在保'
  } else if (tlStatus === '过保' && epStatus === '过保') {
    return '过保'
  } else if (tlStatus === '点位无关联项目') {
    return '点位无关联项目'
  } else if (epStatus === '点位无关联项目' && (tlStatus === '在保' || tlStatus === '过保')) {
    return tlStatus
  }
  return '点位无关联项目'
}

function getWarrantyStatus(intersectionId: number): string {
  return getIntersectionWarranty(intersectionId)
}

function getDeviceStatus(intersectionId: number, deviceType: 'tl' | 'ep'): string {
  const devices = deviceType === 'tl'
    ? allTrafficLights.value.filter(tl => tl.intersection_id === intersectionId)
    : allElectronicPolices.value.filter(ep => ep.intersection_id === intersectionId)

  if (devices.length === 0) return '无项目'

  const validDates = devices
    .map(d => d.warranty_expire_date)
    .filter(d => d)
  if (validDates.length === 0) return '无项目'

  const latestDate = new Date(Math.max(...validDates.map(d => new Date(d).getTime())))
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return latestDate >= today ? '在保' : '过保'
}

function getTlColor(intersectionId: number): string {
  const status = getDeviceStatus(intersectionId, 'tl')
  if (status === '在保') return '#22c55e' // 鲜艳绿色
  if (status === '过保') return '#ef4444' // 鲜艳红色
  return '#6b7280' // 灰色
}

function getEpColor(intersectionId: number): string {
  const status = getDeviceStatus(intersectionId, 'ep')
  if (status === '在保') return '#22c55e' // 鲜艳绿色
  if (status === '过保') return '#ef4444' // 鲜艳红色
  return '#6b7280' // 灰色
}

function handleDataUpdated() {
  fetchData()
}

onMounted(() => {
  fetchData()
  eventBus.on('dataUpdated', handleDataUpdated)
})

onUnmounted(() => {
  eventBus.off('dataUpdated', handleDataUpdated)
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  margin-bottom: 16px;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.green {
  background-color: #67c23a;
}

.status-dot.gray {
  background-color: #909399;
}

.warranty-circle {
  width: 13px;
  height: 13px;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  display: inline-flex;
}

.half-circle {
  width: 6.5px;
  height: 13px;
}

.half-circle.left {
  border-radius: 6.5px 0 0 6.5px;
}

.half-circle.right {
  border-radius: 0 6.5px 6.5px 0;
}
</style>
