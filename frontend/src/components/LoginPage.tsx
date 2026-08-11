import React, { useState } from 'react';
import { Flame, User, Lock, Database, ArrowRight, CheckCircle2, Key, Home } from 'lucide-react';

interface LoginPageProps {
  onLogin: (username: string, mode: 'demo' | 'live') => void;
  onGoHome: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin, onGoHome }) => {
  const [username, setUsername] = useState('data.engineer@company.com');
  const [password, setPassword] = useState('••••••••••••');
  const [mode, setMode] = useState<'demo' | 'live'>('demo');
  const [token, setToken] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setTimeout(() => {
      onLogin(username, mode);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans comic-dots">
      {/* Top Left Home Button */}
      <button
        onClick={onGoHome}
        className="fixed top-6 left-6 px-4 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-yellow-400 font-mono font-bold text-xs border-3 border-black shadow-pop flex items-center gap-2 z-50"
      >
        <Home className="h-4 w-4" />
        <span>Back to Landing Page</span>
      </button>

      <div className="w-full max-w-md relative z-10 my-12">
        {/* Header Branding */}
        <div className="text-center mb-8 space-y-3">
          <div className="inline-flex items-center justify-center p-4 rounded-2xl bg-yellow-400 border-4 border-black shadow-pop-red comic-sticker">
            <Flame className="h-10 w-10 text-black" />
          </div>

          <div>
            <h1 className="font-comic text-4xl tracking-wider text-yellow-400 drop-shadow-[3px_3px_0px_#000]">
              GOVERNANCE STUDIO LOGIN
            </h1>
            <p className="text-xs font-mono text-slate-300 tracking-wider uppercase mt-1">
              DataHub Metadata Contract Protocol
            </p>
          </div>
        </div>

        {/* Login Form Card */}
        <div className="bg-zinc-900 rounded-3xl p-8 border-4 border-black shadow-pop-yellow relative">
          <div className="flex items-center justify-between border-b-2 border-black pb-4 mb-6">
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-cyan-400" />
              <span className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
                Authentication Gate
              </span>
            </div>
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-red-600 text-white border-2 border-black">
              STRICT AST
            </span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Identity / Username */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300 flex items-center justify-between">
                <span>User Identifier</span>
                <span className="text-[10px] text-yellow-400 font-bold">REQUIRED</span>
              </label>
              <div className="relative">
                <User className="h-4 w-4 text-yellow-400 absolute left-3.5 top-3.5" />
                <input
                  type="email"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-black border-2 border-black focus:border-yellow-400 rounded-xl py-2.5 pl-10 pr-4 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none shadow-inner"
                  placeholder="user@company.com"
                />
              </div>
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-xs font-mono text-slate-300 flex items-center justify-between">
                <span>Access Passcode</span>
                <span className="text-[10px] text-yellow-400 font-bold">ENCRYPTED</span>
              </label>
              <div className="relative">
                <Lock className="h-4 w-4 text-yellow-400 absolute left-3.5 top-3.5" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-black border-2 border-black focus:border-yellow-400 rounded-xl py-2.5 pl-10 pr-4 text-xs font-mono text-slate-100 placeholder-slate-600 focus:outline-none shadow-inner"
                />
              </div>
            </div>

            {/* Catalog Mode Selection */}
            <div className="space-y-2 pt-2">
              <label className="text-xs font-mono text-slate-300 block">
                DataHub Environment Mode
              </label>

              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setMode('demo')}
                  className={`p-3 rounded-xl border-2 text-left flex items-start gap-2.5 transition-all ${
                    mode === 'demo'
                      ? 'bg-yellow-400 text-black border-black shadow-pop font-bold'
                      : 'bg-black text-slate-400 border-black hover:border-zinc-700'
                  }`}
                >
                  <Database className={`h-4 w-4 mt-0.5 shrink-0 ${mode === 'demo' ? 'text-black' : 'text-slate-500'}`} />
                  <div>
                    <span className="font-mono text-xs font-bold block">Demo Mode</span>
                    <span className="text-[10px] opacity-80 leading-tight block">
                      Local Catalog Fixtures
                    </span>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setMode('live')}
                  className={`p-3 rounded-xl border-2 text-left flex items-start gap-2.5 transition-all ${
                    mode === 'live'
                      ? 'bg-yellow-400 text-black border-black shadow-pop font-bold'
                      : 'bg-black text-slate-400 border-black hover:border-zinc-700'
                  }`}
                >
                  <Key className={`h-4 w-4 mt-0.5 shrink-0 ${mode === 'live' ? 'text-black' : 'text-slate-500'}`} />
                  <div>
                    <span className="font-mono text-xs font-bold block">DataHub Live</span>
                    <span className="text-[10px] opacity-80 leading-tight block">
                      REST API Server
                    </span>
                  </div>
                </button>
              </div>
            </div>

            {/* Live Token Input if live mode chosen */}
            {mode === 'live' && (
              <div className="space-y-1.5 animate-fadeIn">
                <label className="text-xs font-mono text-cyan-300 flex items-center justify-between">
                  <span>DataHub Bearer Token</span>
                </label>
                <input
                  type="text"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="w-full bg-black border-2 border-black rounded-xl py-2.5 px-3.5 text-xs font-mono text-cyan-300 placeholder-zinc-700 focus:outline-none focus:border-cyan-400"
                  placeholder="eyJhbGciOiJIUzI1Ni..."
                />
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3.5 px-4 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-black font-mono font-extrabold text-xs uppercase tracking-wider border-3 border-black shadow-pop-red hover:shadow-pop-lg transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <span className="h-4 w-4 rounded-full border-2 border-black border-t-transparent animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <span>Enter Governance Studio</span>
                  <ArrowRight className="h-4 w-4 stroke-[3] group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Footer Security Badge */}
          <div className="mt-6 pt-4 border-t-2 border-black flex items-center justify-between text-[10px] text-slate-400 font-mono">
            <span className="flex items-center gap-1 text-cyan-300 font-bold">
              <CheckCircle2 className="h-3 w-3 text-cyan-400" />
              AST Symbol Contract Enforced
            </span>
            <span>DataHub Source of Truth</span>
          </div>
        </div>
      </div>
    </div>
  );
};
