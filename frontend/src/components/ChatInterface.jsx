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

    useEffect(() => {
        // Check if we have a saved session (optional in future)
    }, []);

    const handleSend = async (text) => {
        if (!text.trim() || isLoading) return;

        const userMessage = { role: 'user', content: text, timestamp: new Date() };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // Optimistic update for UI responsiveness
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
            inputRef.current?.focus();
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend(input);
        }
    };

    const startNewChat = () => {
        setMessages([]);
        setSessionId(`session_${Date.now()}`);
    };

    return (
        <div className="flex-1 flex flex-col h-full relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px]"></div>
                <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-secondary/5 rounded-full blur-[100px]"></div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 md:p-8 pt-24 pb-32 scroll-smooth">
                {messages.length === 0 ? (
                    <WelcomeCard onQuickQuestion={handleSend} />
                ) : (
                    <div className="max-w-4xl mx-auto space-y-8">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`flex gap-4 animate-fadeIn ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                            >
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg ${msg.role === 'user'
                                        ? 'bg-gradient-to-br from-primary to-secondary text-white'
                                        : 'bg-white dark:bg-card-dark text-primary border border-gray-100 dark:border-white/10'
                                    }`}>
                                    {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                                </div>

                                <div className={`flex flex-col max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                    <div className={`p-5 rounded-2xl shadow-sm text-[0.95rem] leading-relaxed ${msg.role === 'user'
                                            ? 'bg-primary text-white rounded-tr-none'
                                            : 'bg-white dark:bg-card-dark text-dark dark:text-light rounded-tl-none border border-gray-100 dark:border-white/5 shadow-md'
                                        }`}>
                                        {msg.content}
                                        {msg.source && (
                                            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-white/10 text-xs opacity-70 italic flex items-center gap-1">
                                                <Sparkles size={12} /> Source: {msg.source}
                                            </div>
                                        )}
                                    </div>
                                    <span className="text-xs text-gray-400 mt-2 px-1">
                                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex gap-4 animate-fadeIn">
                                <div className="w-10 h-10 rounded-full bg-white dark:bg-card-dark text-primary border border-gray-100 dark:border-white/10 flex items-center justify-center shrink-0 shadow-lg">
                                    <Bot size={20} />
                                </div>
                                <div className="bg-white dark:bg-card-dark p-6 rounded-2xl rounded-tl-none border border-gray-100 dark:border-white/5 shadow-md flex items-center gap-3">
                                    <Loader2 className="animate-spin text-primary" size={20} />
                                    <span className="text-gray-500 text-sm font-medium">Analyzing market data...</span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            <div className="fixed bottom-0 left-0 md:left-[300px] right-0 p-6 bg-gradient-to-t from-white via-white/80 to-transparent dark:from-bg-dark dark:via-bg-dark/80 z-20">
                <div className="max-w-4xl mx-auto relative group">
                    <div className="absolute inset-0 bg-gradient-to-r from-primary via-secondary to-primary opacity-20 group-hover:opacity-30 blur-xl rounded-full transition-opacity duration-300"></div>
                    <div className="relative flex items-center gap-2 bg-white dark:bg-card-dark/80 backdrop-blur-xl border border-gray-200 dark:border-white/10 rounded-full p-2 pr-2 pl-6 shadow-2xl transition-all duration-300 focus-within:border-primary/50 focus-within:shadow-[0_0_20px_rgba(67,97,238,0.2)]">
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Ask about stocks, savings, or retirement..."
                            className="flex-1 bg-transparent border-none outline-none text-dark dark:text-light placeholder:text-gray-400 py-3"
                            disabled={isLoading}
                        />
                        <button
                            onClick={() => handleSend(input)}
                            disabled={isLoading || !input.trim()}
                            className={`w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300 ${input.trim()
                                    ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg hover:shadow-primary/40 hover:scale-105 active:scale-95'
                                    : 'bg-gray-100 dark:bg-white/5 text-gray-400 cursor-not-allowed'
                                }`}
                        >
                            {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} className={input.trim() ? 'ml-0.5' : ''} />}
                        </button>
                    </div>
                    <p className="text-center text-xs text-gray-400 mt-3 font-medium">
                        AI may produce inaccurate information. Consult a financial expert.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ChatInterface;
