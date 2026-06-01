import apiClient from './index'

export const maintenanceApi = {
  getMaintenanceRecords: (facilityType: string, facilityId: number) =>
    apiClient.get(`/maintenance/${facilityType}/${facilityId}`),

  createMaintenanceRecord: (data: {
    facility_type: string
    facility_id: number
    fault_level: string
    fault_description: string
    solution?: string
  }) => apiClient.post('/maintenance/', data),

  deleteMaintenanceRecord: (id: number) =>
    apiClient.delete('/maintenance/', { params: { id } })
}