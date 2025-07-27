import type { Message } from '../../types';
import MessageItem from './MessageItem';
import TypingIndicator from './TypingIndicator';
import './MessageList.css';

interface MessageListProps {
  messages: Message[];
  isTyping: boolean;
}

const MessageList = ({ messages, isTyping }: MessageListProps) => {
  return (
    <div className="message-list">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      {isTyping && <TypingIndicator />}
    </div>
  );
};

export default MessageList;