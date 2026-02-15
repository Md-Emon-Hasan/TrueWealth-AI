import React from 'react';
import { TrendingUp, Coins, PiggyBank, ArrowUpRight, Umbrella, Lightbulb, FileText, Zap } from 'lucide-react';

const WelcomeCard = ({ onQuickQuestion }) => {
    const features = [
        { icon: TrendingUp, text: "Portfolio Analysis" },
        { icon: Coins, text: "Investment Tips" },
        { icon: PiggyBank, text: "Savings Strategies" }
    ];

    const quickQuestions = [
        { icon: ArrowUpRight, text: "Market Trends", question: "What's the current stock market trend?" },
        { icon: Umbrella, text: "Retirement Plan", question: "How should I plan for retirement?" },
        { icon: Lightbulb, text: "Beginner Tips", question: "What are good investments for beginners?" },
        { icon: FileText, text: "Tax Strategy", question: "How to optimize my tax strategy?" }
    ];

    return (
        <div className="flex-1 flex items-center justify-center p-4 md:p-8 animate-fadeIn">
            <div className="bg-white dark:bg-card-dark rounded-[2.5rem] p-8 md:p-12 w-full max-w-4xl shadow-2xl border border-gray-100 dark:border-white/5 text-center relative overflow-hidden backdrop-blur-xl">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary via-secondary to-warning"></div>

                <div className="mb-8">
                    <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Zap className="w-10 h-10 text-primary" />
                    </div>
                    <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent pb-2">
                        Welcome to TrueWealth AI
                    </h2>
                    <p className="text-gray-500 dark:text-gray-400 text-lg md:text-xl max-w-2xl mx-auto leading-relaxed">
                        Your personal AI financial strategist. Determine your path to financial freedom with data-driven insights.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12 max-w-3xl mx-auto">
                    {features.map((feature, index) => (
                        <div key={index} className="group bg-primary/5 dark:bg-white/5 p-6 rounded-2xl hover:-translate-y-2 transition-all duration-300 border border-transparent hover:border-primary/20 hover:shadow-lg cursor-default">
                            <feature.icon className="w-10 h-10 text-primary mb-4 mx-auto group-hover:scale-110 transition-transform duration-300" />
                            <p className="font-semibold text-dark dark:text-light">{feature.text}</p>
                        </div>
                    ))}
                </div>

                <div className="flex flex-wrap justify-center gap-4">
                    {quickQuestions.map((item, index) => (
                        <button
                            key={index}
                            onClick={() => onQuickQuestion(item.question)}
                            className="flex items-center gap-3 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 px-6 py-3 rounded-full hover:bg-primary hover:text-white dark:hover:bg-primary dark:hover:border-primary hover:shadow-lg hover:shadow-primary/30 transition-all duration-300 group"
                        >
                            <item.icon size={18} className="text-primary group-hover:text-white transition-colors" />
                            <span className="font-medium">{item.text}</span>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default WelcomeCard;
