import { useState } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import './InputForm.css';

interface InputFormProps {
  onSendMessage: (message: string) => void;
  disabled: boolean;
  placeholder?: string;
}

const InputForm = ({ onSendMessage, disabled, placeholder }: InputFormProps) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        disabled={disabled}
        placeholder={placeholder || 'Type your message...'}
        className="input-field"
        autoFocus
      />
      <button 
        type="submit" 
        disabled={disabled || !input.trim()}
        className="send-button"
      >
        Send
      </button>
    </form>
  );
};

export default InputForm;