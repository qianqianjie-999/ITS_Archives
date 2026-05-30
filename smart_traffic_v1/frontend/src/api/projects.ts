import apiClient from './index'
import type { Project } from '@/types'

interface WarrantyRecord {
  id?: number
  project_name: string
  acceptance_date: string
  warranty_expire_date: string
  extension_date: string
  facility_type?: string
  facility_id?: number
  project_id?: number
}

export const projectApi = {
  list: () => apiClient.get<Project[]>('/projects/'),

  getById: (id: number) => apiClient.get<Project>(`/projects/${id}`),

  create: (data: Partial<Project>) => apiClient.post('/projects/', data),

  update: (id: number, data: Partial<Project>) => apiClient.put(`/projects/${id}`, data),

  delete: (id: number) => apiClient.delete(`/projects/${id}`),

  getByFacility: (facilityType: string, facilityId: number) => {
    const params = { facility_type: facilityType, facility_id: facilityId }
    return apiClient.get<Project[]>('/projects/', { params })
  },

  getWarrantyExtensions: (facilityType?: string, facilityId?: number) => {
    const params: Record<string, any> = {}
    if (facilityType) params.facility_type = facilityType
    if (facilityId) params.facility_id = facilityId
    return apiClient.get<WarrantyRecord[]>('/projects/warranty-extensions', { params })
  },

  deleteWarrantyExtension: (extensionId: number) => {
    return apiClient.delete(`/projects/warranty-extensions/${extensionId}`)
  }
}