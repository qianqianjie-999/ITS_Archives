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
          <div class="tab-header">
            <span>信号灯列表</span>
            <el-button v-if="userStore.isEditor" type="primary" size="small" @click="showTrafficLightDialog = true">新增信号灯</el-button>
          </div>
          <el-table :data="trafficLights" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="signal_type" label="信号机类型" />
            <el-table-column prop="signal_count" label="信号灯数" />
            <el-table-column prop="left_arrow_count" label="左箭头数" />
            <el-table-column prop="straight_arrow_count" label="直箭头数" />
            <el-table-column prop="right_arrow_count" label="右箭头数" />
            <el-table-column prop="full_screen_count" label="全屏数" />
            <el-table-column prop="non_motor_count" label="非机动车数" />
            <el-table-column prop="pedestrian_count" label="人行信号灯数" />
            <el-table-column prop="radar_count" label="雷达数" />
            <el-table-column prop="guide_screen_count" label="诱导屏数" />
            <el-table-column prop="power_source" label="取电说明" />
            <el-table-column v-if="userStore.isEditor" label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editTrafficLight(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteTrafficLight(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="电子警察" name="electronicPolices">
          <div class="tab-header">
            <span>电子警察列表</span>
            <el-button v-if="userStore.isEditor" type="primary" size="small" @click="showElectronicPoliceDialog = true">新增电子警察</el-button>
          </div>
          <el-table :data="electronicPolices" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="capture_type" label="抓拍类型" />
            <el-table-column prop="terminal_server_count" label="终端服务器数" />
            <el-table-column prop="forward_capture_count" label="正向抓拍数" />
            <el-table-column prop="reverse_capture_count" label="反向抓拍数" />
            <el-table-column prop="led_light_count" label="LED补光灯数" />
            <el-table-column prop="strobe_light_count" label="频闪灯数" />
            <el-table-column prop="ptz_count" label="球机数" />
            <el-table-column prop="signal_detector_count" label="信号检测器数" />
            <el-table-column prop="network_source" label="取网说明" />
            <el-table-column v-if="userStore.isEditor" label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editElectronicPolice(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteElectronicPolice(row.id)">删除</el-button>
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
            accept=".pdf,.jpg,.jpeg,.png"
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

    <el-dialog v-model="showTrafficLightDialog" :title="trafficLightForm.id ? '编辑信号灯' : '新增信号灯'" width="700px">
      <el-form :model="trafficLightForm" label-width="120px">
        <el-form-item label="归属项目" required>
          <el-select v-model="trafficLightForm.project_id" placeholder="请选择项目" filterable>
            <el-option v-for="project in projectOptions" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="信号机类型">
          <el-select v-model="trafficLightForm.signal_type" placeholder="请选择信号机类型">
            <el-option label="智能" value="智能" />
            <el-option label="非智能" value="非智能" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="信号机数量">
              <el-input-number v-model="trafficLightForm.signal_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="左转箭头灯数量">
              <el-input-number v-model="trafficLightForm.left_arrow_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="直行箭头灯数量">
              <el-input-number v-model="trafficLightForm.straight_arrow_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="右转箭头灯数量">
              <el-input-number v-model="trafficLightForm.right_arrow_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="满屏灯数量">
              <el-input-number v-model="trafficLightForm.full_screen_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="非机动灯数量">
              <el-input-number v-model="trafficLightForm.non_motor_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="人行灯数量">
              <el-input-number v-model="trafficLightForm.pedestrian_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车流量雷达数量">
              <el-input-number v-model="trafficLightForm.radar_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="诱导屏数量">
              <el-input-number v-model="trafficLightForm.guide_screen_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="取电说明">
          <el-input v-model="trafficLightForm.power_source" placeholder="如：市电、太阳能" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTrafficLightDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTrafficLight">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showElectronicPoliceDialog" :title="electronicPoliceForm.id ? '编辑电子警察' : '新增电子警察'" width="700px">
      <el-form :model="electronicPoliceForm" label-width="120px">
        <el-form-item label="归属项目" required>
          <el-select v-model="electronicPoliceForm.project_id" placeholder="请选择项目" filterable>
            <el-option v-for="project in projectOptions" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="抓拍类型">
          <el-select v-model="electronicPoliceForm.capture_type" placeholder="请选择抓拍类型">
            <el-option label="普通电警" value="普通电警" />
            <el-option label="大货车抓拍电警" value="大货车抓拍电警" />
            <el-option label="不礼让行人电警" value="不礼让行人电警" />
            <el-option label="行人穿红灯电警" value="行人穿红灯电警" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="终端服务器数量">
              <el-input-number v-model="electronicPoliceForm.terminal_server_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="正向抓拍数量">
              <el-input-number v-model="electronicPoliceForm.forward_capture_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="反向抓拍数量">
              <el-input-number v-model="electronicPoliceForm.reverse_capture_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="LED灯数量">
              <el-input-number v-model="electronicPoliceForm.led_light_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="爆闪灯数量">
              <el-input-number v-model="electronicPoliceForm.strobe_light_count" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="监控球机数量">
              <el-input-number v-model="electronicPoliceForm.ptz_count" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="信号灯检测器数量">
          <el-input-number v-model="electronicPoliceForm.signal_detector_count" :min="0" />
        </el-form-item>
        <el-form-item label="取网说明">
          <el-input v-model="electronicPoliceForm.network_source" placeholder="如：光纤、无线" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showElectronicPoliceDialog = false">取消</el-button>
        <el-button type="primary" @click="submitElectronicPolice">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { intersectionApi, type IntersectionDetail } from '@/api/intersections'
import { attachmentApi, type Attachment } from '@/api/attachments'
import { projectApi } from '@/api/projects'
import { useUserStore } from '@/stores/user'
import type { TrafficLight, ElectronicPolice, Project } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const intersection = ref<IntersectionDetail['intersection'] | null>(null)
const trafficLights = ref<TrafficLight[]>([])
const electronicPolices = ref<ElectronicPolice[]>([])
const attachments = ref<Attachment[]>([])
const warrantyRecords = ref<WarrantyRecord[]>([])
const activeTab = ref('trafficLights')

const showTrafficLightDialog = ref(false)
const showElectronicPoliceDialog = ref(false)
const showWarrantyDialog = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

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

const trafficLightForm = reactive<Partial<TrafficLight>>({
  id: undefined,
  project_id: undefined,
  project_name: '',
  signal_type: '',
  signal_count: 0,
  left_arrow_count: 0,
  straight_arrow_count: 0,
  right_arrow_count: 0,
  full_screen_count: 0,
  non_motor_count: 0,
  pedestrian_count: 0,
  radar_count: 0,
  guide_screen_count: 0,
  power_source: ''
})

const electronicPoliceForm = reactive<Partial<ElectronicPolice>>({
  id: undefined,
  project_id: undefined,
  project_name: '',
  capture_type: '',
  terminal_server_count: 0,
  forward_capture_count: 0,
  reverse_capture_count: 0,
  led_light_count: 0,
  strobe_light_count: 0,
  ptz_count: 0,
  signal_detector_count: 0,
  network_source: ''
})

function getStatusType(status?: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    default: return 'info'
  }
}

function editTrafficLight(row: TrafficLight) {
  Object.assign(trafficLightForm, {
    id: row.id,
    project_id: row.project_id,
    project_name: row.project_name,
    signal_type: row.signal_type,
    signal_count: row.signal_count || 0,
    left_arrow_count: row.left_arrow_count || 0,
    straight_arrow_count: row.straight_arrow_count || 0,
    right_arrow_count: row.right_arrow_count || 0,
    full_screen_count: row.full_screen_count || 0,
    non_motor_count: row.non_motor_count || 0,
    pedestrian_count: row.pedestrian_count || 0,
    radar_count: row.radar_count || 0,
    guide_screen_count: row.guide_screen_count || 0,
    power_source: row.power_source
  })
  showTrafficLightDialog.value = true
}

async function submitTrafficLight() {
  try {
    if (trafficLightForm.id) {
      await intersectionApi.updateTrafficLight(
        Number(route.params.id),
        trafficLightForm.id,
        trafficLightForm
      )
      ElMessage.success('更新成功')
    } else {
      await intersectionApi.createTrafficLight(Number(route.params.id), trafficLightForm)
      ElMessage.success('创建成功')
    }
    showTrafficLightDialog.value = false
    resetTrafficLightForm()
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteTrafficLight(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该信号灯吗？', '警告', { type: 'warning' })
    await intersectionApi.deleteTrafficLight(Number(route.params.id), id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function resetTrafficLightForm() {
  trafficLightForm.id = undefined
  trafficLightForm.project_id = undefined
  trafficLightForm.project_name = ''
  trafficLightForm.signal_type = ''
  trafficLightForm.signal_count = 0
  trafficLightForm.left_arrow_count = 0
  trafficLightForm.straight_arrow_count = 0
  trafficLightForm.right_arrow_count = 0
  trafficLightForm.full_screen_count = 0
  trafficLightForm.non_motor_count = 0
  trafficLightForm.pedestrian_count = 0
  trafficLightForm.radar_count = 0
  trafficLightForm.guide_screen_count = 0
  trafficLightForm.power_source = ''
}

function editElectronicPolice(row: ElectronicPolice) {
  Object.assign(electronicPoliceForm, {
    id: row.id,
    project_id: row.project_id,
    project_name: row.project_name,
    capture_type: row.capture_type,
    terminal_server_count: row.terminal_server_count || 0,
    forward_capture_count: row.forward_capture_count || 0,
    reverse_capture_count: row.reverse_capture_count || 0,
    led_light_count: row.led_light_count || 0,
    strobe_light_count: row.strobe_light_count || 0,
    ptz_count: row.ptz_count || 0,
    signal_detector_count: row.signal_detector_count || 0,
    network_source: row.network_source
  })
  showElectronicPoliceDialog.value = true
}

async function submitElectronicPolice() {
  try {
    if (electronicPoliceForm.id) {
      await intersectionApi.updateElectronicPolice(
        Number(route.params.id),
        electronicPoliceForm.id,
        electronicPoliceForm
      )
      ElMessage.success('更新成功')
    } else {
      await intersectionApi.createElectronicPolice(Number(route.params.id), electronicPoliceForm)
      ElMessage.success('创建成功')
    }
    showElectronicPoliceDialog.value = false
    resetElectronicPoliceForm()
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteElectronicPolice(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该电子警察吗？', '警告', { type: 'warning' })
    await intersectionApi.deleteElectronicPolice(Number(route.params.id), id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function resetElectronicPoliceForm() {
  electronicPoliceForm.id = undefined
  electronicPoliceForm.project_id = undefined
  electronicPoliceForm.project_name = ''
  electronicPoliceForm.capture_type = ''
  electronicPoliceForm.terminal_server_count = 0
  electronicPoliceForm.forward_capture_count = 0
  electronicPoliceForm.reverse_capture_count = 0
  electronicPoliceForm.led_light_count = 0
  electronicPoliceForm.strobe_light_count = 0
  electronicPoliceForm.ptz_count = 0
  electronicPoliceForm.signal_detector_count = 0
  electronicPoliceForm.network_source = ''
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    try {
      await attachmentApi.upload(file, 'intersection', Number(route.params.id))
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
    const res = await attachmentApi.list('intersection', Number(route.params.id))
    attachments.value = res as unknown as Attachment[]
  } catch (error) {
    console.error('获取附件失败', error)
  }
}

async function fetchWarrantyRecords() {
  try {
    const projectApi = await import('@/api/projects')
    const records = await projectApi.projectApi.getByFacility('intersection', Number(route.params.id)) as unknown as Project[]
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
    await intersectionApi.extendWarranty(
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
    const data = await intersectionApi.getById(Number(route.params.id)) as unknown as IntersectionDetail
    intersection.value = data.intersection
    trafficLights.value = data.traffic_lights
    electronicPolices.value = data.electronic_polices
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