<template>
  <div class="project-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="openAddDialog">新增项目</el-button>
        </div>
      </template>

      <div class="filter-bar">
        <el-row :gutter="12">
          <el-col :span="10">
            <el-select v-model="filterWarranty" placeholder="质保状态" clearable>
              <el-option label="全部" value="" />
              <el-option label="在保" value="在保" />
              <el-option label="过保" value="过保" />
            </el-select>
          </el-col>
          <el-col :span="14">
            <el-input v-model="searchKeyword" placeholder="搜索项目名称、建设单位..." clearable>
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-col>
        </el-row>
      </div>

      <el-table :data="pagedProjects" stripe v-loading="loading">
        <el-table-column label="序号" width="60">
          <template #default="{ $index }">
            {{ (currentPage - 1) * perPage + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="contract_amount" label="合同金额(万元)" width="140">
          <template #default="{ row }">
            {{ row.contract_amount ? `¥${row.contract_amount.toLocaleString()}万元` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="acceptance_date" label="验收日期" width="120" />
        <el-table-column prop="warranty_period" label="质保期" width="120">
          <template #default="{ row }">
            {{ row.warranty_period ? `${row.warranty_period}年` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
        <el-table-column label="质保状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.warranty_expire_date && new Date(row.warranty_expire_date) >= new Date() ? 'success' : 'danger'">
              {{ row.warranty_expire_date ? (new Date(row.warranty_expire_date) >= new Date() ? '在保' : '过保') : '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="builder" label="建设单位" />
        <el-table-column prop="construction_unit" label="施工单位" />
        <el-table-column label="关联项目" width="80" align="center">
          <template #default="{ row }">
            <span :class="row.is_referenced ? 'status-dot green' : 'status-dot gray'" :title="row.is_referenced ? '已被引用' : '未被引用'" />
          </template>
        </el-table-column>
        <el-table-column v-if="userStore.isEditor" label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="editProject(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteProject(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="perPage"
          :total="filteredProjects.length"
          layout="total, prev, pager, next"
          class="dark-pagination"
        />
      </div>
    </el-card>

    <el-dialog v-model="showDialog" :title="editProjectForm.id ? '编辑项目' : '新增项目'" width="500px">
      <el-form :model="editProjectForm" label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="editProjectForm.name" />
        </el-form-item>
        <el-form-item label="合同金额">
          <div style="display: flex; align-items: center;">
            <el-input-number v-model="editProjectForm.contract_amount" :precision="2" :step="1000" style="width: 180px;" />
            <span style="margin-left: 8px;">万元</span>
          </div>
        </el-form-item>
        <el-form-item label="验收日期">
          <el-date-picker v-model="editProjectForm.acceptance_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="质保期">
          <div style="display: flex; align-items: center;">
            <el-input v-model="editProjectForm.warranty_period" style="width: 180px;" />
            <span style="margin-left: 8px;">年</span>
          </div>
        </el-form-item>
        <el-form-item label="质保到期" required>
          <el-date-picker v-model="editProjectForm.warranty_expire_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="建设单位">
          <el-input v-model="editProjectForm.builder" />
        </el-form-item>
        <el-form-item label="施工单位">
          <el-input v-model="editProjectForm.construction_unit" />
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
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { projectApi } from '@/api/projects'
import { useUserStore } from '@/stores/user'
import type { Project } from '@/types'
import { eventBus } from '@/utils/eventBus'

const userStore = useUserStore()
const allProjects = ref<Project[]>([])
const loading = ref(false)
const showDialog = ref(false)
const currentPage = ref(1)
const perPage = ref(15)
const searchKeyword = ref('')
const filterWarranty = ref('')

const filteredProjects = computed(() => {
  return allProjects.value.filter(p => {
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      const haystack = [p.name, p.builder, p.construction_unit].filter(Boolean).join(' ').toLowerCase()
      if (!haystack.includes(kw)) return false
    }
    if (filterWarranty.value) {
      const isExpired = p.warranty_expire_date && new Date(p.warranty_expire_date) < new Date()
      if (filterWarranty.value === '在保' && isExpired) return false
      if (filterWarranty.value === '过保' && !isExpired) return false
    }
    return true
  })
})

const pagedProjects = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredProjects.value.slice(start, start + perPage.value)
})

watch([searchKeyword, filterWarranty], () => {
  currentPage.value = 1
})

const editProjectForm = reactive<Partial<Project>>({
  id: undefined,
  name: '',
  contract_amount: undefined,
  acceptance_date: '',
  warranty_period: '',
  warranty_expire_date: '',
  builder: '',
  construction_unit: ''
})

function openAddDialog() {
  editProjectForm.id = undefined
  editProjectForm.name = ''
  editProjectForm.contract_amount = undefined
  editProjectForm.acceptance_date = ''
  editProjectForm.warranty_period = ''
  editProjectForm.warranty_expire_date = ''
  editProjectForm.builder = ''
  editProjectForm.construction_unit = ''
  showDialog.value = true
}

function editProject(project: Project) {
  Object.assign(editProjectForm, {
    id: project.id,
    name: project.name,
    contract_amount: project.contract_amount,
    acceptance_date: project.acceptance_date,
    warranty_period: project.warranty_period,
    warranty_expire_date: project.warranty_expire_date,
    builder: project.builder,
    construction_unit: project.construction_unit
  })
  showDialog.value = true
}

async function submitProject() {
  try {
    const data = { ...editProjectForm }
    if (editProjectForm.id) {
      await projectApi.update(editProjectForm.id, data)
      ElMessage.success('更新成功')
      eventBus.emit('dataUpdated', 'project', 'update', editProjectForm.id)
    } else {
      await projectApi.create(data)
      ElMessage.success('创建成功')
      eventBus.emit('dataUpdated', 'project', 'create')
    }
    showDialog.value = false
    fetchData()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '操作失败')
  }
}

async function deleteProject(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该项目吗？', '警告', { type: 'warning' })
    await projectApi.delete(id)
    ElMessage.success('删除成功')
    fetchData()
    eventBus.emit('dataUpdated', 'project', 'delete', id)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '删除失败')
    }
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await projectApi.list({ per_page: 0 })
    allProjects.value = res.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
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
</style>
