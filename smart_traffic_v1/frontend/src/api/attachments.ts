import apiClient from './index'

export interface Attachment {
  id: number
  related_entity_type: string
  related_entity_id: number
  file_name: string
  file_path: string
  original_filename: string
  file_size: number
  upload_time: string
}

export const attachmentApi = {
  list: (entityType?: string, entityId?: number) => {
    const params: Record<string, any> = {}
    if (entityType) params.related_entity_type = entityType
    if (entityId) params.related_entity_id = entityId
    return apiClient.get<Attachment[]>('/attachments/', { params })
  },

  upload: (file: File, entityType: string, entityId: number) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('related_entity_type', entityType)
    formData.append('related_entity_id', String(entityId))
    return apiClient.post('/attachments/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  download: (attachmentId: number) => {
    return apiClient.get(`/attachments/${attachmentId}`, {
      responseType: 'blob'
    })
  },

  delete: (attachmentId: number) => {
    return apiClient.delete(`/attachments/${attachmentId}`)
  }
}