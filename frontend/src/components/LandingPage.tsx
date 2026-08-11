import React, { useState } from 'react';
import { Flame, ShieldAlert, Sparkles, Database, CheckCircle2, ArrowRight, Zap, RefreshCw, Cpu, Layers, Award, Terminal } from 'lucide-react';

interface LandingPageProps {
  onStart: () => void;
  onSelectDataset: (datasetId: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStart, onSelectDataset }) => {
  const [activeTab, setActiveTab] = useState<'orders' | 'customers' | 'revenue'>('orders');

  return (
    <div className="min-h-screen bg-zinc-950 text-slate-100 font-sans comic-dots selection:bg-yellow-400 selection:text-black">
      {/* Top Banner / Navbar */}
      <nav className="h-20 border-b-4 border-black bg-zinc-900/90 backdrop-blur-md sticky top-0 z-50 flex items-center justify-between px-6 shadow-pop">
        <div className="flex items-center gap-3">
          <div className="h-11 w-11 rounded-xl bg-yellow-400 border-3 border-black flex items-center justify-center shadow-[3px_3px_0px_#000] rotate-[-3deg]">
            <Flame className="h-6 w-6 text-black" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-comic text-3xl tracking-wider text-yellow-400 drop-shadow-[2px_2px_0px_#000]">
                FORGEHUB AI
              </span>
              <span className="font-mono text-[10px] font-extrabold px-2 py-0.5 rounded bg-red-600 text-white border-2 border-black uppercase shadow-[2px_2px_0px_#000] rotate-[2deg]">
                ZAP HALLUCINATIONS!
              </span>
            </div>
            <p className="text-xs text-slate-300 font-mono font-semibold hidden sm:block">
              Metadata-Governed AI Data Engineering Platform
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={onStart}
            className="px-5 py-2.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-black font-mono font-extrabold text-xs uppercase tracking-wider border-3 border-black shadow-pop-red hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all flex items-center gap-2"
          >
            <span>Launch Studio</span>
            <ArrowRight className="h-4 w-4 stroke-[3]" />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-16 px-6 max-w-6xl mx-auto text-center space-y-8">
        {/* Comic Sticker Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-red-500 text-white border-3 border-black font-mono font-bold text-xs shadow-pop comic-sticker">
          <Zap className="h-4 w-4 text-yellow-300 fill-yellow-300" />
          <span>STOP ROGUE AI SQL FROM BREAKING PRODUCTION!</span>
        </div>

        {/* Catchy Hero Headline */}
        <h1 className="font-comic text-5xl sm:text-7xl lg:text-8xl tracking-wider text-white leading-none drop-shadow-[4px_4px_0px_#000]">
          DATAHUB METADATA IS THE <span className="text-yellow-400 underline decoration-red-500 decoration-wavy">BOSS</span> OF YOUR LLM!
        </h1>

        <p className="max-w-3xl mx-auto text-base sm:text-lg text-slate-300 font-mono leading-relaxed bg-zinc-900/80 p-5 rounded-2xl border-3 border-black shadow-pop">
          Generic AI generators produce plausible SQL that hallucinates non-existent columns like <code className="text-red-400 bg-black px-1.5 py-0.5 rounded border border-red-900">magic_orders_v2</code> or sums <code className="text-yellow-300">USD + EUR</code> interchangeable. 
          <strong className="text-yellow-400"> ForgeHub AI locks the LLM in a DataHub Symbol Contract</strong> — making hallucinations mechanically impossible!
        </p>

        {/* Hero CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <button
            onClick={onStart}
            className="px-8 py-4 rounded-2xl bg-yellow-400 hover:bg-yellow-300 text-black font-mono font-black text-sm uppercase tracking-wider border-4 border-black shadow-pop-red hover:shadow-pop-lg hover:scale-105 active:scale-95 transition-all flex items-center gap-3 text-lg"
          >
            <Sparkles className="h-6 w-6 stroke-[2.5]" />
            <span>Launch Governance Studio</span>
            <ArrowRight className="h-5 w-5 stroke-[3]" />
          </button>

          <a
            href="#how-it-works"
            className="px-6 py-4 rounded-2xl bg-zinc-900 hover:bg-zinc-800 text-white font-mono font-bold text-sm uppercase tracking-wider border-3 border-black shadow-pop hover:translate-y-[-2px] transition-all flex items-center gap-2"
          >
            <Terminal className="h-5 w-5 text-cyan-400" />
            <span>See How It Works</span>
          </a>
        </div>
      </section>

      {/* Comic Storyboard Section (3 Panels) */}
      <section id="how-it-works" className="py-12 px-6 max-w-6xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h2 className="font-comic text-4xl sm:text-5xl text-yellow-400 tracking-wider drop-shadow-[3px_3px_0px_#000]">
            THE DATA ENGINEERING DRAMA: IN 3 PANELS!
          </h2>
          <p className="text-xs font-mono text-slate-400">How ForgeHub AI saves your 3 AM data pipeline calls</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Panel 1 */}
          <div className="bg-red-950/40 p-6 rounded-2xl border-4 border-black shadow-pop-red space-y-3 relative overflow-hidden">
            <div className="absolute -right-3 -top-3 px-3 py-1 bg-red-600 text-white font-comic text-lg border-2 border-black rotate-12 shadow-[2px_2px_0px_#000]">
              PANEL 1: THE CHAOS! 💥
            </div>

            <div className="h-12 w-12 rounded-xl bg-red-600 border-2 border-black flex items-center justify-center text-white font-black text-xl shadow-[3px_3px_0px_#000]">
              👿
            </div>

            <h3 className="font-comic text-2xl text-red-400 tracking-wide">
              Rogue AI SQL Generator
            </h3>

            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              Asked to create an orders model, the LLM hallucinates <code className="text-red-300">customer_name</code> (which doesn't exist in <code className="text-slate-400">retail.orders</code>) and sums USD and EUR together without converting currency!
            </p>

            <div className="p-3 bg-black rounded-xl border-2 border-red-800 text-[11px] font-mono text-red-400">
              ❌ UNKNOWN_COLUMN: customer_name<br/>
              ❌ SEMANTIC_ERROR: Mixed Currency Addition
            </div>
          </div>

          {/* Panel 2 */}
          <div className="bg-yellow-950/30 p-6 rounded-2xl border-4 border-black shadow-pop-yellow space-y-3 relative overflow-hidden">
            <div className="absolute -right-3 -top-3 px-3 py-1 bg-yellow-400 text-black font-comic text-lg border-2 border-black rotate-[-6deg] shadow-[2px_2px_0px_#000]">
              PANEL 2: THE SHIELD! 🛡️
            </div>

            <div className="h-12 w-12 rounded-xl bg-yellow-400 border-2 border-black flex items-center justify-center text-black font-black text-xl shadow-[3px_3px_0px_#000]">
              ⚡
            </div>

            <h3 className="font-comic text-2xl text-yellow-400 tracking-wide">
              DataHub Contract Lock
            </h3>

            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              ForgeHub AI queries DataHub first, builds a verified <strong className="text-yellow-300">Symbol Table</strong>, and constructs an AST boundary. The LLM is forced to operate ONLY inside this box!
            </p>

            <div className="p-3 bg-black rounded-xl border-2 border-yellow-700 text-[11px] font-mono text-yellow-300">
              🔒 Symbol Table: {`{ order_id, quantity, unit_price }`}<br/>
              🛡️ AST Parser: sqlglot Enforcement Active
            </div>
          </div>

          {/* Panel 3 */}
          <div className="bg-cyan-950/30 p-6 rounded-2xl border-4 border-black shadow-pop-cyan space-y-3 relative overflow-hidden">
            <div className="absolute -right-3 -top-3 px-3 py-1 bg-cyan-400 text-black font-comic text-lg border-2 border-black rotate-[8deg] shadow-[2px_2px_0px_#000]">
              PANEL 3: VICTORY! 🏆
            </div>

            <div className="h-12 w-12 rounded-xl bg-cyan-400 border-2 border-black flex items-center justify-center text-black font-black text-xl shadow-[3px_3px_0px_#000]">
              🚀
            </div>

            <h3 className="font-comic text-2xl text-cyan-300 tracking-wide">
              Production dbt Artifacts
            </h3>

            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              Generates validated <code className="text-cyan-300">fct_orders.sql</code>, <code className="text-cyan-300">schema.yml</code>, automated unit tests, and publishes lineage directly back into DataHub!
            </p>

            <div className="p-3 bg-black rounded-xl border-2 border-cyan-800 text-[11px] font-mono text-emerald-400">
              ✓ AST Syntax & Table Checks Passed<br/>
              ✓ DataHub Lineage Write-Back Complete
            </div>
          </div>
        </div>
      </section>

      {/* Superpowers Feature Grid */}
      <section className="py-12 px-6 max-w-6xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <span className="px-3 py-1 rounded-full bg-cyan-400 text-black font-mono font-bold text-xs border-2 border-black shadow-[2px_2px_0px_#000]">
            HEROIC FEATURES
          </span>
          <h2 className="font-comic text-4xl sm:text-5xl text-white tracking-wider drop-shadow-[3px_3px_0px_#000]">
            4 CORE GOVERNANCE SUPERPOWERS
          </h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {/* Feature 1 */}
          <div className="p-6 bg-zinc-900 rounded-2xl border-3 border-black shadow-pop hover:translate-y-[-4px] transition-all space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-red-500 border-2 border-black text-white shadow-[2px_2px_0px_#000]">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <h3 className="font-comic text-2xl text-yellow-400">1. Symbol Table Jail</h3>
            </div>
            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              Before calling the LLM, ForgeHub AI builds a verified catalog registry. If a column or table isn't registered in DataHub, <strong className="text-red-400 font-bold">it cannot exist in the generated SQL. Period.</strong>
            </p>
          </div>

          {/* Feature 2 */}
          <div className="p-6 bg-zinc-900 rounded-2xl border-3 border-black shadow-pop hover:translate-y-[-4px] transition-all space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-yellow-400 border-2 border-black text-black shadow-[2px_2px_0px_#000]">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="font-comic text-2xl text-yellow-400">2. Semantic Type Cop</h3>
            </div>
            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              DataHub glossary terms act as a business type checker. Operations like <code className="text-yellow-300">SUM(discount_rate)</code> or adding mixed currency fields are caught and flagged automatically.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="p-6 bg-zinc-900 rounded-2xl border-3 border-black shadow-pop hover:translate-y-[-4px] transition-all space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-cyan-400 border-2 border-black text-black shadow-[2px_2px_0px_#000]">
                <RefreshCw className="h-5 w-5" />
              </div>
              <h3 className="font-comic text-2xl text-yellow-400">3. Self-Repair Superhero</h3>
            </div>
            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              If an AST parser or YAML validator flags an error, ForgeHub AI feeds the exact AST error log back into the LLM up to 3 repair attempts automatically!
            </p>
          </div>

          {/* Feature 4 */}
          <div className="p-6 bg-zinc-900 rounded-2xl border-3 border-black shadow-pop hover:translate-y-[-4px] transition-all space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-rose-500 border-2 border-black text-white shadow-[2px_2px_0px_#000]">
                <Layers className="h-5 w-5" />
              </div>
              <h3 className="font-comic text-2xl text-yellow-400">4. DataHub Long-Term Memory</h3>
            </div>
            <p className="text-xs font-mono text-slate-300 leading-relaxed">
              After human authorization, the agent writes documentation, AI provenance tags, and upstream/downstream lineage graphs directly back into DataHub.
            </p>
          </div>
        </div>
      </section>

      {/* Quick Interactive Scenario Preview */}
      <section className="py-12 px-6 max-w-5xl mx-auto space-y-6">
        <div className="bg-zinc-900 p-8 rounded-3xl border-4 border-black shadow-pop-yellow space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-2 border-black pb-4">
            <div>
              <span className="font-comic text-xl text-yellow-400 tracking-wide">
                ⚡ DEMO CATALOG FIXTURES PREVIEW
              </span>
              <p className="text-xs font-mono text-slate-400">Click a dataset to inspect its gap report and launch studio</p>
            </div>

            <button
              onClick={onStart}
              className="px-4 py-2 rounded-xl bg-yellow-400 hover:bg-yellow-300 text-black font-mono font-bold text-xs border-2 border-black shadow-pop"
            >
              Open Studio →
            </button>
          </div>

          {/* Scenario Tabs */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <button
              onClick={() => {
                setActiveTab('orders');
                onSelectDataset('orders');
              }}
              className={`p-4 rounded-2xl border-3 text-left transition-all ${
                activeTab === 'orders'
                  ? 'bg-red-950/60 border-red-500 shadow-pop-red'
                  : 'bg-black border-black hover:border-zinc-700'
              }`}
            >
              <div className="font-mono text-xs font-bold text-red-400 mb-1 flex items-center justify-between">
                <span>retail.orders</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-red-600 text-white font-black">GAP</span>
              </div>
              <p className="text-[11px] text-slate-300 line-clamp-2 font-mono">
                Fact orders table. Gap: UNDEFINED_CURRENCY on unit_price.
              </p>
            </button>

            <button
              onClick={() => {
                setActiveTab('customers');
                onSelectDataset('customers');
              }}
              className={`p-4 rounded-2xl border-3 text-left transition-all ${
                activeTab === 'customers'
                  ? 'bg-yellow-950/60 border-yellow-400 shadow-pop-yellow'
                  : 'bg-black border-black hover:border-zinc-700'
              }`}
            >
              <div className="font-mono text-xs font-bold text-yellow-300 mb-1 flex items-center justify-between">
                <span>retail.customers</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-yellow-500 text-black font-black">PII</span>
              </div>
              <p className="text-[11px] text-slate-300 line-clamp-2 font-mono">
                Customer dim table. Contains email/name PII fields.
              </p>
            </button>

            <button
              onClick={() => {
                setActiveTab('revenue');
                onSelectDataset('revenue');
              }}
              className={`p-4 rounded-2xl border-3 text-left transition-all ${
                activeTab === 'revenue'
                  ? 'bg-cyan-950/60 border-cyan-400 shadow-pop-cyan'
                  : 'bg-black border-black hover:border-zinc-700'
              }`}
            >
              <div className="font-mono text-xs font-bold text-cyan-300 mb-1 flex items-center justify-between">
                <span>retail.revenue</span>
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-400 text-black font-black">FINANCIAL</span>
              </div>
              <p className="text-[11px] text-slate-300 line-clamp-2 font-mono">
                Monthly revenue cohort table. Ambiguous currency.
              </p>
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t-4 border-black bg-black py-8 px-6 text-center space-y-3 font-mono text-xs text-slate-500">
        <div className="flex items-center justify-center gap-2">
          <Flame className="h-4 w-4 text-yellow-400" />
          <span className="text-slate-300 font-bold">FORGEHUB AI GOVERNANCE AGENT</span>
        </div>
        <p>Built with DataHub API • sqlglot AST Validator • FastAPI • React & TypeScript</p>
      </footer>
    </div>
  );
};
