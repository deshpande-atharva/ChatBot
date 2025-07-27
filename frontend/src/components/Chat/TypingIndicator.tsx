import './TypingIndicator.css';

const TypingIndicator = () => {
  return (
    <div className="typing-indicator">
      <div className="typing-bubble">
        <div className="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;