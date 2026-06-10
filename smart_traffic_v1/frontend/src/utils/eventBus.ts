type EventCallback = (type: string) => void

class EventBus {
  private listeners: Map<string, Set<EventCallback>> = new Map()
  private debounceTimers: Map<string, ReturnType<typeof setTimeout>> = new Map()
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

  emit(event: string, type: string): void {
    const existingTimer = this.debounceTimers.get(event)
    if (existingTimer) {
      clearTimeout(existingTimer)
    }

    const timer = setTimeout(() => {
      const callbacks = this.listeners.get(event)
      if (callbacks) {
        callbacks.forEach(callback => callback(type))
      }
      this.debounceTimers.delete(event)
    }, this.debounceDelay)

    this.debounceTimers.set(event, timer)
  }
}

export const eventBus = new EventBus()