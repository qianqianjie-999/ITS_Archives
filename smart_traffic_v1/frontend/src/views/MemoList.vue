<template>
  <div class="memo-page">
    <div class="page-header">
      <h1>备忘录管理</h1>
      <el-button type="primary" @click="openCreateModal">
        <el-icon><Plus /></el-icon>
        新建备忘录
      </el-button>
    </div>

    <!-- 搜索筛选 -->
    <div class="filter-bar">
      <el-input v-model="filters.keyword" placeholder="搜索主题" clearable @clear="fetchMemos" />
      <el-input v-model="filters.create_user" placeholder="记录人" clearable @clear="fetchMemos" />
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="事件开始日期"
        end-placeholder="事件结束日期"
        value-format="YYYY-MM-DD"
        @change="handleDateChange"
      />
      <el-button @click="resetFilters">重置</el-button>
      <el-button type="primary" @click="fetchMemos">搜索</el-button>
    </div>

    <!-- 备忘录列表 -->
    <div class="memo-grid">
      <div
        v-for="memo in memos"
        :key="memo.id"
        class="memo-card"
        @click="openDetailModal(memo)"
      >
        <div class="memo-header">
          <h3 class="memo-title">{{ memo.title }}</h3>
        </div>
        <p class="memo-content">{{ memo.content?.slice(0, 100) }}{{ (memo.content?.length ?? 0) > 100 ? '...' : '' }}</p>
        <div class="memo-meta">
          <span class="meta-item">
            <el-icon><User /></el-icon>
            {{ memo.create_user }}
          </span>
          <span class="meta-item" v-if="memo.happen_time">
            <el-icon><Clock /></el-icon>
            {{ formatDate(memo.happen_time) }}
          </span>
        </div>
        <div class="memo-footer">
          <span class="attach-count" v-if="memo.attachments?.length">
            <el-icon><Paperclip /></el-icon>
            {{ memo.attachments.length }}个附件
          </span>
          <span class="create-time">创建于 {{ formatDateTime(memo.create_time) }}</span>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="total > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchMemos"
        @current-change="fetchMemos"
      />
    </div>

    <!-- 空状态 -->
    <el-empty v-if="memos.length === 0" description="暂无备忘录" />

    <!-- 详情弹窗 -->
    <el-dialog title="备忘录详情" v-model="detailVisible" width="700px" :append-to-body="false">
      <div v-if="selectedMemo" class="memo-detail">
        <div class="detail-item">
          <label>主题：</label>
          <span>{{ selectedMemo.title }}</span>
        </div>
        <div class="detail-item">
          <label>记录人：</label>
          <span>{{ selectedMemo.create_user }}</span>
        </div>
        <div class="detail-item" v-if="selectedMemo.happen_time">
          <label>事件时间：</label>
          <span>{{ formatDateTime(selectedMemo.happen_time) }}</span>
        </div>
        <div class="detail-item">
          <label>创建时间：</label>
          <span>{{ formatDateTime(selectedMemo.create_time) }}</span>
        </div>
        <div class="detail-item" v-if="selectedMemo.content">
          <label>事件内容：</label>
          <div class="content-text">{{ selectedMemo.content }}</div>
        </div>
        <div class="detail-item" v-if="selectedMemo.attachments?.length">
          <label>附件：</label>
          <div class="attachment-list">
            <div
              v-for="attach in selectedMemo.attachments"
              :key="attach.aid"
              class="attachment-item"
            >
              <el-icon><Files /></el-icon>
              <span class="file-name">{{ attach.file_name }}</span>
              <span class="file-size">({{ formatFileSize(attach.file_size) }})</span>
              <el-button size="small" @click.stop="handleDownload(attach)">下载</el-button>
              <el-button size="small" @click.stop="handlePreview(attach)" v-if="canPreview(attach.file_type)">预览</el-button>
              <el-button size="small" type="danger" @click.stop="handleDeleteAttachment(attach)">删除</el-button>
            </div>
          </div>
        </div>
        <div class="detail-item" v-else>
          <label>附件：</label>
          <span class="no-attachment">暂无附件</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="openEditModal">编辑</el-button>
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑弹窗 -->
    <el-dialog :title="isEdit ? '编辑备忘录' : '新建备忘录'" v-model="formVisible" width="600px" :append-to-body="false">
      <el-form :model="memoForm" label-width="100px" :rules="formRules" ref="formRef">
        <el-form-item label="主题" prop="title">
          <el-input v-model="memoForm.title" placeholder="请输入备忘录主题" />
        </el-form-item>
        <el-form-item label="记录人" prop="create_user">
          <el-input v-model="memoForm.create_user" placeholder="请输入记录人姓名" />
        </el-form-item>
        <el-form-item label="事件时间">
          <el-date-picker
            v-model="memoForm.happen_time"
            type="datetime"
            placeholder="选择事件发生时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="事件内容">
          <el-input
            v-model="memoForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入事件详细内容"
          />
        </el-form-item>
        <el-form-item label="附件">
          <div class="upload-area" @click="triggerFileInput">
            <el-icon :size="32"><Upload /></el-icon>
            <span>点击上传附件</span>
            <span class="upload-hint">支持图片、PDF、Word、Excel等（单文件≤10MB）</span>
          </div>
          <input
            type="file"
            ref="fileInputRef"
            multiple
            accept="image/*,.pdf,.doc,.docx,.xls,.xlsx,.zip,.rar"
            @change="handleFileChange"
            style="display: none"
          />
          <div v-if="selectedFiles.length" class="file-list">
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
              <el-icon><Files /></el-icon>
              <span>{{ file.name }}</span>
              <span class="file-size">({{ formatFileSize(file.size) }})</span>
              <el-button size="small" type="danger" @click="removeFile(index)">删除</el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus, Files, Upload, Clock, User, Paperclip } from '@element-plus/icons-vue'
import { formatDateTime, formatDate } from '@/utils/date'
import { getMemos, createMemo, updateMemo, deleteMemo, deleteAttachment, downloadAttachment, previewAttachment } from '@/api/memos'
import type { Memo, MemoForm, MemoAttachment } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

const memos = ref<Memo[]>([])
const total = ref(0)
const pagination = reactive({
  page: 1,
  per_page: 20
})
const filters = reactive({
  keyword: '',
  create_user: '',
  start_date: '',
  end_date: ''
})
const dateRange = ref<[string, string] | null>(null)

const detailVisible = ref(false)
const formVisible = ref(false)
const isEdit = ref(false)
const selectedMemo = ref<Memo | null>(null)
const formRef = ref()
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])

const memoForm = reactive<MemoForm>({
  title: '',
  content: '',
  happen_time: '',
  create_user: ''
})

const formRules = {
  title: [{ required: true, message: '请输入备忘录主题', trigger: 'blur' }],
  create_user: [{ required: true, message: '请输入记录人', trigger: 'blur' }]
}

const fetchMemos = async () => {
  try {
    const result = await getMemos({
      keyword: filters.keyword,
      create_user: filters.create_user,
      start_date: filters.start_date,
      end_date: filters.end_date,
      page: pagination.page,
      per_page: pagination.per_page
    })
    memos.value = result.items
    total.value = result.total
  } catch (error) {
    ElMessage.error('获取备忘录列表失败')
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.create_user = ''
  filters.start_date = ''
  filters.end_date = ''
  dateRange.value = null
  pagination.page = 1
  fetchMemos()
}

const handleDateChange = (val: [string, string] | null) => {
  if (val) {
    filters.start_date = val[0]
    filters.end_date = val[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
}

const openCreateModal = () => {
  isEdit.value = false
  memoForm.title = ''
  memoForm.content = ''
  memoForm.happen_time = ''
  memoForm.create_user = ''
  selectedFiles.value = []
  formVisible.value = true
}

const openDetailModal = (memo: Memo) => {
  selectedMemo.value = memo
  detailVisible.value = true
}

const openEditModal = () => {
  if (!selectedMemo.value) return
  isEdit.value = true
  memoForm.title = selectedMemo.value.title
  memoForm.content = selectedMemo.value.content || ''
  memoForm.happen_time = selectedMemo.value.happen_time || ''
  memoForm.create_user = selectedMemo.value.create_user
  selectedFiles.value = []
  detailVisible.value = false
  formVisible.value = true
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    // 检查文件大小（10MB）
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.warning(`${file.name} 超过10MB限制`)
      continue
    }
    selectedFiles.value.push(file)
  }
  target.value = ''
}

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    if (isEdit.value && selectedMemo.value) {
      await updateMemo(selectedMemo.value.id, memoForm, selectedFiles.value.length > 0 ? selectedFiles.value : undefined)
      ElMessage.success('更新成功')
    } else {
      await createMemo(memoForm, selectedFiles.value.length > 0 ? selectedFiles.value : undefined)
      ElMessage.success('创建成功')
    }
    
    formVisible.value = false
    fetchMemos()
  } catch (error: any) {
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}

const handleDelete = async () => {
  if (!selectedMemo.value) return
  
  try {
    await ElMessageBox.confirm('确定要删除这条备忘录吗？', '提示', {
      type: 'warning'
    })
    
    await deleteMemo(selectedMemo.value.id)
    ElMessage.success('删除成功')
    detailVisible.value = false
    fetchMemos()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleDeleteAttachment = async (attach: MemoAttachment) => {
  if (!selectedMemo.value) return
  
  try {
    await ElMessageBox.confirm(`确定要删除附件「${attach.file_name}」吗？`, '提示', {
      type: 'warning'
    })
    
    await deleteAttachment(selectedMemo.value.id, attach.aid)
    ElMessage.success('删除成功')
    // 刷新详情
    const result = await getMemos({ keyword: '', page: 1, per_page: 1000 })
    const updated = result.items.find(m => m.id === selectedMemo.value!.id)
    if (updated) {
      selectedMemo.value = updated
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleDownload = (attach: MemoAttachment) => {
  downloadAttachment(attach.file_path, attach.file_name)
}

const handlePreview = (attach: MemoAttachment) => {
  previewAttachment(attach.file_path)
}

const canPreview = (fileType?: string): boolean => {
  if (!fileType) return false
  const previewTypes = ['png', 'jpg', 'jpeg', 'gif', 'pdf']
  return previewTypes.includes(fileType.toLowerCase())
}

const formatFileSize = (size?: number) => {
  if (!size) return '0 B'
  if (size < 1024) return size + ' B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
  return (size / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  fetchMemos()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

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
  flex-wrap: wrap;

  .el-input {
    width: 180px;
  }
}

.memo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.memo-card {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  box-shadow: $shadow-sm;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid $primary-color;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-md;
    background: $bg-hover;
  }
}

.memo-header {
  margin-bottom: 12px;
}

.memo-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  margin: 0;
}

.memo-content {
  font-size: 14px;
  color: $text-secondary;
  line-height: 1.6;
  margin: 0 0 12px;
  white-space: pre-wrap;
}

.memo-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 13px;
  color: $text-secondary;

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.memo-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: $text-placeholder;
  padding-top: 12px;
  border-top: 1px solid $border-color;

  .attach-count {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}



:deep(.el-dialog__body) {
  max-height: 65vh;
  overflow-y: auto;
}

.memo-detail {
  .detail-item {
    margin-bottom: 16px;

    label {
      font-weight: 600;
      color: $text-primary;
      display: block;
      margin-bottom: 4px;
    }

    span, .content-text, .no-attachment {
      color: $text-secondary;
      line-height: 1.6;
    }

    .content-text {
      white-space: pre-wrap;
      background: $bg-card;
      padding: 12px;
      border-radius: 6px;
      border: 1px solid $border-color;
    }

    .no-attachment {
      color: $text-placeholder;
      font-style: italic;
    }
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
  background: $bg-card;
  border-radius: 6px;
  border: 1px solid $border-color;

  .file-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: $text-primary;
  }

  .file-size {
    color: $text-placeholder;
    font-size: 12px;
  }
}

.upload-area {
  border: 2px dashed $border-color;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: $text-secondary;
  background: $bg-card;

  &:hover {
    border-color: $primary-color;
    background: $bg-hover;
  }

  .upload-hint {
    font-size: 12px;
    color: $text-placeholder;
  }
}

.file-list {
  margin-top: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: $bg-card;
  border-radius: 6px;
  border: 1px solid $border-color;

  span {
    flex: 1;
    color: $text-primary;
  }

  .file-size {
    color: $text-placeholder;
    font-size: 12px;
  }
}
</style>