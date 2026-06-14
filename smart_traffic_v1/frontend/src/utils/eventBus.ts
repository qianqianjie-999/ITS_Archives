export type DataEventType =
  | 'intersection'
  | 'trafficLight'
  | 'electronicPolice'
  | 'parkingEnforcement'
  | 'parkingEnforcementPoint'
  | 'checkpoint'
  | 'checkpointPoint'
  | 'skyNet'
  | 'skyNetPoint'
  | 'backendDevice'
  | 'project'
  | 'warrantyExtension'
  | 'maintenance'
  | 'attachment'
  | 'all'

export interface DataEventPayload {
  type: DataEventType
  action?: 'create' | 'update' | 'delete'
  id?: number
  timestamp: number
}

type EventCallback = (payload: DataEventPayload) => void

class EventBus {
  private listeners: Map<string, Set<EventCallback>> = new Map()
  private debounceTimers: Map<string, ReturnType<typeof setTimeout>> = new Map()
  private debouncePayloads: Map<string, DataEventPayload> = new Map()
  private readonly debounceDelay = 500

  on(event: string, callback: EventCallback): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: EventCallback): void {
    const callbacks = this.listeners.get(event)
    if (callbacks) {
      callbacks.delete(callback)
    }
  }

  emit(event: string, type: DataEventType | string, action?: 'create' | 'update' | 'delete', id?: number): void {
    const payload: DataEventPayload = {
      type: type as DataEventType,
      action,
      id,
      timestamp: Date.now()
    }

    const existingTimer = this.debounceTimers.get(event)
    if (existingTimer) {
      clearTimeout(existingTimer)
    }

    this.debouncePayloads.set(event, payload)

    const timer = setTimeout(() => {
      const callbacks = this.listeners.get(event)
      const finalPayload = this.debouncePayloads.get(event) || payload
      if (callbacks) {
        callbacks.forEach(callback => callback(finalPayload))
      }
      this.debounceTimers.delete(event)
      this.debouncePayloads.delete(event)
    }, this.debounceDelay)

    this.debounceTimers.set(event, timer)
  }
}

export const eventBus = new EventBus()
