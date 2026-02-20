import React from 'react';
import { TrendingUp, Coins, PiggyBank, ArrowUpRight, Umbrella, Lightbulb, FileText, Handshake } from 'lucide-react';
import Logo from '../assets/logo.png';

const WelcomeCard = ({ onQuickQuestion }) => {
    const features = [
        { icon: TrendingUp, text: "Portfolio Analysis", color: "text-blue-500", bg: "bg-blue-50" },
        { icon: Coins, text: "Investment Tips", color: "text-purple-500", bg: "bg-purple-50" },
        { icon: PiggyBank, text: "Savings Strategies", color: "text-pink-500", bg: "bg-pink-50" }
    ];

    const quickQuestions = [
        { icon: ArrowUpRight, text: "Market Trends", question: "What's the current stock market trend?" },
        { icon: Umbrella, text: "Retirement Plan", question: "How should I plan for retirement?" },
        { icon: Lightbulb, text: "Beginner Tips", question: "What are good investments for beginners?" },
        { icon: FileText, text: "Tax Strategy", question: "How to optimize my tax strategy?" }
    ];

    return (
        <div className="flex-1 flex items-center justify-center p-6 animate-fadeIn">
            {/* Glassmorphism Card */}
            <div className="bg-white/80 backdrop-blur-xl rounded-[32px] p-8 md:p-12 w-full max-w-[950px] shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/50 text-center relative overflow-hidden">

                {/* Decorative top sheen */}
                <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 opacity-80"></div>

                <div className="mb-8 md:mb-10 px-2">
                    <h2 className="text-3xl md:text-5xl font-extrabold mb-3 md:mb-4 bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-600 tracking-tight flex flex-col items-center justify-center gap-3 md:gap-4">
                        <img src={Logo} alt="TrueWealth AI Logo" className="w-20 h-20 md:w-24 md:h-24 object-contain mb-4 drop-shadow-md" />
                        <span className="text-slate-800 leading-tight">Welcome to TrueWealth AI</span>
                    </h2>
                    <p className="text-lg md:text-xl text-slate-500 font-medium px-4">
                        Your intelligent partner for financial freedom
                    </p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 mb-8 md:mb-12 px-2 md:px-4">
                    {features.map((feature, index) => (
                        <div key={index} className={`${feature.bg} p-5 md:p-6 rounded-3xl border border-white transition-all duration-300 hover:-translate-y-2 hover:shadow-lg cursor-pointer group flex flex-col items-center justify-center h-[160px] md:h-[180px]`}>
                            <div className={`w-14 h-14 md:w-16 md:h-16 rounded-2xl ${feature.bg} brightness-95 flex items-center justify-center mb-3 md:mb-4 group-hover:scale-110 transition-transform`}>
                                <feature.icon className={`w-6 h-6 md:w-8 md:h-8 ${feature.color}`} />
                            </div>
                            <p className="font-bold text-slate-700 text-base md:text-lg group-hover:text-primary transition-colors">{feature.text}</p>
                        </div>
                    ))}
                </div>

                <div className="flex flex-wrap justify-center gap-3">
                    {quickQuestions.map((item, index) => (
                        <button
                            key={index}
                            onClick={() => onQuickQuestion(item.question)}
                            className="bg-white border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 rounded-full px-6 py-3 flex items-center gap-3 cursor-pointer transition-all duration-200 text-sm font-semibold text-slate-600 hover:text-blue-600 shadow-sm hover:shadow-md group"
                        >
                            <div className="w-8 h-8 rounded-full bg-slate-100 group-hover:bg-blue-100 flex items-center justify-center transition-colors">
                                <item.icon size={14} className="text-slate-500 group-hover:text-blue-600" />
                            </div>
                            <span>{item.text}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default WelcomeCard;
