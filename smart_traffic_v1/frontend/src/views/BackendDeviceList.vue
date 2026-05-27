<template>
  <div class="backend-device-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>后端设备列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="openDialog()">新增后端设备</el-button>
        </div>
      </template>
      <el-table :data="backendDevices" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="设备名称" />
        <el-table-column prop="type" label="设备类型" width="140" />
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
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-button v-if="userStore.isEditor" type="danger" size="small" @click="deleteBackendDevice(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editForm.id ? '编辑后端设备' : '新增后端设备'" width="600px">
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="设备名称" required>
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="editForm.type" placeholder="请选择设备类型" style="width: 100%">
            <el-option v-for="t in deviceTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="归属项目">
          <el-select v-model="editForm.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="建设单位">
          <el-input v-model="editForm.construction_unit" />
        </el-form-item>
        <el-form-item label="施工单位">
          <el-input v-model="editForm.construction_company" />
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { pointApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import type { BackendDevice, Project } from '@/types'

const userStore = useUserStore()
const loading = ref(false)
const backendDevices = ref<BackendDevice[]>([])
const projects = ref<Project[]>([])
const showDialog = ref(false)

const deviceTypes = [
  '网络交换设备',
  '网络安全设备',
  '服务器',
  '存储设备',
  '显示设备',
  '操作设备',
  '消防设备',
  '用电设备',
  '空调设备'
]

const editForm = ref<any>({
  id: undefined,
  project_id: undefined,
  name: '',
  type: '',
  construction_unit: '',
  construction_company: ''
})

async function fetchData() {
  loading.value = true
  try {
    backendDevices.value = await pointApi.listBackendDevices() as unknown as BackendDevice[]
  } catch (error) {
    ElMessage.error('获取后端设备列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchProjects() {
  try {
    projects.value = await projectApi.list() as unknown as Project[]
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

function openDialog(row?: BackendDevice) {
  if (row) {
    editForm.value = {
      id: row.id,
      project_id: row.project_id,
      name: row.name,
      type: row.type,
      construction_unit: row.construction_unit,
      construction_company: row.construction_company
    }
  } else {
    editForm.value = {
      id: undefined,
      project_id: undefined,
      name: '',
      type: '',
      construction_unit: '',
      construction_company: ''
    }
  }
  showDialog.value = true
}

async function submitBackendDevice() {
  try {
    if (!editForm.value.name) {
      ElMessage.warning('请填写设备名称')
      return
    }
    const data = {
      name: editForm.value.name,
      type: editForm.value.type,
      construction_unit: editForm.value.construction_unit,
      construction_company: editForm.value.construction_company,
      project_id: editForm.value.project_id
    }
    
    if (editForm.value.id) {
      await pointApi.updateBackendDevice(0, editForm.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await pointApi.createBackendDevice(0, data)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteBackendDevice(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条后端设备记录吗?', '提示', {
      type: 'warning'
    })
    await pointApi.deleteBackendDevice(0, id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getStatusType(status?: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    case '无项目': return 'warning'
    default: return 'info'
  }
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
}
</style>
