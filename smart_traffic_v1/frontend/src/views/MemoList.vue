<template>
  <div class="memo-page">
    <div class="page-header">
      <h1>备忘录管理</h1>
      <el-button type="primary" @click="openCreateModal">
        <el-icon><Plus /></el-icon>
        新建备忘录
      </el-button>
    </div>

    <div class="filter-bar">
      <el-select v-model="filterStatus" placeholder="状态筛选">
        <el-option label="全部" value="" />
        <el-option label="待办" value="pending" />
        <el-option label="进行中" value="in_progress" />
        <el-option label="已完成" value="completed" />
      </el-select>
      <el-select v-model="filterPriority" placeholder="优先级筛选">
        <el-option label="全部" value="" />
        <el-option label="高" value="high" />
        <el-option label="中" value="medium" />
        <el-option label="低" value="low" />
      </el-select>
      <el-input v-model="searchKeyword" placeholder="搜索标题" />
    </div>

    <div class="memo-grid">
      <div
        v-for="memo in filteredMemos"
        :key="memo.id"
        class="memo-card"
        :class="[`priority-${memo.priority}`, `status-${memo.status}`]"
        @click="openDetailModal(memo)"
      >
        <div class="memo-header">
          <h3 class="memo-title">{{ memo.title }}</h3>
          <span class="priority-badge" :class="memo.priority">{{ priorityMap[memo.priority] }}</span>
        </div>
        <p class="memo-content">{{ memo.content?.slice(0, 100) }}{{ (memo.content?.length ?? 0) > 100 ? '...' : '' }}</p>
        <div class="memo-footer">
          <span class="status-tag" :class="memo.status">{{ statusMap[memo.status] }}</span>
          <span v-if="memo.category" class="category-tag">{{ memo.category }}</span>
          <span class="attach-count" v-if="memo.attachments?.length">
            <el-icon><Paperclip /></el-icon>
            {{ memo.attachments.length }}
          </span>
        </div>
        <div class="memo-time">{{ formatDateTime(memo.updated_at) }}</div>
      </div>
    </div>

    <el-dialog title="备忘录详情" :visible.sync="detailVisible" width="600px">
      <div v-if="selectedMemo" class="memo-detail">
        <div class="detail-header">
          <span class="priority-badge large" :class="selectedMemo.priority">{{ priorityMap[selectedMemo.priority] }}</span>
          <span class="status-tag" :class="selectedMemo.status">{{ statusMap[selectedMemo.status] }}</span>
        </div>
        <h2>{{ selectedMemo.title }}</h2>
        <p class="detail-content">{{ selectedMemo.content }}</p>
        <div v-if="selectedMemo.category" class="detail-category">
          <el-tag>{{ selectedMemo.category }}</el-tag>
        </div>
        <div v-if="selectedMemo.attachments?.length" class="detail-attachments">
          <h4>附件</h4>
          <div class="attachment-list">
            <div
              v-for="(attach, index) in selectedMemo.attachments"
              :key="index"
              class="attachment-item"
            >
              <el-icon><Files /></el-icon>
              <span>{{ attach.original_filename }}</span>
              <el-button size="small" @click.stop="downloadAttachment(attach.file_name, attach.original_filename)">下载</el-button>
              <el-button size="small" @click.stop="previewAttachment(attach.file_name)" v-if="isImage(attach.file_name)">预览</el-button>
            </div>
          </div>
        </div>
        <div class="detail-time">
          创建时间: {{ formatDateTime(selectedMemo.created_at) }}
          <br>
          更新时间: {{ formatDateTime(selectedMemo.updated_at) }}
        </div>
      </div>
    </el-dialog>

    <el-dialog title="新建/编辑备忘录" :visible.sync="createVisible" width="600px">
      <el-form :model="memoForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="memoForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="内容">
          <el-textarea v-model="memoForm.content" rows="4" placeholder="请输入内容" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="memoForm.category" placeholder="请输入分类标签" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="memoForm.priority">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="memoForm.status">
            <el-option label="待办" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="附件">
          <div class="upload-area">
            <input
              type="file"
              ref="fileInput"
              multiple
              accept="image/*,.pdf,.doc,.docx,.xls,.xlsx"
              @change="handleFileUpload"
              class="file-input"
            />
            <div class="upload-btn" @click="triggerFileInput">
              <el-icon :size="32"><Upload /></el-icon>
              <span>点击上传附件</span>
              <span class="upload-hint">支持图片、PDF、Word、Excel</span>
            </div>
          </div>
          <div v-if="uploadedFiles.length" class="uploaded-files">
            <div
              v-for="(file, index) in uploadedFiles"
              :key="index"
              class="uploaded-item"
            >
              <el-icon><Files /></el-icon>
              <span>{{ file.original_filename }}</span>
              <el-button size="small" @click="removeFile(index)">删除</el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMemo">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Paperclip, Files, Upload } from '@element-plus/icons-vue'
import { formatDateTime } from '@/utils/date'
import { createMemo, getMemos } from '@/api/memos'
import type { Memo, MemoForm } from '@/types'

const filterStatus = ref('')
const filterPriority = ref('')
const searchKeyword = ref('')
const detailVisible = ref(false)
const createVisible = ref(false)
const selectedMemo = ref<Memo | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const uploadedFiles = ref<Array<{ file_name: string; original_filename: string }>>([])
const memos = ref<Memo[]>([])

const memoForm = ref<MemoForm>({
  title: '',
  content: '',
  category: '',
  priority: 'medium',
  status: 'pending',
  attachments: []
})

const priorityMap: Record<string, string> = {
  high: '高优先级',
  medium: '中优先级',
  low: '低优先级'
}

const statusMap: Record<string, string> = {
  pending: '待办',
  in_progress: '进行中',
  completed: '已完成'
}

const filteredMemos = computed(() => {
  return memos.value.filter(memo => {
    const statusMatch = !filterStatus.value || memo.status === filterStatus.value
    const priorityMatch = !filterPriority.value || memo.priority === filterPriority.value
    const keywordMatch = !searchKeyword.value || memo.title.includes(searchKeyword.value)
    return statusMatch && priorityMatch && keywordMatch
  })
})

const fetchMemos = async () => {
  const result = await getMemos()
  memos.value = result.data
}

const openCreateModal = () => {
  memoForm.value = {
    title: '',
    content: '',
    category: '',
    priority: 'medium',
    status: 'pending',
    attachments: []
  }
  uploadedFiles.value = []
  createVisible.value = true
}

const openDetailModal = (memo: Memo) => {
  selectedMemo.value = memo
  detailVisible.value = true
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/attachments/upload', {
      method: 'POST',
      body: formData
    })

    if (response.ok) {
      const data = await response.json()
      uploadedFiles.value.push({
        file_name: data.file_name,
        original_filename: data.original_filename
      })
      memoForm.value.attachments = uploadedFiles.value
    }
  }

  target.value = ''
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
  memoForm.value.attachments = uploadedFiles.value
}

const saveMemo = async () => {
  if (!memoForm.value.title) {
    alert('请输入标题')
    return
  }

  await createMemo(memoForm.value)
  createVisible.value = false
  await fetchMemos()
}

const downloadAttachment = (fileName: string, originalName: string) => {
  const url = `/api/attachments/download/${fileName}?filename=${encodeURIComponent(originalName)}`
  const a = document.createElement('a')
  a.href = url
  a.download = originalName
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const previewAttachment = (fileName: string) => {
  const url = `/api/attachments/download/${fileName}?preview=true`
  window.open(url, '_blank')
}

const isImage = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext || '')
}

fetchMemos()
</script>

<style lang="scss" scoped>
.memo-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;

  .el-select {
    width: 120px;
  }

  .el-input {
    width: 200px;
  }
}

.memo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.memo-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }

  &.priority-high {
    border-left-color: #ef4444;
  }

  &.priority-medium {
    border-left-color: #f59e0b;
  }

  &.priority-low {
    border-left-color: #10b981;
  }
}

.memo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.memo-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.priority-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;

  &.high {
    background: #fee2e2;
    color: #dc2626;
  }

  &.medium {
    background: #fef3c7;
    color: #d97706;
  }

  &.low {
    background: #d1fae5;
    color: #059669;
  }

  &.large {
    font-size: 14px;
    padding: 4px 12px;
  }
}

.memo-content {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 12px;
  white-space: pre-wrap;
}

.memo-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.status-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;

  &.pending {
    background: #e0e7ff;
    color: #4338ca;
  }

  &.in_progress {
    background: #dbeafe;
    color: #1d4ed8;
  }

  &.completed {
    background: #d1fae5;
    color: #059669;
  }
}

.category-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f3f4f6;
  color: #374151;
}

.attach-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
}

.memo-time {
  font-size: 12px;
  color: #9ca3af;
}

.memo-detail {
  .detail-header {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }

  h2 {
    font-size: 20px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 16px;
  }

  .detail-content {
    font-size: 14px;
    color: #4b5563;
    line-height: 1.8;
    white-space: pre-wrap;
    margin: 0 0 16px;
  }

  .detail-category {
    margin-bottom: 16px;
  }

  .detail-attachments {
    margin-bottom: 16px;

    h4 {
      margin: 0 0 12px;
      font-size: 14px;
      font-weight: 600;
    }
  }

  .attachment-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .attachment-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f9fafb;
    border-radius: 6px;
  }

  .detail-time {
    font-size: 12px;
    color: #9ca3af;
  }
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: #3b82f6;
    background: #eff6ff;
  }
}

.file-input {
  display: none;
}

.upload-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #6b7280;
}

.upload-hint {
  font-size: 12px;
  color: #9ca3af;
}

.uploaded-files {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.uploaded-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
}
</style>