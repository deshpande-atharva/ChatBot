import ChatInterface from './components/Chat/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="app">
      <div className="app-header">
        <h1>Bind IQ Insurance Onboarding</h1>
      </div>
      <div className="app-body">
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;