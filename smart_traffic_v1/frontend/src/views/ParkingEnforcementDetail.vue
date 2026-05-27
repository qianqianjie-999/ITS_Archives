<template>
  <div class="parking-enforcement-detail">
    <div class="detail-header">
      <el-button @click="goBack">返回</el-button>
      <h2>{{ point?.name || '违停点位详情' }}</h2>
    </div>

    <el-card v-if="point" class="point-info">
      <template #header>
        <span>点位信息</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="点位名称">{{ point.name }}</el-descriptions-item>
        <el-descriptions-item label="区域">{{ point.area || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="device-section">
      <template #header>
        <div class="card-header">
          <span>违停球设备</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showAddDialog = true">新增违停球</el-button>
        </div>
      </template>
      <el-table :data="parkingEnforcements" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="camera_area" label="抓拍区域" />
        <el-table-column prop="project_name" label="归属项目" />
        <el-table-column prop="acceptance_date" label="项目验收日期" width="140" />
        <el-table-column prop="warranty_period" label="项目质保期" width="120" />
        <el-table-column prop="warranty_expire_date" label="项目质保到期时间" width="160" />
        <el-table-column prop="warranty_status" label="质保状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.warranty_status)">
              {{ row.warranty_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="construction_unit" label="建设单位" />
        <el-table-column prop="construction_company" label="施工单位" />
        <el-table-column prop="camera_count" label="抓拍机数量" width="120" />
        <el-table-column prop="parking_sign_count" label="违停标牌数量" width="120" />
        <el-table-column prop="monitor_sign_count" label="监控标牌数量" width="120" />
        <el-table-column prop="power_source" label="取电说明" />
        <el-table-column prop="network_source" label="取网说明" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button v-if="userStore.isEditor" type="success" size="small" @click="editDevice(row)">
              编辑
            </el-button>
            <el-button v-if="userStore.isEditor" type="danger" size="small" @click="deleteDevice(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" :title="editForm.id ? '编辑违停球' : '新增违停球'" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="抓拍区域">
          <el-input v-model="editForm.camera_area" />
        </el-form-item>
        <el-form-item label="抓拍机数量">
          <el-input-number v-model="editForm.camera_count" :min="0" />
        </el-form-item>
        <el-form-item label="违停标牌数量">
          <el-input-number v-model="editForm.parking_sign_count" :min="0" />
        </el-form-item>
        <el-form-item label="监控标牌数量">
          <el-input-number v-model="editForm.monitor_sign_count" :min="0" />
        </el-form-item>
        <el-form-item label="取电说明">
          <el-input v-model="editForm.power_source" />
        </el-form-item>
        <el-form-item label="取网说明">
          <el-input v-model="editForm.network_source" />
        </el-form-item>
        <el-form-item label="归属项目" required>
          <el-select v-model="editForm.project_id" placeholder="请选择项目">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitDevice">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pointApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import { useUserStore } from '@/stores/user'
import type { Point, ParkingEnforcement, Project } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const point = ref<Point | null>(null)
const parkingEnforcements = ref<ParkingEnforcement[]>([])
const projects = ref<Project[]>([])
const loading = ref(false)
const showAddDialog = ref(false)

const editForm = reactive<Partial<ParkingEnforcement>>({
  id: undefined,
  camera_area: '',
  camera_count: 0,
  parking_sign_count: 0,
  monitor_sign_count: 0,
  power_source: '',
  network_source: '',
  project_id: undefined
})

function getStatusType(status?: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    case '无项目': return 'warning'
    default: return 'info'
  }
}

function goBack() {
  router.push('/parking-enforcements')
}

function editDevice(device: ParkingEnforcement) {
  editForm.id = device.id
  editForm.camera_area = device.camera_area || ''
  editForm.camera_count = device.camera_count || 0
  editForm.parking_sign_count = device.parking_sign_count || 0
  editForm.monitor_sign_count = device.monitor_sign_count || 0
  editForm.power_source = device.power_source || ''
  editForm.network_source = device.network_source || ''
  editForm.project_id = device.project_id
  showAddDialog.value = true
}

function submitDevice() {
  if (!editForm.project_id) {
    ElMessage.error('请选择归属项目')
    return
  }

  const data = {
    camera_area: editForm.camera_area || '',
    camera_count: editForm.camera_count || 0,
    parking_sign_count: editForm.parking_sign_count || 0,
    monitor_sign_count: editForm.monitor_sign_count || 0,
    power_source: editForm.power_source || '',
    network_source: editForm.network_source || '',
    project_id: editForm.project_id
  }

  const pointId = Number(route.params.id)
  
  if (editForm.id) {
    pointApi.updateParkingEnforcement(pointId, editForm.id, data).then(() => {
      ElMessage.success('编辑成功')
      showAddDialog.value = false
      loadData()
    }).catch(() => {
      ElMessage.error('编辑失败')
    })
  } else {
    pointApi.createParkingEnforcement(pointId, data).then(() => {
      ElMessage.success('新增成功')
      showAddDialog.value = false
      loadData()
    }).catch(() => {
      ElMessage.error('新增失败')
    })
  }
}

function deleteDevice(id: number) {
  const pointId = Number(route.params.id)
  ElMessageBox.confirm('确定删除该设备？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    pointApi.deleteParkingEnforcement(pointId, id).then(() => {
      ElMessage.success('删除成功')
      loadData()
    }).catch(() => {
      ElMessage.error('删除失败')
    })
  }).catch(() => {})
}

function loadData() {
  loading.value = true
  const pointId = Number(route.params.id)
  
  Promise.all([
    pointApi.get(pointId),
    projectApi.list()
  ]).then(([pointDetail, projectList]) => {
    point.value = pointDetail.point
    parkingEnforcements.value = pointDetail.parking_enforcements || []
    projects.value = projectList
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

onMounted(() => {
  loadData()
})
</script>
