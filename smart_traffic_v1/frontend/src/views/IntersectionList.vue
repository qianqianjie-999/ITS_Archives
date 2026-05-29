<template>
  <div class="intersection-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>路口列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showDialog = true">新增路口</el-button>
        </div>
      </template>
      <el-table :data="intersections" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="路口名称" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="east_west_road" label="东西路" />
        <el-table-column prop="north_south_road" label="南北路" />
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
    </el-card>

    <el-dialog v-model="showDialog" :title="editIntersectionForm.id ? '编辑路口' : '新增路口'" width="400px">
      <el-form :model="editIntersectionForm" label-width="80px">
        <el-form-item label="路口名称" required>
          <el-input v-model="editIntersectionForm.name" />
        </el-form-item>
        <el-form-item label="类型">
          <el-input v-model="editIntersectionForm.type" />
        </el-form-item>
        <el-form-item label="东西路">
          <el-input v-model="editIntersectionForm.east_west_road" />
        </el-form-item>
        <el-form-item label="南北路">
          <el-input v-model="editIntersectionForm.north_south_road" />
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
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { intersectionApi } from '@/api/intersections'
import { useUserStore } from '@/stores/user'
import type { Intersection } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const intersections = ref<Intersection[]>([])
const loading = ref(false)
const showDialog = ref(false)

const editIntersectionForm = reactive<Partial<Intersection>>({
  id: undefined,
  name: '',
  type: '',
  east_west_road: '',
  north_south_road: ''
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
    const res = await intersectionApi.list()
    intersections.value = res as unknown as Intersection[]
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