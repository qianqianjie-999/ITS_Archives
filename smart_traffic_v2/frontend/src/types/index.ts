export interface User {
  id: number
  username: string
  display_name: string
  role: 'admin' | 'editor' | 'viewer'
  is_active: boolean
  last_login?: string
}

export interface Project {
  id: number
  name: string
  contract_amount?: number
  acceptance_date?: string
  warranty_period?: string
  warranty_expire_date: string
  builder?: string
  constructor?: string
}

export interface Intersection {
  id: number
  name: string
  type?: string
  warranty_status?: string
  latest_expire_date?: string
}

export interface TrafficLight {
  id: number
  intersection_id: number
  project_id: number
  project_name?: string
  warranty_expire_date?: string
  signal_type?: string
  signal_count: number
  left_arrow_count: number
  straight_arrow_count: number
  right_arrow_count: number
  full_screen_count: number
  non_motor_count: number
  pedestrian_count: number
  radar_count: number
  guide_screen_count: number
  power_source?: string
}

export interface ElectronicPolice {
  id: number
  intersection_id: number
  project_id: number
  project_name?: string
  warranty_expire_date?: string
  capture_type?: string
  terminal_server_count: number
  forward_capture_count: number
  reverse_capture_count: number
  led_light_count: number
  strobe_light_count: number
  ptz_count: number
  signal_detector_count: number
  network_source?: string
}

export interface Point {
  id: number
  name: string
  area?: string
  type?: string
  warranty_status?: string
  latest_expire_date?: string
}

export interface ParkingEnforcement {
  id: number
  point_id: number
  project_id: number
  project_name?: string
  warranty_expire_date?: string
  camera_count: number
  parking_sign_count: number
  monitor_sign_count: number
  power_source?: string
  network_source?: string
}

export interface Checkpoint {
  id: number
  point_id: number
  project_id: number
  project_name?: string
  warranty_expire_date?: string
  camera_count: number
  strobe_light_count: number
  radar_count: number
  sign_count: number
  power_source?: string
  network_source?: string
}

export interface Attachment {
  id: number
  related_entity_type: string
  related_entity_id: number
  file_name: string
  file_path: string
  file_size?: number
  mime_type?: string
  upload_time: string
  uploaded_by?: string
  description?: string
}

export interface OperationLog {
  id: number
  user_id: number
  username?: string
  operation_type: string
  entity_type?: string
  entity_id?: number
  old_value?: any
  new_value?: any
  ip_address?: string
  operation_time: string
}

export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  message?: string
  data?: T
}