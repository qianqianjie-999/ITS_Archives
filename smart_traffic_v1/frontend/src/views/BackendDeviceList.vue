<template>
  <div class="backend-device-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>后端设备列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="openDialog()">新增后端设备</el-button>
        </div>
      </template>

      <div class="filter-bar">
        <el-row :gutter="12">
          <el-col :span="10">
            <el-select v-model="filterWarranty" placeholder="质保状态" clearable>
              <el-option label="全部" value="" />
              <el-option label="在保" value="在保" />
              <el-option label="过保" value="过保" />
              <el-option label="无项目" value="无项目" />
            </el-select>
          </el-col>
          <el-col :span="14">
            <el-input v-model="searchKeyword" placeholder="搜索设备名称、设备类型..." clearable>
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-col>
        </el-row>
      </div>

      <el-table :data="pagedBackendDevices" stripe v-loading="loading" @row-click="selectDevice">
        <el-table-column label="序号" width="60">
          <template #default="{ $index }">
            {{ (currentPage - 1) * perPage + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="model" label="品牌型号" width="140" />
        <el-table-column prop="type" label="设备类型" width="140" />
        <el-table-column prop="quantity" label="设备数量" width="90" align="center" />
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
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click.stop="openDialog(row)">编辑</el-button>
            <el-button v-if="userStore.isEditor" type="danger" size="small" @click.stop="deleteBackendDevice(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="perPage"
          :total="filteredBackendDevices.length"
          layout="total, prev, pager, next"
          class="dark-pagination"
        />
      </div>
    </el-card>

    <el-card class="warranty-section" style="margin-top: 16px" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>质保延期记录 - {{ selectedDevice.name }}</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showWarrantyDialog = true">申请质保延期</el-button>
        </div>
      </template>
      <el-table :data="warrantyRecords" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="project_name" label="归属项目" />
        <el-table-column prop="acceptance_date" label="验收日期" width="140" />
        <el-table-column prop="warranty_expire_date" label="质保到期时间" width="160" />
        <el-table-column prop="warranty_status" label="质保状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.warranty_status)">
              {{ row.warranty_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="userStore.isAdmin" label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteBackendDevice(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="maintenance-section" style="margin-top: 16px" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>维修记录 - {{ selectedDevice.name }}</span>
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

    <el-card class="attachment-section" style="margin-top: 16px" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>附件列表 - {{ selectedDevice.name }}</span>
          <span v-if="userStore.isEditor" class="upload-tip">（仅支持 PDF、JPG、JPEG、PNG 格式）</span>
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

    <el-dialog v-model="showWarrantyDialog" title="申请质保延期" width="500px">
      <el-form :model="warrantyForm" label-width="100px">
        <el-form-item label="设备名称">
          <span>{{ selectedDevice?.name }}</span>
        </el-form-item>
        <el-form-item label="归属项目" required>
          <el-select v-model="warrantyForm.project_id" placeholder="请选择项目" filterable style="width: 100%" @change="onProjectChange">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="新质保到期" required>
          <el-date-picker v-model="warrantyForm.warranty_expire_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showWarrantyDialog = false">取消</el-button>
        <el-button type="primary" @click="submitWarranty">确定</el-button>
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

    <el-dialog v-model="showDialog" :title="editForm.id ? '编辑后端设备' : '新增后端设备'" width="600px">
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="设备名称" required>
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="设备品牌型号" required>
          <el-input v-model="editForm.model" placeholder="请输入品牌型号" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="editForm.type" placeholder="请选择设备类型" style="width: 100%">
            <el-option v-for="t in deviceTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备数量">
          <el-input-number v-model="editForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="归属项目">
          <el-select v-model="editForm.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitBackendDevice">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Files, Search } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { backendDeviceApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import { maintenanceApi } from '@/api/maintenance'
import { attachmentApi, type Attachment } from '@/api/attachments'
import type { BackendDevice, Project } from '@/types'

const userStore = useUserStore()
const loading = ref(false)
const backendDevices = ref<BackendDevice[]>([])
const projects = ref<Project[]>([])
const attachments = ref<Attachment[]>([])
const showDialog = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const previewVisible = ref(false)
const previewUrl = ref('')
const previewType = ref<'image' | 'pdf' | 'other'>('other')
const previewFilename = ref('')
const showWarrantyDialog = ref(false)
const showMaintenanceDialog = ref(false)
const selectedDevice = ref<BackendDevice | null>(null)
const warrantyRecords = ref<any[]>([])
const maintenanceRecords = ref<MaintenanceRecord[]>([])
const currentPage = ref(1)
const perPage = ref(20)
const searchKeyword = ref('')
const filterWarranty = ref('')

const filteredBackendDevices = computed(() => {
  return backendDevices.value.filter(d => {
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      const haystack = [d.name, d.type, d.project_name].filter(Boolean).join(' ').toLowerCase()
      if (!haystack.includes(kw)) return false
    }
    if (filterWarranty.value) {
      if ((d as any).warranty_status !== filterWarranty.value) return false
    }
    return true
  })
})

const pagedBackendDevices = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredBackendDevices.value.slice(start, start + perPage.value)
})

watch([searchKeyword, filterWarranty], () => {
  currentPage.value = 1
})

interface MaintenanceRecord {
  id: number
  facility_type: string
  facility_id: number
  fault_level: string
  fault_level_text: string
  fault_description: string
  solution: string
  record_time: string
  recorder_id: number
  recorder_name: string
}

const warrantyForm = ref<any>({
  project_id: undefined as number | undefined,
  warranty_expire_date: ''
})

const maintenanceForm = ref<any>({
  fault_level: 'medium',
  fault_description: '',
  solution: ''
})

const deviceTypes = [
  '网络交换设备',
  '网络安全设备',
  '服务器',
  '存储设备',
  '显示设备',
  '操作设备',
  '消防设备',
  '用电设备',
  '空调设备',
  '软件平台'
]

const editForm = ref<any>({
  id: undefined,
  project_id: undefined,
  name: '',
  model: '',
  type: '',
  quantity: 1
})

async function fetchData() {
  loading.value = true
  try {
    const res = await backendDeviceApi.list({ per_page: 0 })
    backendDevices.value = res.data
  } catch (error) {
    ElMessage.error('获取后端设备列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchProjects() {
  try {
    projects.value = (await projectApi.list({ per_page: 0 })).data
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

async function fetchWarrantyRecords(deviceId: number) {
  try {
    warrantyRecords.value = (await backendDeviceApi.getHistory(deviceId)).data
  } catch (error) {
    warrantyRecords.value = []
  }
}

function selectDevice(row: BackendDevice) {
  selectedDevice.value = row
  fetchWarrantyRecords(row.id)
  fetchMaintenanceRecords(row.id)
  fetchAttachments(row.id)
}

function openDialog(row?: BackendDevice) {
  if (row) {
    editForm.value = {
      id: row.id,
      project_id: row.project_id,
      name: row.name,
      model: row.model || '',
      type: row.type,
      quantity: (row as any).quantity || 1
    }
  } else {
    editForm.value = {
      id: undefined,
      project_id: undefined,
      name: '',
      model: '',
      type: '',
      quantity: 1
    }
  }
  showDialog.value = true
}

function onProjectChange(projectId: number) {
  const project = projects.value.find(p => p.id === projectId)
  if (project && project.warranty_expire_date) {
    warrantyForm.value.warranty_expire_date = project.warranty_expire_date
  }
}

async function submitWarranty() {
  if (!warrantyForm.value.project_id) {
    ElMessage.error('请选择项目')
    return
  }
  if (!warrantyForm.value.warranty_expire_date) {
    ElMessage.error('请选择新质保到期日期')
    return
  }
  try {
    await backendDeviceApi.extendWarranty(selectedDevice.value!.id, {
      project_id: warrantyForm.value.project_id,
      warranty_expire_date: warrantyForm.value.warranty_expire_date
    })
    ElMessage.success('质保延期成功')
    showWarrantyDialog.value = false
    warrantyForm.value.project_id = undefined
    warrantyForm.value.warranty_expire_date = ''
    fetchData()
    fetchWarrantyRecords(selectedDevice.value!.id)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '质保延期失败')
  }
}

async function submitBackendDevice() {
  try {
    if (!editForm.value.name) {
      ElMessage.warning('请填写设备名称')
      return
    }
    if (!editForm.value.model) {
      ElMessage.warning('请填写设备品牌型号')
      return
    }
    const data = {
      name: editForm.value.name,
      model: editForm.value.model,
      type: editForm.value.type,
      quantity: editForm.value.quantity,
      project_id: editForm.value.project_id
    }

    if (editForm.value.id) {
      await backendDeviceApi.update(editForm.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await backendDeviceApi.create(data)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    fetchData()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '操作失败')
  }
}

async function deleteBackendDevice(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条后端设备记录吗?', '提示', {
      type: 'warning'
    })
    await backendDeviceApi.delete(id)
    ElMessage.success('删除成功')
    if (selectedDevice.value?.id === id) {
      selectedDevice.value = null
      warrantyRecords.value = []
      maintenanceRecords.value = []
    }
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '删除失败')
    }
  }
}

async function fetchMaintenanceRecords(deviceId: number) {
  try {
    const res = await maintenanceApi.getMaintenanceRecords('backend_device', deviceId)
    maintenanceRecords.value = res.data
  } catch (error) {
    console.error('获取维修记录失败', error)
    maintenanceRecords.value = []
  }
}

async function submitMaintenance() {
  try {
    if (!maintenanceForm.value.fault_description) {
      ElMessage.warning('请填写故障现象')
      return
    }
    await maintenanceApi.createMaintenanceRecord({
      facility_type: 'backend_device',
      facility_id: selectedDevice.value!.id,
      fault_level: maintenanceForm.value.fault_level,
      fault_description: maintenanceForm.value.fault_description,
      solution: maintenanceForm.value.solution
    })
    ElMessage.success('添加成功')
    showMaintenanceDialog.value = false
    maintenanceForm.value.fault_level = 'medium'
    maintenanceForm.value.fault_description = ''
    maintenanceForm.value.solution = ''
    await fetchMaintenanceRecords(selectedDevice.value!.id)
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

async function deleteMaintenanceRecord(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该维修记录吗？', '警告', { type: 'warning' })
    await maintenanceApi.deleteMaintenanceRecord(id)
    ElMessage.success('删除成功')
    await fetchMaintenanceRecords(selectedDevice.value!.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '删除失败')
    }
  }
}

function getStatusType(status?: string) {
  if (status === '在保') return 'success'
  if (status === '过保') return 'danger'
  if (status === '无项目') return 'warning'
  if (status && new Date(status) >= new Date()) return 'success'
  if (status && new Date(status) < new Date()) return 'danger'
  return 'info'
}

function getFaultLevelType(level?: string) {
  switch (level) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
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
  if (!file || !selectedDevice.value) return

  try {
    await attachmentApi.upload(file, 'backend_device', selectedDevice.value.id)
    ElMessage.success('上传成功')
    await fetchAttachments(selectedDevice.value.id)
    target.value = ''
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

async function fetchAttachments(deviceId: number) {
  try {
    const res = await attachmentApi.list('backend_device', deviceId)
    attachments.value = res.data
  } catch (error) {
    console.error('获取附件失败', error)
    attachments.value = []
  }
}

async function deleteAttachment(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该附件吗？', '警告', { type: 'warning' })
    await attachmentApi.delete(id)
    ElMessage.success('删除成功')
    if (selectedDevice.value) {
      await fetchAttachments(selectedDevice.value.id)
    }
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
  fetchData()
  fetchProjects()
})
</script>

<style scoped lang="scss">
.backend-device-list {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .filter-bar {
    margin-bottom: 16px;
  }
}
</style>
