<template>
  <div class="intersection-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>路口列表</span>
        </div>
      </template>
      <el-table :data="intersections" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="路口名称" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="latest_expire_date" label="质保到期" width="120">
          <template #default="{ row }">
            {{ row.latest_expire_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="warranty_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.warranty_status)">
              {{ row.warranty_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="goToDetail(row.id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { intersectionApi } from '@/api/intersections'
import type { Intersection } from '@/types'

const router = useRouter()
const intersections = ref<Intersection[]>([])
const loading = ref(false)

function getStatusType(status?: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    default: return 'info'
  }
}

function goToDetail(id: number) {
  router.push(`/intersections/${id}`)
}

async function fetchData() {
  loading.value = true
  try {
    intersections.value = await intersectionApi.list()
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