import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, User, Bot, Loader2 } from 'lucide-react';
import client from '../api/client';
import WelcomeCard from './WelcomeCard';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState(`session_${Date.now()}`);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (text) => {
        if (!text.trim() || isLoading) return;

        const userMessage = { role: 'user', content: text, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await client.post('/chat', {
                message: text,
                session_id: sessionId
            });

            const aiMessage = {
                role: 'ai',
                content: response.data.response,
                source: response.data.source,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            const errorMessage = {
                role: 'ai',
                content: "I'm having trouble connecting to the financial servers. Please try again later.",
                isError: true,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
            if (inputRef.current) inputRef.current.focus();
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend(input);
        }
    };

    return (
        <div className="flex-1 flex flex-col h-full relative overflow-hidden">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 pt-20 md:pt-24 pb-4 scroll-smooth" id="chatMessages">
                {messages.length === 0 ? (
                    <div className="max-w-5xl mx-auto h-full flex items-center justify-center">
                        <WelcomeCard onQuickQuestion={handleSend} />
                    </div>
                ) : (
                    <div className="max-w-5xl mx-auto space-y-6">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`flex flex-col animate-fadeIn ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                            >
                                <div className={`relative max-w-[85%] md:max-w-[80%] p-5 rounded-[24px] shadow-sm ${msg.role === 'user'
                                    ? 'bg-gradient-to-br from-[#4361ee] to-[#3a0ca3] text-white rounded-br-[4px]'
                                    : 'bg-white text-slate-700 rounded-bl-[4px] border border-slate-100 shadow-[0_2px_8px_rgba(0,0,0,0.04)]'
                                    }`}>
                                    <div className="text-[0.95rem] leading-relaxed">
                                        {msg.content}
                                    </div>
                                    {msg.source && (
                                        <div className="mt-2 pt-2 border-t border-white/20 text-xs opacity-80 flex items-center gap-1">
                                            <Sparkles size={12} /> Source: {msg.source}
                                        </div>
                                    )}
                                </div>
                                <span className="text-xs text-gray-400 mt-2 px-1">
                                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex items-start animate-fadeIn">
                                <div className="bg-white dark:bg-[#16213e] p-4 rounded-[18px] rounded-bl-[5px] shadow-[0_2px_5px_rgba(0,0,0,0.1)] flex items-center gap-2 border border-gray-100 dark:border-gray-700">
                                    <Loader2 className="animate-spin text-[#4361ee]" size={18} />
                                    <span className="text-gray-500 dark:text-gray-400 text-sm">Analyzing market data...</span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="w-full p-4 pb-6 md:pb-8 bg-gradient-to-t from-white/90 via-white/50 to-transparent z-20 relative">
                <div className="max-w-5xl mx-auto">
                    <div className="flex items-center bg-white/70 backdrop-blur-xl rounded-[24px] p-2 pl-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] w-[95%] md:w-[90%] mx-auto border border-white/60 transition-all hover:shadow-[0_12px_40px_rgba(0,0,0,0.12)] hover:bg-white/90">
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Ask detailed questions about finance..."
                            className="flex-1 bg-transparent border-none outline-none text-slate-800 placeholder:text-slate-400 py-3 text-base font-medium"
                            disabled={isLoading}
                        />
                        <button
                            onClick={() => handleSend(input)}
                            disabled={isLoading || !input.trim()}
                            aria-label="Send message"
                            title="Send message"
                            className="w-[52px] h-[52px] rounded-[18px] bg-[#4361ee] text-white flex items-center justify-center transition-all hover:bg-[#3a0ca3] hover:scale-105 shadow-lg shadow-blue-500/30 active:scale-95 ml-3 shrink-0"
                        >
                            <Send size={22} className={input.trim() ? 'translate-x-0.5' : ''} strokeWidth={2.5} />
                        </button>
                    </div>
                    <p className="text-center text-[0.8rem] opacity-70 mt-3 mb-0 text-[#2b2d42] dark:text-[#e6e6e6]">
                        AI may produce inaccurate information. Consult a financial expert.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
