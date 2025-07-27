import axios from 'axios';
import type { AxiosInstance } from 'axios';
import type { Session, Message, ChatRequest, ChatResponse } from '../types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request/response interceptors for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // Session endpoints
  async createSession(): Promise<Session> {
    const response = await this.client.post<Session>('/api/sessions');
    return response.data;
  }

  async getSession(sessionId: string): Promise<Session> {
    const response = await this.client.get<Session>(`/api/sessions/${sessionId}`);
    return response.data;
  }

  // Message endpoints
  async sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/api/messages', {
      session_id: sessionId,
      message,
    } as ChatRequest);
    return response.data;
  }

  async getMessages(sessionId: string): Promise<Message[]> {
    const response = await this.client.get<Message[]>(`/api/messages/${sessionId}`);
    return response.data;
  }
}

export const api = new ApiService();