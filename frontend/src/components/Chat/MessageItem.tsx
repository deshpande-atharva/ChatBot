import type { Message } from '../../types';
import './MessageItem.css';

interface MessageItemProps {
  message: Message;
}

const MessageItem = ({ message }: MessageItemProps) => {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <div className={`message-item ${message.sender}`}>
      <div className="message-bubble">
        <p className="message-content">{message.content}</p>
        <span className="message-time">{formatTime(message.created_at)}</span>
      </div>
    </div>
  );
};

export default MessageItem;