<template>
  <div class="point-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>点位列表</span>
        </div>
      </template>
      <el-table :data="points" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="点位名称" />
        <el-table-column prop="area" label="区域" />
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
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { pointApi } from '@/api/points'
import type { Point } from '@/types'

const points = ref<Point[]>([])
const loading = ref(false)

function getStatusType(status?: string) {
  switch (status) {
    case '在保': return 'success'
    case '过保': return 'danger'
    default: return 'info'
  }
}

async function fetchData() {
  loading.value = true
  try {
    points.value = await pointApi.list()
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>