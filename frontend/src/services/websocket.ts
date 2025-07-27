import type { WebSocketMessage } from '../types';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 3000;
  private listeners: ((message: WebSocketMessage) => void)[] = [];

  connect(sessionId: string) {
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/${sessionId}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage;
          this.notifyListeners(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect(sessionId);
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }

  private attemptReconnect(sessionId: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(sessionId);
      }, this.reconnectTimeout);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners = [];
  }

  addMessageListener(listener: (message: WebSocketMessage) => void) {
    this.listeners.push(listener);
  }

  removeMessageListener(listener: (message: WebSocketMessage) => void) {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  private notifyListeners(message: WebSocketMessage) {
    this.listeners.forEach(listener => listener(message));
  }
}

export const websocketService = new WebSocketService();