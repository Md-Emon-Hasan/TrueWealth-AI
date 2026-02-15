import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import StatusBar from './components/StatusBar';
import ChatInterface from './components/ChatInterface';

function App() {
  const [messages, setMessages] = useState([]);

  const handleNewChat = () => {
    // Logic to reset chat state will be handled inside ChatInterface 
    // or by lifting state up if needed. For now, we'll reload to keep it simple
    // or assume ChatInterface handles it.
    window.location.reload();
  };

  return (
    <div className="flex h-screen bg-bg-light dark:bg-bg-dark font-sans overflow-hidden relative">
      {/* Background Circles */}
      <div className="bg-circles">
        <div className="circle-1 top-[-100px] right-[-100px] w-[500px] h-[500px] bg-primary/20"></div>
        <div className="circle-2 bottom-[-150px] left-[-150px] w-[600px] h-[600px] bg-secondary/20"></div>
        <div className="circle-3 top-1/2 left-1/3 w-[300px] h-[300px] bg-warning/10"></div>
      </div>

      <Sidebar onNewChat={handleNewChat} />

      <main className="flex-1 flex flex-col md:ml-[300px] relative">
        <StatusBar />
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;
