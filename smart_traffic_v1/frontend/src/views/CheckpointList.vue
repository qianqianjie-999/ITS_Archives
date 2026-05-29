<template>
  <div class="checkpoint-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>卡口点位列表</span>
          <el-button v-if="userStore.isEditor" type="primary" @click="showDialog = true">新增点位</el-button>
        </div>
      </template>
      <el-table :data="points" stripe v-loading="loading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="点位名称" />
        <el-table-column prop="area" label="卡口类型" />
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
        <el-form-item label="卡口类型">
          <el-select v-model="editPointForm.area" placeholder="请选择卡口类型" style="width: 100%">
            <el-option label="雷达测速卡口" value="雷达测速卡口" />
            <el-option label="闯禁区卡口" value="闯禁区卡口" />
            <el-option label="大货车不靠右行驶卡口" value="大货车不靠右行驶卡口" />
            <el-option label="单行道卡口" value="单行道卡口" />
          </el-select>
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
import { checkpointPointApi } from '@/api/points'
import { useUserStore } from '@/stores/user'
import type { CheckpointPoint } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const points = ref<CheckpointPoint[]>([])
const loading = ref(false)
const showDialog = ref(false)

const editPointForm = reactive<Partial<CheckpointPoint>>({
  id: undefined,
  name: '',
  area: '',
  type: ''
})

function goToDetail(id: number) {
  router.push(`/checkpoints/${id}`)
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
  checkpointPointApi.list().then(data => {
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
