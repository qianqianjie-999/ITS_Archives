<template>
  <div class="point-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>点位详情 - {{ point?.name }}</span>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="point">
        <el-descriptions-item label="名称">{{ point.name }}</el-descriptions-item>
        <el-descriptions-item label="区域">{{ point.area || '-' }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ point.type }}</el-descriptions-item>
        <el-descriptions-item label="质保状态">
          <el-tag :type="getStatusType(point.warranty_status)">
            {{ point.warranty_status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="质保到期">
          {{ point.latest_expire_date || '-' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <el-tabs v-model="activeTab">
        <el-tab-pane label="违停抓拍" name="parkingEnforcements">
          <div class="tab-header">
            <span>违停抓拍设备列表</span>
            <el-button v-if="userStore.isEditor" type="primary" size="small" @click="showParkingDialog = true">新增设备</el-button>
          </div>
          <el-table :data="parkingEnforcements" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="camera_count" label="抓拍机数量" />
            <el-table-column prop="network_source" label="取网说明" />
            <el-table-column prop="warranty_expire_date" label="质保到期" />
            <el-table-column v-if="userStore.isEditor" label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editParkingEnforcement(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteParkingEnforcement(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="治安卡口" name="checkpoints">
          <div class="tab-header">
            <span>治安卡口设备列表</span>
            <el-button v-if="userStore.isEditor" type="primary" size="small" @click="showCheckpointDialog = true">新增设备</el-button>
          </div>
          <el-table :data="checkpoints" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="device_count" label="设备数量" />
            <el-table-column prop="camera_count" label="摄像机数量" />
            <el-table-column prop="network_source" label="取网说明" />
            <el-table-column prop="warranty_expire_date" label="质保到期" />
            <el-table-column v-if="userStore.isEditor" label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editCheckpoint(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteCheckpoint(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="附件" name="attachments">
          <div class="tab-header">
            <span>附件列表</span>
            <el-button v-if="userStore.isEditor" type="primary" size="small" @click="triggerFileInput()">上传附件</el-button>
          </div>
          <input
            ref="fileInputRef"
            type="file"
            style="display: none"
            @change="handleFileUpload"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif"
          />
          <el-table :data="attachments" stripe>
            <el-table-column prop="original_filename" label="文件名" />
            <el-table-column prop="file_size" label="大小" width="100">
              <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
            </el-table-column>
            <el-table-column prop="upload_time" label="上传时间" width="150" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="downloadAttachment(row.id)">下载</el-button>
                <el-button v-if="userStore.isEditor" type="danger" size="small" @click="deleteAttachment(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="质保延期" name="warranty">
          <div class="tab-header">
            <span>质保延期记录</span>
            <el-button v-if="userStore.isEditor" type="primary" size="small" @click="showWarrantyDialog = true">申请质保延期</el-button>
          </div>
          <el-table :data="warrantyRecords" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="acceptance_date" label="验收日期" />
            <el-table-column prop="warranty_expire_date" label="质保到期" />
            <el-table-column prop="extension_date" label="延期日期" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="showWarrantyDialog" title="申请质保延期" width="400px">
      <el-form :model="warrantyForm" label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="warrantyForm.projectName" />
        </el-form-item>
        <el-form-item label="质保到期日期" required>
          <el-date-picker v-model="warrantyForm.expireDate" type="date" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showWarrantyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitWarranty">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showParkingDialog" :title="parkingForm.id ? '编辑违停抓拍' : '新增违停抓拍'" width="600px">
      <el-form :model="parkingForm" label-width="120px">
        <el-form-item label="归属项目" required>
          <el-select v-model="parkingForm.project_id" placeholder="请选择项目" filterable>
            <el-option v-for="project in projectOptions" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="抓拍区域">
          <el-input v-model="parkingForm.area" placeholder="如：XX路与XX路交叉口" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备数量">
              <el-input-number v-model="parkingForm.device_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="抓拍机数量">
              <el-input-number v-model="parkingForm.camera_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="违停标牌数量">
              <el-input-number v-model="parkingForm.parking_sign_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="监控标牌数量">
              <el-input-number v-model="parkingForm.monitor_sign_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="取电说明">
          <el-input v-model="parkingForm.power_source" placeholder="如：市电、太阳能" />
        </el-form-item>
        <el-form-item label="取网说明">
          <el-input v-model="parkingForm.network_source" placeholder="如：光纤、无线" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showParkingDialog = false">取消</el-button>
        <el-button type="primary" @click="submitParkingEnforcement">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCheckpointDialog" :title="checkpointForm.id ? '编辑治安卡口' : '新增治安卡口'" width="600px">
      <el-form :model="checkpointForm" label-width="120px">
        <el-form-item label="归属项目" required>
          <el-select v-model="checkpointForm.project_id" placeholder="请选择项目" filterable>
            <el-option v-for="project in projectOptions" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="卡口类型">
          <el-select v-model="checkpointForm.type" placeholder="请选择卡口类型">
            <el-option label="雷达测速卡口" value="雷达测速卡口" />
            <el-option label="闯禁区卡口" value="闯禁区卡口" />
            <el-option label="大货车不靠右行驶卡口" value="大货车不靠右行驶卡口" />
            <el-option label="单行道卡口" value="单行道卡口" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备数量">
              <el-input-number v-model="checkpointForm.device_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="抓拍机数量">
              <el-input-number v-model="checkpointForm.camera_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="爆闪灯数量">
              <el-input-number v-model="checkpointForm.strobe_light_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="测速雷达数量">
              <el-input-number v-model="checkpointForm.radar_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="标牌数量">
          <el-input-number v-model="checkpointForm.sign_count" :min="0" />
        </el-form-item>
        <el-form-item label="取电说明">
          <el-input v-model="checkpointForm.power_source" placeholder="如：市电" />
        </el-form-item>
        <el-form-item label="取网说明">
          <el-input v-model="checkpointForm.network_source" placeholder="如：光纤" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCheckpointDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCheckpoint">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pointApi, type PointDetail } from '@/api/points'
import { attachmentApi, type Attachment } from '@/api/attachments'
import { projectApi } from '@/api/projects'
import { useUserStore } from '@/stores/user'
import type { ParkingEnforcement, Checkpoint, Project } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const point = ref<PointDetail['point'] | null>(null)
const attachments = ref<Attachment[]>([])
const warrantyRecords = ref<WarrantyRecord[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const parkingEnforcements = ref<ParkingEnforcement[]>([])
const checkpoints = ref<Checkpoint[]>([])
const activeTab = ref('parkingEnforcements')

const showParkingDialog = ref(false)
const showCheckpointDialog = ref(false)
const showWarrantyDialog = ref(false)

interface WarrantyRecord {
  project_name: string
  acceptance_date: string
  warranty_expire_date: string
  extension_date: string
}

interface ProjectOption {
  id: number
  name: string
}

const projectOptions = ref<ProjectOption[]>([])

const warrantyForm = reactive({
  projectName: '',
  expireDate: ''
})

const parkingForm = reactive<Partial<ParkingEnforcement>>({
  id: undefined,
  project_id: undefined,
  project_name: '',
  area: '',
  device_count: 0,
  camera_count: 0,
  parking_sign_count: 0,
  monitor_sign_count: 0,
  power_source: '',
  network_source: ''
})

const checkpointForm = reactive<Partial<Checkpoint>>({
  id: undefined,
  project_id: undefined,
  project_name: '',
  type: '',
  device_count: 0,
  camera_count: 0,
  strobe_light_count: 0,
  radar_count: 0,
  sign_count: 0,
  power_source: '',
  network_source: ''
})

function getStatusType(status?: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    default: return 'info'
  }
}

function editParkingEnforcement(row: ParkingEnforcement) {
  Object.assign(parkingForm, {
    id: row.id,
    project_id: row.project_id,
    project_name: row.project_name,
    area: row.area,
    device_count: row.device_count || 0,
    camera_count: row.camera_count || 0,
    parking_sign_count: row.parking_sign_count || 0,
    monitor_sign_count: row.monitor_sign_count || 0,
    power_source: row.power_source,
    network_source: row.network_source
  })
  showParkingDialog.value = true
}

async function submitParkingEnforcement() {
  try {
    if (parkingForm.id) {
      await pointApi.updateParkingEnforcement(
        Number(route.params.id),
        parkingForm.id,
        parkingForm
      )
      ElMessage.success('更新成功')
    } else {
      await pointApi.createParkingEnforcement(Number(route.params.id), parkingForm)
      ElMessage.success('创建成功')
    }
    showParkingDialog.value = false
    parkingForm.id = undefined
    parkingForm.project_id = undefined
    parkingForm.project_name = ''
    parkingForm.area = ''
    parkingForm.device_count = 0
    parkingForm.camera_count = 0
    parkingForm.parking_sign_count = 0
    parkingForm.monitor_sign_count = 0
    parkingForm.power_source = ''
    parkingForm.network_source = ''
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteParkingEnforcement(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该设备吗？', '警告', { type: 'warning' })
    await pointApi.deleteParkingEnforcement(Number(route.params.id), id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function editCheckpoint(row: Checkpoint) {
  Object.assign(checkpointForm, {
    id: row.id,
    project_id: row.project_id,
    project_name: row.project_name,
    type: row.type,
    device_count: row.device_count || 0,
    camera_count: row.camera_count || 0,
    strobe_light_count: row.strobe_light_count || 0,
    radar_count: row.radar_count || 0,
    sign_count: row.sign_count || 0,
    power_source: row.power_source,
    network_source: row.network_source
  })
  showCheckpointDialog.value = true
}

async function submitCheckpoint() {
  try {
    if (checkpointForm.id) {
      await pointApi.updateCheckpoint(
        Number(route.params.id),
        checkpointForm.id,
        checkpointForm
      )
      ElMessage.success('更新成功')
    } else {
      await pointApi.createCheckpoint(Number(route.params.id), checkpointForm)
      ElMessage.success('创建成功')
    }
    showCheckpointDialog.value = false
    checkpointForm.id = undefined
    checkpointForm.project_id = undefined
    checkpointForm.project_name = ''
    checkpointForm.type = ''
    checkpointForm.device_count = 0
    checkpointForm.camera_count = 0
    checkpointForm.strobe_light_count = 0
    checkpointForm.radar_count = 0
    checkpointForm.sign_count = 0
    checkpointForm.power_source = ''
    checkpointForm.network_source = ''
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteCheckpoint(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该设备吗？', '警告', { type: 'warning' })
    await pointApi.deleteCheckpoint(Number(route.params.id), id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    try {
      await attachmentApi.upload(file, 'point', Number(route.params.id))
      ElMessage.success('上传成功')
      fetchAttachments()
    } catch (error) {
      ElMessage.error('上传失败')
    }
    target.value = ''
  }
}

async function downloadAttachment(id: number) {
  try {
    const response = await attachmentApi.download(id) as unknown as Blob
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `attachment_${id}`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

async function deleteAttachment(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该附件吗？', '警告', { type: 'warning' })
    await attachmentApi.delete(id)
    ElMessage.success('删除成功')
    fetchAttachments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function fetchAttachments() {
  try {
    const res = await attachmentApi.list('point', Number(route.params.id))
    attachments.value = res as unknown as Attachment[]
  } catch (error) {
    console.error('获取附件失败', error)
  }
}

async function fetchWarrantyRecords() {
  try {
    const projectApi = await import('@/api/projects')
    const records = await projectApi.projectApi.getByFacility('point', Number(route.params.id)) as unknown as Project[]
    warrantyRecords.value = records.map((project) => ({
      project_name: project.name,
      acceptance_date: project.acceptance_date || '',
      warranty_expire_date: project.warranty_expire_date,
      extension_date: project.acceptance_date || ''
    }))
  } catch (error) {
    console.error('获取质保延期记录失败', error)
  }
}

async function submitWarranty() {
  try {
    if (!warrantyForm.projectName || !warrantyForm.expireDate) {
      ElMessage.warning('请填写完整信息')
      return
    }
    await pointApi.extendWarranty(
      Number(route.params.id),
      warrantyForm.projectName,
      warrantyForm.expireDate
    )
    ElMessage.success('申请成功')
    showWarrantyDialog.value = false
    warrantyForm.projectName = ''
    warrantyForm.expireDate = ''
    await fetchWarrantyRecords()
    await fetchData()
  } catch (error) {
    ElMessage.error('申请失败')
  }
}

async function fetchProjects() {
  try {
    const projects = await projectApi.list() as unknown as Project[]
    projectOptions.value = projects.map(p => ({
      id: p.id,
      name: p.name
    }))
  } catch (error) {
    console.error('获取项目列表失败', error)
  }
}

async function fetchData() {
  loading.value = true
  try {
    await fetchProjects()
    const data = await pointApi.getById(Number(route.params.id)) as unknown as PointDetail
    point.value = data.point
    parkingEnforcements.value = data.parking_enforcements
    checkpoints.value = data.checkpoints
    await fetchAttachments()
    await fetchWarrantyRecords()
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.card-header, .tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tab-header {
  margin-bottom: 16px;
}
</style>