import { useEffect, useRef } from 'react';
import { useChat } from '../../hooks/useChat';
import MessageList from './MessageList';
import InputForm from './InputForm';
import './ChatInterface.css';

const ChatInterface = () => {
  const {
    session,
    messages,
    isLoading,
    isTyping,
    error,
    initializeSession,
    sendMessage,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initializeSession();
  }, [initializeSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getProgressPercentage = (): number => {
    if (!session) return 0;
    
    const steps = [
      'zip_code', 'full_name', 'email', 'vehicle_info', 
      'vehicle_use', 'blind_spot', 'license_type', 'license_status'
    ];
    
    const currentIndex = steps.indexOf(session.current_step);
    if (currentIndex === -1) return 0;
    
    return Math.round(((currentIndex + 1) / steps.length) * 100);
  };

  if (isLoading && messages.length === 0) {
    return (
      <div className="chat-interface">
        <div className="chat-loading">
          <div className="spinner"></div>
          <p>Initializing chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-interface">
      {session && session.status === 'active' && (
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${getProgressPercentage()}%` }}
          />
          <span className="progress-text">{getProgressPercentage()}% Complete</span>
        </div>
      )}

      <div className="chat-messages">
        <MessageList messages={messages} isTyping={isTyping} />
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="chat-input">
        <InputForm
          onSendMessage={sendMessage}
          disabled={!session || session.status === 'completed' || isLoading}
          placeholder={
            session?.status === 'completed' 
              ? 'Onboarding completed!' 
              : 'Type your message...'
          }
        />
      </div>

      {session?.status === 'completed' && (
        <div className="completion-banner">
          <p>🎉 Thank you for completing the onboarding!</p>
          <button onClick={() => window.location.reload()}>Start New Session</button>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;