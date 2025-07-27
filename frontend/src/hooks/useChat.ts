import { useState, useEffect, useCallback } from 'react';
import type { Session, Message } from '../types';
import { api } from '../services/api';
import { websocketService } from '../services/websocket';

export const useChat = () => {
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize session
  const initializeSession = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Create new session
      const newSession = await api.createSession();
      setSession(newSession);
      
      // Connect WebSocket
      websocketService.connect(newSession.id);
      
      // Load initial messages
      const initialMessages = await api.getMessages(newSession.id);
      setMessages(initialMessages);
      
      // Set up WebSocket listener
      const handleWebSocketMessage = (wsMessage: any) => {
        if (wsMessage.type === 'message') {
          setMessages(prev => {
            // Check if message already exists (prevent duplicates)
            const exists = prev.some(msg => msg.id === wsMessage.message.id);
            if (exists) return prev;
            
            return [...prev, wsMessage.message];
          });
          
          // Stop typing indicator when bot message arrives
          if (wsMessage.message.sender === 'bot') {
            setIsTyping(false);
          }
        }
      };
      
      websocketService.addMessageListener(handleWebSocketMessage);
      
      return () => {
        websocketService.removeMessageListener(handleWebSocketMessage);
      };
    } catch (err) {
      setError('Failed to initialize chat session');
      console.error('Session initialization error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Send message
  const sendMessage = useCallback(async (message: string) => {
    if (!session || !message.trim()) return;

    try {
      setIsTyping(true);
      setError(null);
      
      // Send message to API
      const response = await api.sendMessage(session.id, message);
      
      // Update session status if changed
      if (response.session_status !== session.status) {
        setSession(prev => prev ? { ...prev, status: response.session_status } : null);
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Send message error:', err);
      setIsTyping(false);
    }
  }, [session]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      websocketService.disconnect();
    };
  }, []);

  return {
    session,
    messages,
    isLoading,
    isTyping,
    error,
    initializeSession,
    sendMessage,
  };
};