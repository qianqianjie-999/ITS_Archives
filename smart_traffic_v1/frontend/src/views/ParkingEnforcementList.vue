<template>
  <div class="parking-enforcement-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>违停点位列表</span>
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
            <el-input v-model="searchKeyword" placeholder="搜索点位名称、抓拍区域..." clearable>
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
        <el-table-column prop="area" label="抓拍区域" />
        <el-table-column prop="type" label="安装位置" width="120" />
        <el-table-column prop="latitude" label="纬度" width="120" />
        <el-table-column prop="longitude" label="经度" width="120" />
        <el-table-column label="关联项目" width="100" align="center">
          <template #default="{ row }">
            <span :class="hasProject(row.id) ? 'status-dot green' : 'status-dot gray'" />
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
        <el-form-item label="抓拍区域">
          <el-input v-model="editPointForm.area" />
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
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { pointApi } from '@/api/points'
import { memoApi } from '@/api/memos'
import { useUserStore } from '@/stores/user'
import type { ParkingEnforcementPoint } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const allPoints = ref<ParkingEnforcementPoint[]>([])
const allParkingEnforcements = ref<any[]>([])
const allMemos = ref<any[]>([])
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

const editPointForm = reactive<Partial<ParkingEnforcementPoint>>({
  id: undefined,
  name: '',
  area: '',
  type: '',
  latitude: undefined,
  longitude: undefined
})

function goToDetail(id: number) {
  router.push(`/parking-enforcements/${id}`)
}

function openAddDialog() {
  editPointForm.id = undefined
  editPointForm.name = ''
  editPointForm.area = ''
  editPointForm.type = ''
  showDialog.value = true
}

function editPoint(point: ParkingEnforcementPoint) {
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
    pointApi.update(editPointForm.id, data).then(() => {
      ElMessage.success('编辑成功')
      showDialog.value = false
      loadPoints()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '编辑失败')
    })
  } else {
    pointApi.create(data).then(() => {
      ElMessage.success('新增成功')
      showDialog.value = false
      loadPoints()
    }).catch((err) => {
      ElMessage.error(err.response?.data?.message || '新增失败')
    })
  }
}

function deletePoint(id: number) {
  ElMessageBox.confirm('确定删除该点位？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    pointApi.delete(id).then(() => {
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
    pointApi.list({ per_page: 0 }),
    pointApi.getParkingEnforcementsAll(),
    memoApi.list({ per_page: 0 })
  ]).then(([pointsRes, enforcementsRes, memosRes]) => {
    allPoints.value = pointsRes.data
    allParkingEnforcements.value = enforcementsRes.data || []
    allMemos.value = memosRes.data || []
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

function hasProject(pointId: number): boolean {
  return allParkingEnforcements.value.some(pe => pe.point_id === pointId && pe.project_id)
}

function hasAttachment(pointId: number): boolean {
  return allMemos.value.some(m => m.parking_enforcement_id === pointId && m.attachments && m.attachments.length > 0)
}

onMounted(() => {
  loadPoints()
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
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-dot.green {
  background-color: #67c23a;
}

.status-dot.gray {
  background-color: #909399;
}
</style>
