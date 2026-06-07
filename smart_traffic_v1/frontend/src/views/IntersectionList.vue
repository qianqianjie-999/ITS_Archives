<template>
  <div class="intersection-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>路口列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showDialog = true">新增路口</el-button>
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
            <el-input v-model="searchKeyword" placeholder="搜索路口名称、道路..." clearable>
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-col>
        </el-row>
      </div>

      <el-table :data="pagedIntersections" stripe v-loading="loading">
        <el-table-column label="序号" width="60">
          <template #default="{ $index }">
            {{ (currentPage - 1) * perPage + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="路口名称" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="east_west_road" label="东西路" />
        <el-table-column prop="north_south_road" label="南北路" />
        <el-table-column prop="latitude" label="纬度" width="120" />
        <el-table-column prop="longitude" label="经度" width="120" />
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToDetail(row.id)">
              详情
            </el-button>
            <el-button v-if="userStore.isEditor" type="success" size="small" @click="editIntersection(row)">
              编辑
            </el-button>
            <el-button v-if="userStore.isEditor" type="danger" size="small" @click="deleteIntersection(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div style="display: flex; justify-content: center; margin-top: 16px">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="perPage"
          :total="filteredIntersections.length"
          layout="total, prev, pager, next"
          class="dark-pagination"
        />
      </div>
    </el-card>

    <el-dialog v-model="showDialog" :title="editIntersectionForm.id ? '编辑路口' : '新增路口'" width="400px">
      <el-form :model="editIntersectionForm" label-width="80px">
        <el-form-item label="路口名称" required>
          <el-input v-model="editIntersectionForm.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="editIntersectionForm.type" placeholder="请选择路口类型">
            <el-option label="十字路口" value="十字路口" />
            <el-option label="丁字路口" value="丁字路口" />
            <el-option label="行人过街" value="行人过街" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="东西路">
          <el-input v-model="editIntersectionForm.east_west_road" />
        </el-form-item>
        <el-form-item label="南北路">
          <el-input v-model="editIntersectionForm.north_south_road" />
        </el-form-item>
        <el-form-item label="纬度">
          <el-input v-model.number="editIntersectionForm.latitude" placeholder="例如：31.2304" />
        </el-form-item>
        <el-form-item label="经度">
          <el-input v-model.number="editIntersectionForm.longitude" placeholder="例如：121.4737" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitIntersection">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { intersectionApi } from '@/api/intersections'
import { useUserStore } from '@/stores/user'
import type { Intersection } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const allIntersections = ref<Intersection[]>([])
const loading = ref(false)
const showDialog = ref(false)
const currentPage = ref(1)
const perPage = ref(20)
const searchKeyword = ref('')
const filterWarranty = ref('')

const filteredIntersections = computed(() => {
  return allIntersections.value.filter(i => {
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase()
      const haystack = [i.name, i.type, i.east_west_road, i.north_south_road].filter(Boolean).join(' ').toLowerCase()
      if (!haystack.includes(kw)) return false
    }
    if (filterWarranty.value) {
      const status = (i as any).warranty_status
      if (status !== filterWarranty.value) return false
    }
    return true
  })
})

const pagedIntersections = computed(() => {
  const start = (currentPage.value - 1) * perPage.value
  return filteredIntersections.value.slice(start, start + perPage.value)
})

watch([searchKeyword, filterWarranty], () => {
  currentPage.value = 1
})

const editIntersectionForm = reactive<Partial<Intersection>>({
  id: undefined,
  name: '',
  type: '',
  east_west_road: '',
  north_south_road: '',
  latitude: undefined,
  longitude: undefined
})

function goToDetail(id: number) {
  router.push(`/intersections/${id}`)
}

function editIntersection(row: Intersection) {
  editIntersectionForm.id = row.id
  editIntersectionForm.name = row.name
  editIntersectionForm.type = row.type || ''
  editIntersectionForm.east_west_road = row.east_west_road || ''
  editIntersectionForm.north_south_road = row.north_south_road || ''
  showDialog.value = true
}

async function submitIntersection() {
  try {
    if (editIntersectionForm.id) {
      await intersectionApi.update(editIntersectionForm.id, editIntersectionForm)
      ElMessage.success('更新成功')
    } else {
      await intersectionApi.create(editIntersectionForm)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    editIntersectionForm.id = undefined
    editIntersectionForm.name = ''
    editIntersectionForm.type = ''
    editIntersectionForm.east_west_road = ''
    editIntersectionForm.north_south_road = ''
    fetchData()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.message || '操作失败')
  }
}

async function deleteIntersection(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该路口吗？', '警告', { type: 'warning' })
    await intersectionApi.delete(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.message || '删除失败')
    }
  }
}

async function fetchData() {
  loading.value = true
  try {
    const res = await intersectionApi.list({ per_page: 0 })
    allIntersections.value = res.data
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

.filter-bar {
  margin-bottom: 16px;
}
</style>
