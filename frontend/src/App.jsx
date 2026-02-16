import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import StatusBar from './components/StatusBar';
import { Menu } from 'lucide-react';

function App() {
  const [chatKey, setChatKey] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const startNewChat = () => {
    setChatKey(prev => prev + 1);
    setIsSidebarOpen(false); // Close sidebar on mobile when new chat starts
  };

  return (
    <div className="flex h-screen font-sans overflow-hidden">
      {/* Background Mesh Gradient */}
      <div className="bg-circles">
        <div className="circle-1"></div>
        <div className="circle-2"></div>
        <div className="circle-3"></div>
        <div className="circle-4"></div>
      </div>

      {/* Mobile Menu Button - Floating Glass */}
      <button
        onClick={() => setIsSidebarOpen(true)}
        className="md:hidden fixed top-4 left-4 z-40 p-3 bg-white/70 backdrop-blur-md rounded-xl shadow-lg text-slate-700 hover:text-primary transition-all active:scale-95 border border-white/50"
      >
        <Menu size={24} />
      </button>

      {/* Sidebar with Responsive Props */}
      <Sidebar
        onNewChat={startNewChat}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/20 z-40 md:hidden backdrop-blur-sm transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        ></div>
      )}

      <div className="flex-1 flex flex-col relative z-0 md:ml-[320px] transition-all duration-500">
        {/* Helper div to push content down on mobile if needed, or StatusBar handles it */}
        <StatusBar />
        <ChatInterface key={chatKey} />
      </div>
    </div>
  );
}

export default App;
