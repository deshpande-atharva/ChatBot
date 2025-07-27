// Session types
export interface Session {
  id: string;
  status: 'active' | 'completed';
  current_step: string;
  created_at: string;
  data?: Record<string, any>;
}

// Message types
export interface Message {
  id: string;
  session_id: string;
  sender: 'user' | 'bot';
  content: string;
  created_at: string;
}

// API Request/Response types
export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  message: string;
  current_step: string;
  session_status: 'active' | 'completed';
}

// WebSocket message type
export interface WebSocketMessage {
  type: 'message';
  message: Message;
}

// Component props types
export interface ChatInterfaceProps {
  sessionId?: string;
}

export interface MessageListProps {
  messages: Message[];
  isTyping: boolean;
}

export interface MessageItemProps {
  message: Message;
}

export interface InputFormProps {
  onSendMessage: (message: string) => void;
  disabled: boolean;
  placeholder?: string;
}