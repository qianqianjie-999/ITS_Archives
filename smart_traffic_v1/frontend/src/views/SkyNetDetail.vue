<template>
  <div class="sky-net-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>结构化相机点位详情 - {{ point?.name }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="point">
        <el-descriptions-item label="点位名称">{{ point.name }}</el-descriptions-item>
        <el-descriptions-item label="监控区域">{{ point.monitor_area || '-' }}</el-descriptions-item>
        <el-descriptions-item label="安装位置">{{ point.location || '-' }}</el-descriptions-item>
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
            <span>结构化相机</span>
            <el-button v-if="userStore.isEditor" type="primary" @click="showAddDialog = true">添加详情信息</el-button>
          </div>
        </template>
      <el-table :data="pagedSkyNets" stripe v-loading="loading">
        <el-table-column label="序号" width="60">
          <template #default="{ $index }">
            {{ (currentPage - 1) * perPage + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="归属项目" />
        <el-table-column prop="acceptance_date" label="项目验收日期" width="140" />
        <el-table-column prop="warranty_period" label="项目质保期" width="120">
          <template #default="{ row }">
            {{ row.warranty_period ? `${row.warranty_period}年` : '-' }}
          </template>
        </el-table-column>
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
        <el-table-column prop="camera_count" label="相机数量" width="100" />
        <el-table-column prop="bracket_count" label="支架数量" width="100" />
        <el-table-column prop="pole_count" label="立杆数量" width="100" />
        <el-table-column prop="box_count" label="挂箱数量" width="100" />
        <el-table-column prop="fill_light_count" label="补光灯数量" width="100" />
        <el-table-column prop="speaker_count" label="音箱数量" width="100" />
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
      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="perPage"
          :total="skyNets.length"
          layout="total, prev, pager, next"
          class="dark-pagination"
        />
      </div>
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
            <el-tag :type="getStatusType(row.warranty_expire_date ? (new Date(row.warranty_expire_date) >= new Date() ? '在保' : '过保') : '无项目')">
              {{ row.warranty_expire_date ? (new Date(row.warranty_expire_date) >= new Date() ? '在保' : '过保') : '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="userStore.isAdmin" label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteWarrantyExtension(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="maintenance-section" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>维修记录</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showMaintenanceDialog = true">添加维修记录</el-button>
        </div>
      </template>
      <el-table :data="maintenanceRecords" stripe>
        <el-table-column label="序号" width="60">
          <template #default="{ $index }">
            {{ $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="fault_level_text" label="故障等级" width="100">
          <template #default="{ row }">
            <el-tag :type="getFaultLevelType(row.fault_level)">
              {{ row.fault_level_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fault_description" label="故障现象" />
        <el-table-column prop="fault_time" label="故障发现时间" width="180" />
        <el-table-column prop="solution" label="解决办法" />
        <el-table-column prop="record_time" label="记录时间" width="180" />
        <el-table-column prop="recorder_name" label="记录人" width="120" />
        <el-table-column v-if="userStore.isAdmin" label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteMaintenanceRecord(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="attachment-section" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>附件列表</span>
          <span v-if="userStore.isEditor" class="upload-tip">（仅支持 PDF、JPG、JPEG、PNG、GIF、BMP、WEBP 格式，最大16MB）</span>
          <el-button v-if="userStore.isEditor" type="primary" size="small" @click="triggerFileInput()">上传附件</el-button>
        </div>
      </template>
      <input
        ref="fileInputRef"
        type="file"
        style="display: none"
        @change="handleFileUpload"
        accept=".pdf,.jpg,.jpeg,.png"
      />
      <el-table :data="attachments" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="original_filename" label="文件名" />
        <el-table-column prop="file_size" label="大小" width="100">
          <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="150" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="previewAttachment(row)">预览</el-button>
            <el-button type="success" size="small" @click="downloadAttachment(row.id)">下载</el-button>
            <el-button v-if="userStore.isEditor" type="danger" size="small" @click="deleteAttachment(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="previewVisible" title="附件预览" width="800px" append-to-body>
      <div v-if="previewType === 'image'" class="preview-image-container">
        <img :src="previewUrl" :alt="previewFilename" class="preview-image" />
      </div>
      <div v-else-if="previewType === 'pdf'" class="preview-pdf-container">
        <iframe :src="previewUrl" class="preview-pdf" frameborder="0"></iframe>
      </div>
      <div v-else class="preview-unsupported">
        <el-icon size="64" class="preview-icon">
          <Files />
        </el-icon>
        <p>该文件类型不支持预览，请下载查看</p>
      </div>
    </el-dialog>

    <el-dialog v-model="showExtendWarrantyDialog" title="申请质保延期" width="500px">
      <el-form :model="extendWarrantyForm" label-width="100px">
        <el-form-item label="归属项目" required>
          <el-select v-model="extendWarrantyForm.project_id" placeholder="请选择项目" filterable style="width: 100%" @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="新质保到期" required>
          <el-date-picker v-model="extendWarrantyForm.warranty_expire_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExtendWarrantyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitExtendWarranty">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showMaintenanceDialog" title="添加维修记录" width="500px">
      <el-form :model="maintenanceForm" label-width="100px">
        <el-form-item label="故障等级" required>
          <el-radio-group v-model="maintenanceForm.fault_level">
            <el-radio label="high">高</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="故障现象" required>
          <el-input v-model="maintenanceForm.fault_description" type="textarea" :rows="4" placeholder="请描述故障现象" />
        </el-form-item>
        <el-form-item label="故障发现时间">
          <el-date-picker v-model="maintenanceForm.fault_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择故障发现时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="解决办法">
          <el-input v-model="maintenanceForm.solution" type="textarea" :rows="4" placeholder="请描述解决办法" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMaintenanceDialog = false">取消</el-button>
        <el-button type="primary" @click="submitMaintenance">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddDialog" :title="editForm.id ? '编辑详情信息' : '添加详情信息'" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="归属项目" required>
          <el-select v-model="editForm.project_id" placeholder="请选择项目">
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="相机数量">
          <el-input-number v-model="editForm.camera_count" :min="0" />
        </el-form-item>
        <el-form-item label="支架数量">
          <el-input-number v-model="editForm.bracket_count" :min="0" />
        </el-form-item>
        <el-form-item label="立杆数量">
          <el-input-number v-model="editForm.pole_count" :min="0" />
        </el-form-item>
        <el-form-item label="挂箱数量">
          <el-input-number v-model="editForm.box_count" :min="0" />
        </el-form-item>
        <el-form-item label="补光灯数量">
          <el-input-number v-model="editForm.fill_light_count" :min="0" />
        </el-form-item>
        <el-form-item label="音箱数量">
          <el-input-number v-model="editForm.speaker_count" :min="0" />
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Files } from '@element-plus/icons-vue'
import { skyNetApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import { maintenanceApi } from '@/api/maintenance'
import { attachmentApi, type Attachment } from '@/api/attachments'
import { useUserStore } from '@/stores/user'
import type { SkyNetPoint, SkyNet, Project, WarrantyExtension } from '@/types'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const point = ref<SkyNetPoint | null>(null)
const skyNets = ref<SkyNet[]>([])
const projects = ref<Project[]>([])
const warrantyExtensions = ref<WarrantyExtension[]>([])
const maintenanceRecords = ref<MaintenanceRecord[]>([])
const attachments = ref<Attachment[]>([])
const loading = ref(false)
const currentPage = ref(1)
const perPage = ref(20)
const showAddDialog = ref(false)
const showExtendWarrantyDialog = ref(false)
const showMaintenanceDialog = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const previewVisible = ref(false)
const previewUrl = ref('')
const previewType = ref<'image' | 'pdf' | 'other'>('other')
const previewFilename = ref('')

interface MaintenanceRecord {
  id: number
  facility_type: string
  facility_id: number
  fault_level: string
  fault_level_text: string
  fault_description: string
  fault_time: string
  solution: string
  record_time: string
  recorder_id: number
  recorder_name: string
}

const pagedSkyNets = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return skyNets.value.slice(start, start + perPage.value)
})

const extendWarrantyForm = reactive({
  project_id: undefined as number | undefined,
  warranty_expire_date: ''
})

const maintenanceForm = reactive({
  fault_level: 'medium',
  fault_description: '',
  fault_time: '',
  solution: ''
})

function onProjectChange(projectId: number) {
  const project = projects.value.find(p => p.id === projectId)
  if (project && project.warranty_expire_date) {
    extendWarrantyForm.warranty_expire_date = project.warranty_expire_date
  }
}

const editForm = reactive<Partial<SkyNet>>({
  id: undefined,
  camera_area: '',
  camera_count: 0,
  bracket_count: 0,
  pole_count: 0,
  box_count: 0,
  fill_light_count: 0,
  speaker_count: 0,
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

function getFaultLevelType(level?: string) {
  switch (level) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

function goBack() {
  router.push('/sky-net')
}

function editDevice(device: SkyNet) {
  editForm.id = device.id
  editForm.camera_area = device.camera_area || ''
  editForm.camera_count = device.camera_count || 0
  editForm.bracket_count = device.bracket_count || 0
  editForm.pole_count = device.pole_count || 0
  editForm.box_count = device.box_count || 0
  editForm.fill_light_count = device.fill_light_count || 0
  editForm.speaker_count = device.speaker_count || 0
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
    bracket_count: editForm.bracket_count || 0,
    pole_count: editForm.pole_count || 0,
    box_count: editForm.box_count || 0,
    fill_light_count: editForm.fill_light_count || 0,
    speaker_count: editForm.speaker_count || 0,
    power_source: editForm.power_source || '',
    network_source: editForm.network_source || '',
    project_id: editForm.project_id
  }

  const pointId = Number(route.params.id)
  
  if (editForm.id) {
    skyNetApi.updateSkyNet(pointId, editForm.id, data).then(() => {
      ElMessage.success('编辑成功')
      showAddDialog.value = false
      loadData()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '编辑失败')
    })
  } else {
    skyNetApi.createSkyNet(pointId, data).then(() => {
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
    skyNetApi.deleteSkyNet(pointId, id).then(() => {
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
    skyNetApi.getPoint(pointId),
    projectApi.list({ per_page: 0 })
  ]).then(([pointDetail, projectList]) => {
    point.value = pointDetail.data.point
    skyNets.value = pointDetail.data.sky_nets || []
    warrantyExtensions.value = pointDetail.data.warranty_extensions || []
    projects.value = projectList.data
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

function submitExtendWarranty() {
  if (!extendWarrantyForm.project_id) {
    ElMessage.error('请选择项目')
    return
  }
  if (!extendWarrantyForm.warranty_expire_date) {
    ElMessage.error('请选择新质保到期日期')
    return
  }
  const pointId = Number(route.params.id)
  skyNetApi.extendWarranty(pointId, {
    project_id: extendWarrantyForm.project_id,
    warranty_expire_date: extendWarrantyForm.warranty_expire_date
  }).then(() => {
    ElMessage.success('质保延期成功')
    showExtendWarrantyDialog.value = false
    extendWarrantyForm.project_id = undefined
    extendWarrantyForm.warranty_expire_date = ''
    loadData()
  }).catch((err) => {
    ElMessage.error(err.response?.data?.message || '质保延期失败')
  })
}

function deleteWarrantyExtension(id: number) {
  ElMessageBox.confirm('确定要删除该质保延期记录吗？删除后设备的质保状态将恢复到延期前的状态。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    projectApi.deleteWarrantyExtension(id).then(() => {
      ElMessage.success('删除成功')
      loadData()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '删除失败')
    })
  }).catch(() => {})
}

async function fetchMaintenanceRecords() {
  try {
    const res = await maintenanceApi.getMaintenanceRecords('sky_net', Number(route.params.id))
    maintenanceRecords.value = res.data
  } catch (error) {
    console.error('获取维修记录失败', error)
  }
}

async function submitMaintenance() {
  try {
    if (!maintenanceForm.fault_description) {
      ElMessage.warning('请填写故障现象')
      return
    }
    await maintenanceApi.createMaintenanceRecord({
      facility_type: 'sky_net',
      facility_id: Number(route.params.id),
      fault_level: maintenanceForm.fault_level,
      fault_description: maintenanceForm.fault_description,
      fault_time: maintenanceForm.fault_time || null,
      solution: maintenanceForm.solution
    })
    ElMessage.success('添加成功')
    showMaintenanceDialog.value = false
    maintenanceForm.fault_level = 'medium'
    maintenanceForm.fault_description = ''
    maintenanceForm.fault_time = ''
    maintenanceForm.solution = ''
    await fetchMaintenanceRecords()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

async function deleteMaintenanceRecord(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该维修记录吗？', '警告', { type: 'warning' })
    await maintenanceApi.deleteMaintenanceRecord(id)
    ElMessage.success('删除成功')
    await fetchMaintenanceRecords()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '删除失败')
    }
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    await attachmentApi.upload(file, 'sky_net', Number(route.params.id))
    ElMessage.success('上传成功')
    await fetchAttachments()
    target.value = ''
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

async function fetchAttachments() {
  try {
    const res = await attachmentApi.list('sky_net', Number(route.params.id))
    attachments.value = res.data
  } catch (error) {
    console.error('获取附件失败', error)
  }
}

async function deleteAttachment(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该附件吗？', '警告', { type: 'warning' })
    await attachmentApi.delete(id)
    ElMessage.success('删除成功')
    await fetchAttachments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '删除失败')
    }
  }
}

async function downloadAttachment(id: number) {
  try {
    const response = await attachmentApi.download(id) as unknown as Blob
    const url = window.URL.createObjectURL(response)
    const a = document.createElement('a')
    a.href = url
    a.download = `attachment_${id}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

async function previewAttachment(attachment: Attachment) {
  const filename = attachment.original_filename.toLowerCase()
  previewFilename.value = attachment.original_filename

  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
  const isImage = imageExtensions.some(ext => filename.endsWith(ext))

  if (isImage) {
    previewType.value = 'image'
    try {
      const response = await attachmentApi.download(attachment.id) as unknown as Blob
      previewUrl.value = window.URL.createObjectURL(response)
    } catch (error) {
      ElMessage.error('预览失败')
      return
    }
  } else if (filename.endsWith('.pdf')) {
    previewType.value = 'pdf'
    previewUrl.value = `${import.meta.env.VITE_API_BASE_URL || '/api'}/attachments/${attachment.id}?preview=true`
  } else {
    previewType.value = 'other'
  }
  previewVisible.value = true
}

onMounted(() => {
  loadData()
  fetchMaintenanceRecords()
  fetchAttachments()
})
</script>
