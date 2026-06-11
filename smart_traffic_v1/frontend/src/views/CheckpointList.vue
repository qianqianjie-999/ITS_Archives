<template>
  <div class="checkpoint-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>卡口点位列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="openAddDialog">新增点位</el-button>
        </div>
      </template>

      <div class="filter-bar">
        <el-row :gutter="12">
          <el-col :span="10">
            <el-select v-model="filterWarranty" placeholder="质保状态" clearable>
              <el-option label="全部" value="" />
              <el-option label="在保" value="在保" />
              <el-option label="过保" value="过保" />
              <el-option label="点位无关联项目" value="点位无关联项目" />
            </el-select>
          </el-col>
          <el-col :span="14">
            <el-input v-model="searchKeyword" placeholder="搜索点位名称、卡口类型..." clearable>
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-col>
        </el-row>
      </div>

      <el-table :data="pagedPoints" stripe v-loading="loading">
        <el-table-column label="序号" width="60">
          <template #default="{ $index }">
            {{ (currentPage - 1) * perPage + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="点位名称" />
        <el-table-column prop="area" label="卡口类型" />
        <el-table-column prop="type" label="安装位置" width="120" />
        <el-table-column prop="latitude" label="纬度" width="120" />
        <el-table-column prop="longitude" label="经度" width="120" />
        <el-table-column label="质保状态" width="80" align="center">
          <template #default="{ row }">
            <span
              class="warranty-dot"
              :class="getWarrantyClass(row)"
              :title="row.status || '点位无关联项目'"
            />
          </template>
        </el-table-column>
        <el-table-column label="附件" width="80" align="center">
          <template #default="{ row }">
            <span :class="hasAttachment(row.id) ? 'status-dot green' : 'status-dot gray'" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToDetail(row.id)">
              详情
            </el-button>
            <el-button v-if="userStore.isEditor" type="success" size="small" @click="editPoint(row)">
              编辑
            </el-button>
            <el-button v-if="userStore.isEditor" type="danger" size="small" @click="deletePoint(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="perPage"
          :total="filteredPoints.length"
          layout="total, prev, pager, next"
          class="dark-pagination"
        />
      </div>
    </el-card>

    <el-dialog v-model="showDialog" :title="editPointForm.id ? '编辑点位' : '新增点位'" width="400px">
      <el-form :model="editPointForm" label-width="80px">
        <el-form-item label="点位名称" required>
          <el-input v-model="editPointForm.name" />
        </el-form-item>
        <el-form-item label="卡口类型">
          <el-select v-model="editPointForm.area" placeholder="请选择卡口类型" style="width: 100%">
            <el-option label="雷达测速卡口" value="雷达测速卡口" />
            <el-option label="闯禁区卡口" value="闯禁区卡口" />
            <el-option label="大货车不靠右行驶卡口" value="大货车不靠右行驶卡口" />
            <el-option label="单行道卡口" value="单行道卡口" />
            <el-option label="区间测速" value="区间测速" />
          </el-select>
        </el-form-item>
        <el-form-item label="安装位置">
          <el-input v-model="editPointForm.type" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input v-model.number="editPointForm.latitude" placeholder="例如：31.2304" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input v-model.number="editPointForm.longitude" placeholder="例如：121.4737" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPoint">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { checkpointPointApi } from '@/api/points'
import { attachmentApi, type Attachment } from '@/api/attachments'
import { useUserStore } from '@/stores/user'
import type { CheckpointPoint } from '@/types'
import { eventBus } from '@/utils/eventBus'

const router = useRouter()
const userStore = useUserStore()
const allPoints = ref<CheckpointPoint[]>([])
const allCheckpoints = ref<any[]>([])
const allAttachments = ref<Attachment[]>([])
const loading = ref(false)
const showDialog = ref(false)
const currentPage = ref(1)
const perPage = ref(20)
const searchKeyword = ref('')
const filterWarranty = ref('')

const filteredPoints = computed(() => {
  return allPoints.value.filter(p => {
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      const haystack = [p.name, p.area, p.type].filter(Boolean).join(' ').toLowerCase()
      if (!haystack.includes(kw)) return false
    }
    if (filterWarranty.value) {
      if ((p as any).status !== filterWarranty.value) return false
    }
    return true
  })
})

const pagedPoints = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredPoints.value.slice(start, start + perPage.value)
})

watch([searchKeyword, filterWarranty], () => {
  currentPage.value = 1
})

const editPointForm = reactive<Partial<CheckpointPoint>>({
  id: undefined,
  name: '',
  area: '',
  type: '',
  latitude: undefined,
  longitude: undefined
})

function goToDetail(id: number) {
  router.push(`/checkpoints/${id}`)
}

function openAddDialog() {
  editPointForm.id = undefined
  editPointForm.name = ''
  editPointForm.area = ''
  editPointForm.type = ''
  showDialog.value = true
}

function editPoint(point: CheckpointPoint) {
  editPointForm.id = point.id
  editPointForm.name = point.name
  editPointForm.area = point.area || ''
  editPointForm.type = point.type || ''
  showDialog.value = true
}

function submitPoint() {
  if (!editPointForm.name) {
    ElMessage.error('请输入点位名称')
    return
  }
  
  const data = {
    name: editPointForm.name,
    area: editPointForm.area,
    type: editPointForm.type
  }

  if (editPointForm.id) {
    checkpointPointApi.update(editPointForm.id, data).then(() => {
      ElMessage.success('编辑成功')
      showDialog.value = false
      loadPoints()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '编辑失败')
    })
  } else {
    checkpointPointApi.create(data).then(() => {
      ElMessage.success('创建成功')
      showDialog.value = false
      loadPoints()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '创建失败')
    })
  }
}

function deletePoint(id: number) {
  ElMessageBox.confirm('确定要删除此点位吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    checkpointPointApi.delete(id).then(() => {
      ElMessage.success('删除成功')
      loadPoints()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '删除失败')
    })
  }).catch(() => {})
}

function loadPoints() {
  loading.value = true
  Promise.all([
    checkpointPointApi.list({ per_page: 0 }),
    checkpointPointApi.getCheckpointsAll(),
    attachmentApi.list('checkpoint')
  ]).then(([pointsRes, checkpointsRes, attachmentsRes]) => {
    allPoints.value = pointsRes.data
    allCheckpoints.value = checkpointsRes.data || []
    allAttachments.value = attachmentsRes.data || []
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

function hasProject(pointId: number): boolean {
  return allCheckpoints.value.some(cp => cp.point_id === pointId && cp.project_id)
}

function hasAttachment(pointId: number): boolean {
  return allAttachments.value.some(a => a.related_entity_id === pointId)
}

function getWarrantyClass(row: any): string {
  const status = row.status
  if (status === '在保') return 'warranty-green'
  if (status === '过保') return 'warranty-red'
  return 'warranty-gray'
}

function handleDataUpdated() {
  loadPoints()
}

onMounted(() => {
  loadPoints()
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

.warranty-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.warranty-green {
  background-color: #67c23a;
}

.warranty-red {
  background-color: #f56c6c;
}

.warranty-gray {
  background-color: #909399;
}
</style>
