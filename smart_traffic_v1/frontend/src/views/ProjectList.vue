<template>
  <div class="project-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showDialog = true">新增项目</el-button>
        </div>
      </template>
      <el-table :data="projects" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="contract_amount" label="合同金额" width="120">
          <template #default="{ row }">
            {{ row.contract_amount ? `¥${row.contract_amount.toLocaleString()}` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="acceptance_date" label="验收日期" width="120" />
        <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
        <el-table-column prop="builder" label="建设单位" />
        <el-table-column prop="constructor" label="施工单位" />
        <el-table-column v-if="userStore.isEditor" label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editProject(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteProject(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="editProjectForm.id ? '编辑项目' : '新增项目'" width="500px">
      <el-form :model="editProjectForm" label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="editProjectForm.name" />
        </el-form-item>
        <el-form-item label="合同金额">
          <el-input-number v-model="editProjectForm.contract_amount" :precision="2" :step="1000" />
        </el-form-item>
        <el-form-item label="验收日期">
          <el-date-picker v-model="editProjectForm.acceptance_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="质保期">
          <el-input v-model="editProjectForm.warranty_period" />
        </el-form-item>
        <el-form-item label="质保到期" required>
          <el-date-picker v-model="editProjectForm.warranty_expire_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="建设单位">
          <el-input v-model="editProjectForm.builder" />
        </el-form-item>
        <el-form-item label="施工单位">
          <el-input v-model="editProjectForm.constructor" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitProject">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { projectApi } from '@/api/projects'
import { useUserStore } from '@/stores/user'
import type { Project } from '@/types'

const userStore = useUserStore()
const projects = ref<Project[]>([])
const loading = ref(false)
const showDialog = ref(false)

const editProjectForm = reactive<Partial<Project>>({
  id: undefined,
  name: '',
  contract_amount: undefined,
  acceptance_date: '',
  warranty_period: '',
  warranty_expire_date: '',
  builder: '',
  constructor: ''
})

function editProject(project: Project) {
  Object.assign(editProjectForm, project)
  showDialog.value = true
}

async function submitProject() {
  try {
    if (editProjectForm.id) {
      await projectApi.update(editProjectForm.id, editProjectForm)
      ElMessage.success('更新成功')
    } else {
      await projectApi.create(editProjectForm)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function deleteProject(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该项目吗？', '警告', { type: 'warning' })
    await projectApi.delete(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await projectApi.list()
    projects.value = res as unknown as Project[]
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