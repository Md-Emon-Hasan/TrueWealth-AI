import React from 'react';
import { MessageSquare, Github, Linkedin, Facebook, Phone, Plus, X, Command, Mail } from 'lucide-react';
// import Logo from '../../assets/images/logo.png';

const Sidebar = ({ onNewChat, isOpen, onClose }) => {
    return (
        <div className={`w-[280px] md:w-[320px] h-screen bg-gradient-to-b from-[#4361ee] to-[#3a0ca3] text-white fixed left-0 top-0 z-50 flex flex-col shadow-2xl overflow-y-auto transition-transform duration-500 cubic-bezier(0.2, 0.8, 0.2, 1) ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>

            {/* Shine Overlay */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.15),transparent)] pointer-events-none z-0"></div>

            {/* Decorative Background Blobs */}
            <div className="absolute top-[-10%] left-[-10%] w-32 h-32 bg-purple-400/30 rounded-full blur-3xl pointer-events-none z-0"></div>
            <div className="absolute bottom-[10%] right-[-10%] w-40 h-40 bg-blue-400/20 rounded-full blur-3xl pointer-events-none z-0"></div>

            <button
                onClick={onClose}
                className="md:hidden absolute top-4 right-4 p-2 text-white/80 hover:text-white transition-colors z-20"
            >
                <X size={24} />
            </button>

            <div className="p-8 flex flex-col h-full relative z-10 font-sans">
                {/* Brand Section */}
                <div className="text-center mb-12 mt-8 md:mt-0">
                    <div className="w-20 h-20 mx-auto mb-6 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center shadow-inner border border-white/30">
                        <span className="text-3xl font-bold tracking-tighter">TW</span>
                    </div>

                    <h1 className="text-2xl font-bold tracking-tight mb-1">TrueWealth AI</h1>
                    <p className="text-xs font-light text-blue-200 uppercase tracking-widest">Financial Strategist</p>
                </div>

                {/* Bottom Section: Developer Info & New Chat */}
                <div className="mt-auto">
                    {/* Developer / Info Section */}
                    <div className="bg-white/10 p-6 rounded-2xl mb-6 backdrop-blur-sm border border-white/10 transition-transform hover:scale-[1.02] duration-300">
                        <p className="text-xs font-semibold text-blue-200 uppercase tracking-wider mb-4">Developer</p>

                        <div className="flex items-center gap-3 mb-4">
                            <div className="w-10 h-10 rounded-full bg-blue-500/30 flex items-center justify-center text-sm font-bold border border-white/20">MH</div>
                            <div>
                                <p className="font-medium text-sm">Md. Emon Hasan</p>
                                <p className="text-xs text-blue-200">Dhaka, Bangladesh</p>
                            </div>
                        </div>

                        <div className="flex gap-4 mt-6 justify-between px-2">
                            <a href="mailto:emon.mlengineer@gmail.com" className="text-white/70 hover:text-white transition-all hover:scale-110"><Mail size={18} /></a>
                            <a href="https://wa.me/8801834363533" target="_blank" rel="noreferrer" className="text-white/70 hover:text-white transition-all hover:scale-110"><Phone size={18} /></a>
                            <a href="https://github.com/Md-Emon-Hasan" target="_blank" rel="noreferrer" className="text-white/70 hover:text-white transition-all hover:scale-110"><Github size={18} /></a>
                            <a href="https://www.linkedin.com/in/md-emon-hasan-695483237/" target="_blank" rel="noreferrer" className="text-white/70 hover:text-white transition-all hover:scale-110"><Linkedin size={18} /></a>
                            <a href="https://www.facebook.com/mdemon.hasan2001/" target="_blank" rel="noreferrer" className="text-white/70 hover:text-white transition-all hover:scale-110"><Facebook size={18} /></a>
                        </div>
                    </div>

                    {/* New Chat Button */}
                    <div className="pb-4">
                        <button
                            onClick={onNewChat}
                            className="group w-full bg-white text-[#4361ee] py-4 px-6 rounded-2xl font-bold shadow-lg shadow-black/10 transition-all hover:shadow-xl hover:-translate-y-1 flex items-center justify-center gap-3"
                        >
                            <Plus size={20} strokeWidth={3} className="group-hover:rotate-90 transition-transform duration-300" />
                            <span>New Chat</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
