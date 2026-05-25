<template>
  <div class="intersection-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>路口详情 - {{ intersection?.name }}</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="intersection">
        <el-descriptions-item label="名称">{{ intersection.name }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ intersection.type }}</el-descriptions-item>
        <el-descriptions-item label="质保状态">
          <el-tag :type="getStatusType(intersection.warranty_status)">
            {{ intersection.warranty_status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="质保到期">
          {{ intersection.latest_expire_date || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <el-tabs v-model="activeTab">
        <el-tab-pane label="信号灯" name="trafficLights">
          <el-table :data="trafficLights" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="signal_type" label="信号机类型" />
            <el-table-column prop="signal_count" label="信号灯数" />
            <el-table-column prop="pedestrian_count" label="人行信号灯数" />
            <el-table-column prop="power_source" label="取电说明" />
            <el-table-column v-if="userStore.isEditor" label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editTrafficLight(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="电子警察" name="electronicPolices">
          <el-table :data="electronicPolices" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="capture_type" label="抓拍类型" />
            <el-table-column prop="forward_capture_count" label="正向抓拍" />
            <el-table-column prop="reverse_capture_count" label="反向抓拍" />
            <el-table-column prop="network_source" label="取网说明" />
            <el-table-column v-if="userStore.isEditor" label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editElectronicPolice(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="editForm" label-width="120px">
        <el-form-item v-for="(value, key) in editForm" :key="key" :label="getFieldLabel(key)">
          <el-input v-model="editForm[key]" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { intersectionApi, type IntersectionDetail } from '@/api/intersections'
import { useUserStore } from '@/stores/user'
import type { TrafficLight, ElectronicPolice } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const intersection = ref<IntersectionDetail['intersection']>(null)
const trafficLights = ref<TrafficLight[]>([])
const electronicPolices = ref<ElectronicPolice[]>([])
const activeTab = ref('trafficLights')

const dialogVisible = ref(false)
const dialogTitle = ref('')
const editForm = ref<Record<string, any>>({})
const editType = ref<'trafficLight' | 'electronicPolice'>('trafficLight')

function getStatusType(status?: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    default: return 'info'
  }
}

function getFieldLabel(key: string) {
  const labels: Record<string, string> = {
    signal_type: '信号机类型',
    signal_count: '信号灯数',
    power_source: '取电说明',
    capture_type: '抓拍类型',
    network_source: '取网说明'
  }
  return labels[key] || key
}

function editTrafficLight(row: TrafficLight) {
  editType.value = 'trafficLight'
  dialogTitle.value = '编辑信号灯'
  editForm.value = { ...row }
  dialogVisible.value = true
}

function editElectronicPolice(row: ElectronicPolice) {
  editType.value = 'electronicPolice'
  dialogTitle.value = '编辑电子警察'
  editForm.value = { ...row }
  dialogVisible.value = true
}

async function submitEdit() {
  try {
    if (editType.value === 'trafficLight') {
      await intersectionApi.updateTrafficLight(
        Number(route.params.id),
        editForm.value.id,
        editForm.value
      )
    } else {
      await intersectionApi.updateElectronicPolice(
        Number(route.params.id),
        editForm.value.id,
        editForm.value
      )
    }
    ElMessage.success('更新成功')
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

async function fetchData() {
  loading.value = true
  try {
    const data = await intersectionApi.getById(Number(route.params.id))
    intersection.value = data.intersection
    trafficLights.value = data.traffic_lights
    electronicPolices.value = data.electronic_polices
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>