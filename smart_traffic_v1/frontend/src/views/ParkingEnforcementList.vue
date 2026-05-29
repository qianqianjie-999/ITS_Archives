<template>
  <div class="parking-enforcement-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>违停点位列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showDialog = true">新增点位</el-button>
        </div>
      </template>
      <el-table :data="points" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="点位名称" />
        <el-table-column prop="area" label="抓拍区域" />
        <el-table-column prop="type" label="安装位置" width="120" />
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
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="submitPoint">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pointApi } from '@/api/points'
import { useUserStore } from '@/stores/user'
import type { ParkingEnforcementPoint } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const points = ref<ParkingEnforcementPoint[]>([])
const loading = ref(false)
const showDialog = ref(false)

const editPointForm = reactive<Partial<ParkingEnforcementPoint>>({
  id: undefined,
  name: '',
  area: '',
  type: ''
})

function goToDetail(id: number) {
  router.push(`/parking-enforcements/${id}`)
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
  pointApi.list().then(data => {
    points.value = data
    loading.value = false
  }).catch(() => {
    loading.value = false
  })
}

onMounted(() => {
  loadPoints()
})
</script>
