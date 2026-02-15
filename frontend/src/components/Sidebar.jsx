import React from 'react';
import { MessageSquare, Github, Linkedin, Facebook, Phone } from 'lucide-react';
// import Logo from '../../assets/images/logo.png'; // We need to move the logo later

const Sidebar = ({ onNewChat }) => {
    return (
        <div className="w-[300px] h-screen bg-gradient-to-br from-card-dark to-input-dark text-white fixed left-0 top-0 z-50 flex flex-col shadow-2xl overflow-y-auto border-r border-white/10">
            <div className="p-8 flex flex-col h-full">
                <div className="text-center mb-8">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-full border-[3px] border-white/20 overflow-hidden bg-primary/20 flex items-center justify-center">
                        {/* Fallback if image missing */}
                        <span className="text-2xl font-bold">TW</span>
                        {/* <img src={Logo} alt="Logo" className="w-full h-full object-cover" /> */}
                    </div>
                    <h1 className="text-2xl font-bold mb-2 tracking-wide">TrueWealth AI</h1>
                    <p className="text-sm opacity-70">Version 2.0</p>
                </div>

                <div className="bg-white/5 p-6 rounded-2xl mb-8 backdrop-blur-sm border border-white/5">
                    <h3 className="text-lg font-semibold mb-4 border-b border-white/10 pb-2">Developer</h3>
                    <p className="mb-4">Md. Emon Hasan</p>
                    <div className="flex gap-4 mb-4">
                        <a href="https://wa.me/8801834363533" target="_blank" rel="noreferrer" className="hover:text-accent hover:-translate-y-1 transition-all"><Phone size={20} /></a>
                        <a href="https://github.com/Md-Emon-Hasan" target="_blank" rel="noreferrer" className="hover:text-accent hover:-translate-y-1 transition-all"><Github size={20} /></a>
                        <a href="https://www.linkedin.com/in/md-emon-hasan-695483237/" target="_blank" rel="noreferrer" className="hover:text-accent hover:-translate-y-1 transition-all"><Linkedin size={20} /></a>
                        <a href="https://www.facebook.com/mdemon.hasan2001/" target="_blank" rel="noreferrer" className="hover:text-accent hover:-translate-y-1 transition-all"><Facebook size={20} /></a>
                    </div>
                    <p className="text-sm opacity-70">Dhaka, Bangladesh</p>
                </div>

                <div className="mt-auto">
                    <button
                        onClick={onNewChat}
                        className="w-full bg-white/10 hover:bg-white/20 text-white p-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 backdrop-blur-sm border border-white/10 group"
                    >
                        <MessageSquare size={18} className="group-hover:scale-110 transition-transform" /> New Chat
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
