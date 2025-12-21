// User types
export interface User {
  id: string;
  email: string;
  is_active: boolean;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Chat types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
}

export interface HistoryResponse {
  session_id: string;
  messages: Message[];
}

// Session types
export interface Session {
  id: string;
  title: string | null;
}

export interface SessionsResponse {
  sessions: Session[];
}

// API Error
export interface ApiError {
  detail: string;
}
