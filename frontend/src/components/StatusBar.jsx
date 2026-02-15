import React from 'react';
import { Wifi } from 'lucide-react';

const StatusBar = () => {
    return (
        <div className="fixed top-0 left-0 md:left-[300px] right-0 h-16 bg-white/80 dark:bg-card-dark/80 backdrop-blur-md flex items-center justify-between px-8 z-40 border-b border-gray-200 dark:border-white/5 shadow-sm transition-all">
            <div className="flex items-center gap-3">
                <div className="w-2.5 h-2.5 bg-success rounded-full animate-pulse shadow-[0_0_10px_theme('colors.success')]"></div>
                <span className="font-semibold text-dark dark:text-light tracking-wide">TrueWealth AI</span>
            </div>

            <div className="flex items-center gap-2 text-success text-sm font-medium bg-success/10 px-3 py-1.5 rounded-full border border-success/20">
                <Wifi size={14} />
                <span>System Online</span>
            </div>
        </div>
    );
};

export default StatusBar;
