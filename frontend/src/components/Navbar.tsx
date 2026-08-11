import React from 'react';
import { Database, ShieldCheck, Flame, LogOut, User, Home, Sparkles } from 'lucide-react';

interface NavbarProps {
  demoMode?: boolean;
  username: string;
  onLogout: () => void;
  onGoHome: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  demoMode = true,
  username,
  onLogout,
  onGoHome,
}) => {
  return (
    <header className="h-20 border-b-4 border-black bg-zinc-950/95 backdrop-blur-md sticky top-0 z-50 flex items-center justify-between px-6 shadow-pop">
      {/* Brand logo & tagline */}
      <div className="flex items-center gap-3">
        <button
          onClick={onGoHome}
          className="h-11 w-11 rounded-xl bg-yellow-400 border-3 border-black flex items-center justify-center shadow-[3px_3px_0px_#000] hover:scale-105 transition-transform"
          title="Return to Home Landing Page"
        >
          <Flame className="h-6 w-6 text-black" />
        </button>

        <div>
          <div className="flex items-center gap-2">
            <button onClick={onGoHome} className="font-comic text-2xl tracking-wider text-yellow-400 drop-shadow-[2px_2px_0px_#000] text-left hover:text-yellow-300">
              FORGEHUB AI
            </button>
            <span className="font-mono text-[10px] font-extrabold px-2 py-0.5 rounded bg-red-600 text-white border-2 border-black uppercase shadow-[2px_2px_0px_#000]">
              GOVERNANCE STUDIO
            </span>
          </div>
          <p className="text-xs text-slate-300 font-mono font-semibold hidden sm:block">
            DataHub Contract Engine
          </p>
        </div>
      </div>

      {/* Center metadata contract badge */}
      <div className="hidden lg:flex items-center gap-2 px-4 py-1.5 rounded-full bg-zinc-900 border-2 border-black text-xs font-mono text-slate-200 shadow-pop">
        <ShieldCheck className="h-4 w-4 text-cyan-400" />
        <span>Metadata Rules: <strong className="text-yellow-400 font-bold uppercase tracking-wider">STRICT AST CONTRACT</strong></span>
      </div>

      {/* Right side indicators */}
      <div className="flex items-center gap-3">
        {/* Go Home button */}
        <button
          onClick={onGoHome}
          className="px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-slate-200 font-mono text-xs font-bold border-2 border-black shadow-[2px_2px_0px_#000] transition-all flex items-center gap-1.5"
          title="View Product Landing Page"
        >
          <Home className="h-3.5 w-3.5 text-yellow-400" />
          <span className="hidden sm:inline">Landing Page</span>
        </button>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900 border-2 border-black text-xs font-mono text-slate-300 shadow-[2px_2px_0px_#000]">
          <Database className="h-3.5 w-3.5 text-yellow-400" />
          <span className="hidden sm:inline">DataHub</span>
          <span className="inline-flex items-center gap-1.5 text-[11px] text-cyan-400 font-bold pl-1">
            <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
            {demoMode ? 'Demo Fixtures' : 'Connected'}
          </span>
        </div>

        {/* User profile & Logout */}
        <div className="flex items-center gap-2 pl-2 border-l-2 border-zinc-800">
          <button
            onClick={onLogout}
            className="p-2 rounded-xl bg-red-600 hover:bg-red-500 text-white border-2 border-black shadow-[2px_2px_0px_#000] transition-all flex items-center gap-1 text-xs font-mono font-bold"
            title="Log Out"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};
