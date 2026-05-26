<template>
  <div class="log-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
        </div>
      </template>
      <el-table :data="logs" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="操作用户" width="120" />
        <el-table-column prop="operation_type" label="操作类型" width="120" />
        <el-table-column prop="entity_type" label="实体类型" width="120" />
        <el-table-column prop="entity_id" label="实体ID" width="80" />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="operation_time" label="操作时间" width="180" />
      </el-table>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 20px"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api'
import type { OperationLog } from '@/types'

const logs = ref<OperationLog[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

async function fetchData() {
  loading.value = true
  try {
    const response = await apiClient.get('/logs/', {
      params: { page: currentPage.value, per_page: pageSize.value }
    }) as unknown as { logs: OperationLog[], total: number }
    logs.value = response.logs
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>