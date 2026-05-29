<template>
  <div class="checkpoint-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>卡口点位详情 - {{ point?.name }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="point">
        <el-descriptions-item label="点位名称">{{ point.name }}</el-descriptions-item>
        <el-descriptions-item label="安装位置">{{ point.type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="卡口类型">{{ point.area || '-' }}</el-descriptions-item>
        <el-descriptions-item label="质保状态">
          <el-tag :type="getStatusType(point.status)">
            {{ point.status || '-' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <el-card class="device-section">
        <template #header>
          <div class="card-header">
            <span>卡口设备</span>
            <el-button v-if="userStore.isEditor" type="primary" @click="showAddDialog = true">添加卡口详情信息</el-button>
          </div>
        </template>
      <el-table :data="checkpoints" stripe v-loading="loading">
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
        <el-table-column prop="strobe_light_count" label="爆闪灯数量" width="120" />
        <el-table-column prop="radar_count" label="测速雷达数量" width="120" />
        <el-table-column prop="sign_count" label="标牌数量" width="120" />
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

    <el-card class="warranty-section" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>质保延期记录</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showExtendWarrantyDialog = true">质保延期</el-button>
        </div>
      </template>
      <el-table :data="warrantyExtensions" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="project_name" label="项目名称" />
        <el-table-column prop="warranty_expire_date" label="质保到期时间" width="160" />
        <el-table-column prop="extension_date" label="延期日期" width="140" />
        <el-table-column label="质保状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.warranty_expire_date)">
              {{ row.warranty_expire_date ? (new Date(row.warranty_expire_date) >= new Date() ? '在保' : '过保') : '-' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showExtendWarrantyDialog" title="质保延期" width="450px">
      <el-form :model="extendWarrantyForm" label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="extendWarrantyForm.project_name" placeholder="请输入质保延期项目名称" />
        </el-form-item>
        <el-form-item label="质保到期日期" required>
          <el-date-picker v-model="extendWarrantyForm.warranty_expire_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExtendWarrantyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitExtendWarranty">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddDialog" :title="editForm.id ? '编辑详情信息' : '添加卡口详情信息'" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="归属项目" required>
          <el-select v-model="editForm.project_id" placeholder="请选择项目">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="抓拍机数量">
          <el-input-number v-model="editForm.camera_count" :min="0" />
        </el-form-item>
        <el-form-item label="爆闪灯数量">
          <el-input-number v-model="editForm.strobe_light_count" :min="0" />
        </el-form-item>
        <el-form-item label="测速雷达数量">
          <el-input-number v-model="editForm.radar_count" :min="0" />
        </el-form-item>
        <el-form-item label="标牌数量">
          <el-input-number v-model="editForm.sign_count" :min="0" />
        </el-form-item>
        <el-form-item label="取电说明">
          <el-input v-model="editForm.power_source" />
        </el-form-item>
        <el-form-item label="取网说明">
          <el-input v-model="editForm.network_source" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitDevice">确定</el-button>
      </template>
    </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { checkpointPointApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import { useUserStore } from '@/stores/user'
import type { CheckpointPoint, Checkpoint, Project, WarrantyExtension } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const point = ref<CheckpointPoint | null>(null)
const checkpoints = ref<Checkpoint[]>([])
const projects = ref<Project[]>([])
const warrantyExtensions = ref<WarrantyExtension[]>([])
const loading = ref(false)
const showAddDialog = ref(false)
const showExtendWarrantyDialog = ref(false)

const extendWarrantyForm = reactive({
  project_name: '',
  warranty_expire_date: ''
})

const editForm = reactive<Partial<Checkpoint>>({
  id: undefined,
  checkpoint_type: '',
  camera_count: 0,
  strobe_light_count: 0,
  radar_count: 0,
  sign_count: 0,
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
  router.push('/checkpoints')
}

function editDevice(device: Checkpoint) {
  editForm.id = device.id
  editForm.checkpoint_type = device.checkpoint_type || ''
  editForm.camera_count = device.camera_count || 0
  editForm.strobe_light_count = device.strobe_light_count || 0
  editForm.radar_count = device.radar_count || 0
  editForm.sign_count = device.sign_count || 0
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
    checkpoint_type: editForm.checkpoint_type || '',
    camera_count: editForm.camera_count || 0,
    strobe_light_count: editForm.strobe_light_count || 0,
    radar_count: editForm.radar_count || 0,
    sign_count: editForm.sign_count || 0,
    power_source: editForm.power_source || '',
    network_source: editForm.network_source || '',
    project_id: editForm.project_id
  }

  const pointId = Number(route.params.id)
  
  if (editForm.id) {
    checkpointPointApi.updateCheckpoint(pointId, editForm.id, data).then(() => {
      ElMessage.success('编辑成功')
      showAddDialog.value = false
      loadData()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '编辑失败')
    })
  } else {
    checkpointPointApi.createCheckpoint(pointId, data).then(() => {
      ElMessage.success('新增成功')
      showAddDialog.value = false
      loadData()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '新增失败')
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
    checkpointPointApi.deleteCheckpoint(pointId, id).then(() => {
      ElMessage.success('删除成功')
      loadData()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '删除失败')
    })
  }).catch(() => {})
}

function loadData() {
  loading.value = true
  const pointId = Number(route.params.id)
  
  Promise.all([
    checkpointPointApi.get(pointId),
    projectApi.list()
  ]).then(([pointDetail, projectList]) => {
    point.value = pointDetail.point
    checkpoints.value = pointDetail.checkpoints || []
    warrantyExtensions.value = pointDetail.warranty_extensions || []
    projects.value = projectList
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

function submitExtendWarranty() {
  if (!extendWarrantyForm.project_name) {
    ElMessage.error('请输入项目名称')
    return
  }
  if (!extendWarrantyForm.warranty_expire_date) {
    ElMessage.error('请选择质保到期日期')
    return
  }
  const pointId = Number(route.params.id)
  checkpointPointApi.extendWarranty(pointId, {
    project_name: extendWarrantyForm.project_name,
    warranty_expire_date: extendWarrantyForm.warranty_expire_date
  }).then(() => {
    ElMessage.success('质保延期成功')
    showExtendWarrantyDialog.value = false
    extendWarrantyForm.project_name = ''
    extendWarrantyForm.warranty_expire_date = ''
    loadData()
  }).catch((err) => {
    ElMessage.error(err.response?.data?.message || '质保延期失败')
  })
}

onMounted(loadData)
</script>
