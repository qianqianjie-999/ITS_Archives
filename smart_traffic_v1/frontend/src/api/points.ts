import apiClient from './index'
import type { Point, ParkingEnforcement, Checkpoint, BackendDevice } from '@/types'

export interface PointDetail {
  point: Point
  parking_enforcements: ParkingEnforcement[]
  checkpoints: Checkpoint[]
  backend_devices: BackendDevice[]
}

export const pointApi = {
  list: () => apiClient.get<Point[]>('/points/'),

  create: (data: Partial<Point>) => apiClient.post('/points/', data),

  get: (id: number) => apiClient.get<PointDetail>(`/points/${id}`),

  update: (id: number, data: Partial<Point>) => apiClient.put(`/points/${id}`, data),

  delete: (id: number) => apiClient.delete(`/points/${id}`),

  updateParkingEnforcement: (pointId: number, peId: number, data: Partial<ParkingEnforcement>) =>
    apiClient.put(`/points/${pointId}/parking-enforcement/${peId}`, data),

  deleteParkingEnforcement: (pointId: number, peId: number) =>
    apiClient.delete(`/points/${pointId}/parking-enforcement/${peId}`),

  createParkingEnforcement: (pointId: number, data: Partial<ParkingEnforcement>) =>
    apiClient.post(`/points/${pointId}/parking-enforcement`, data),

  getParkingEnforcements: (pointId: number) => apiClient.get<ParkingEnforcement[]>(`/points/${pointId}/parking-enforcement`),

  getParkingEnforcementsAll: () => apiClient.get<ParkingEnforcement[]>('/points/parking-enforcement'),

  updateCheckpoint: (pointId: number, cpId: number, data: Partial<Checkpoint>) =>
    apiClient.put(`/points/${pointId}/checkpoint/${cpId}`, data),

  deleteCheckpoint: (pointId: number, cpId: number) =>
    apiClient.delete(`/points/${pointId}/checkpoint/${cpId}`),

  createCheckpoint: (pointId: number, data: Partial<Checkpoint>) =>
    apiClient.post(`/points/${pointId}/checkpoint`, data),

  getCheckpoints: (pointId: number) => apiClient.get<Checkpoint[]>(`/points/${pointId}/checkpoint`),

  getCheckpointsAll: () => apiClient.get<Checkpoint[]>('/points/checkpoints'),

  updateBackendDevice: (_pointId: number, bdId: number, data: Partial<BackendDevice>) =>
    apiClient.put(`/points/backend-device/${bdId}`, data),

  deleteBackendDevice: (_pointId: number, bdId: number) =>
    apiClient.delete(`/points/backend-device/${bdId}`),

  createBackendDevice: (_pointId: number, data: Partial<BackendDevice>) =>
    apiClient.post('/points/backend-devices', data),

  listBackendDevices: () => apiClient.get<BackendDevice[]>('/points/backend-devices'),

  extendWarranty: (pointId: number, projectName: string, warrantyExpireDate: string) =>
    apiClient.post(`/points/${pointId}/extend-warranty`, {
      project_name: projectName,
      warranty_expire_date: warrantyExpireDate
    })
}