import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  ChatRequest,
  ChatResponse,
  HistoryResponse,
  SessionsResponse,
} from '../types';

const API_BASE = '/api';

class ApiService {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await this.request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(response.access_token);
    return response;
  }

  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await this.request<TokenResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(response.access_token);
    return response;
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  logout() {
    this.setToken(null);
  }

  // Chat endpoints
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async *streamMessage(data: ChatRequest): AsyncGenerator<string, void, unknown> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            return;
          }
          yield data;
        }
      }
    }
  }

  async getChatHistory(sessionId: string): Promise<HistoryResponse> {
    return this.request<HistoryResponse>(`/chat/history/${sessionId}`);
  }

  async clearChatHistory(sessionId: string): Promise<void> {
    await this.request<{ message: string }>(`/chat/history/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async getSessions(): Promise<SessionsResponse> {
    return this.request<SessionsResponse>('/chat/sessions');
  }
}

export const api = new ApiService();
