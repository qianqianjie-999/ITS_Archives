import apiClient from './index'
import type { ParkingEnforcementPoint, CheckpointPoint, ParkingEnforcement, Checkpoint, BackendDevice, WarrantyExtension } from '@/types'

export interface ParkingPointDetail {
  point: ParkingEnforcementPoint
  parking_enforcements: ParkingEnforcement[]
  warranty_extensions: WarrantyExtension[]
}

export interface CheckpointPointDetail {
  point: CheckpointPoint
  checkpoints: Checkpoint[]
  warranty_extensions: WarrantyExtension[]
}

export interface ExtendWarrantyData {
  project_id?: number
  project_name?: string
  warranty_expire_date: string
}

export const pointApi = {
  list: () => apiClient.get<ParkingEnforcementPoint[]>('/points/parking-points'),

  create: (data: Partial<ParkingEnforcementPoint>) => apiClient.post('/points/parking-points', data),

  get: (id: number) => apiClient.get<ParkingPointDetail>(`/points/parking-points/${id}`),

  update: (id: number, data: Partial<ParkingEnforcementPoint>) => apiClient.put(`/points/parking-points/${id}`, data),

  delete: (id: number) => apiClient.delete(`/points/parking-points/${id}`),

  createParkingEnforcement: (pointId: number, data: Partial<ParkingEnforcement>) =>
    apiClient.post(`/points/parking-points/${pointId}/devices`, data),

  getParkingEnforcements: (pointId: number) =>
    apiClient.get<ParkingEnforcement[]>(`/points/parking-points/${pointId}/devices`),

  updateParkingEnforcement: (pointId: number, peId: number, data: Partial<ParkingEnforcement>) =>
    apiClient.put(`/points/parking-points/${pointId}/devices/${peId}`, data),

  deleteParkingEnforcement: (pointId: number, peId: number) =>
    apiClient.delete(`/points/parking-points/${pointId}/devices/${peId}`),

  getParkingEnforcementsAll: () => apiClient.get<ParkingEnforcement[]>('/points/parking-enforcement'),

  extendWarranty: (pointId: number, data: ExtendWarrantyData) =>
    apiClient.post(`/points/parking-points/${pointId}/extend-warranty`, data),
}

export const checkpointPointApi = {
  list: () => apiClient.get<CheckpointPoint[]>('/points/checkpoint-points'),

  create: (data: Partial<CheckpointPoint>) => apiClient.post('/points/checkpoint-points', data),

  get: (id: number) => apiClient.get<CheckpointPointDetail>(`/points/checkpoint-points/${id}`),

  update: (id: number, data: Partial<CheckpointPoint>) => apiClient.put(`/points/checkpoint-points/${id}`, data),

  delete: (id: number) => apiClient.delete(`/points/checkpoint-points/${id}`),

  createCheckpoint: (pointId: number, data: Partial<Checkpoint>) =>
    apiClient.post(`/points/checkpoint-points/${pointId}/devices`, data),

  getCheckpoints: (pointId: number) =>
    apiClient.get<Checkpoint[]>(`/points/checkpoint-points/${pointId}/devices`),

  updateCheckpoint: (pointId: number, cpId: number, data: Partial<Checkpoint>) =>
    apiClient.put(`/points/checkpoint-points/${pointId}/devices/${cpId}`, data),

  deleteCheckpoint: (pointId: number, cpId: number) =>
    apiClient.delete(`/points/checkpoint-points/${pointId}/devices/${cpId}`),

  getCheckpointsAll: () => apiClient.get<Checkpoint[]>('/points/checkpoints'),

  extendWarranty: (pointId: number, data: ExtendWarrantyData) =>
    apiClient.post(`/points/checkpoint-points/${pointId}/extend-warranty`, data),
}

export const backendDeviceApi = {
  list: () => apiClient.get<BackendDevice[]>('/points/backend-devices'),

  create: (data: Partial<BackendDevice>) => apiClient.post('/points/backend-devices', data),

  update: (id: number, data: Partial<BackendDevice>) => apiClient.put(`/points/backend-device/${id}`, data),

  delete: (id: number) => apiClient.delete(`/points/backend-device/${id}`),
}
