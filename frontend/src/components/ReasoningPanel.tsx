import React from 'react';
import { ReasoningPlan } from '../types';
import { Brain, CheckCircle, ArrowRight, ShieldCheck } from 'lucide-react';

interface ReasoningPanelProps {
  plan: ReasoningPlan;
}

export const ReasoningPanel: React.FC<ReasoningPanelProps> = ({ plan }) => {
  return (
    <div className="bg-zinc-900 rounded-3xl p-6 border-4 border-black mb-6 shadow-pop-yellow">
      <div className="flex items-center justify-between mb-4 border-b-2 border-black pb-3">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-yellow-400" />
          <h3 className="font-comic text-xl text-yellow-400 tracking-wider">
            STRUCTURED REASONING CONTRACT PLAN
          </h3>
        </div>
        <span className="text-[10px] font-mono font-extrabold px-2.5 py-1 rounded-xl bg-cyan-400 text-black border-2 border-black shadow-[2px_2px_0px_#000] uppercase">
          Pre-Generation Inspection
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* Model Name */}
        <div className="p-4 rounded-2xl bg-black border-3 border-black shadow-pop">
          <span className="text-[10px] text-yellow-400 font-mono font-bold uppercase tracking-widest block mb-1">
            Target Model Name
          </span>
          <span className="font-mono text-sm font-extrabold text-white">
            {plan.model_name}
          </span>
        </div>

        {/* Dataset Grain */}
        <div className="p-4 rounded-2xl bg-black border-3 border-black shadow-pop">
          <span className="text-[10px] text-yellow-400 font-mono font-bold uppercase tracking-widest block mb-1">
            Model Grain
          </span>
          <span className="text-xs font-mono font-semibold text-slate-200">
            {plan.grain}
          </span>
        </div>

        {/* Source Tables */}
        <div className="p-4 rounded-2xl bg-black border-3 border-black shadow-pop">
          <span className="text-[10px] text-yellow-400 font-mono font-bold uppercase tracking-widest block mb-1">
            Source Tables
          </span>
          <span className="font-mono text-xs font-extrabold text-cyan-300">
            {plan.source_tables.join(', ')}
          </span>
        </div>
      </div>

      {/* Planned Transformations with Evidence */}
      <div className="space-y-3 mb-6">
        <h4 className="text-[11px] font-mono font-bold text-yellow-400 uppercase tracking-widest">
          Planned Transformations & Evidence
        </h4>

        {plan.transformations.length === 0 ? (
          <p className="text-xs font-mono text-slate-400 italic p-3 bg-black rounded-xl border-2 border-black">
            Pass-through model — no derived columns required.
          </p>
        ) : (
          plan.transformations.map((t, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-black border-3 border-black shadow-pop space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-mono text-xs font-bold text-slate-100">
                  <ArrowRight className="h-4 w-4 text-yellow-400 stroke-[3]" />
                  <span className="text-cyan-300">{t.name}</span>
                  <span className="text-slate-500 font-normal">=</span>
                  <code className="text-yellow-300 bg-zinc-900 px-2 py-0.5 rounded border border-zinc-700 font-mono">
                    {t.expression}
                  </code>
                </div>

                <span className="text-[10px] font-mono font-extrabold px-2 py-0.5 rounded bg-yellow-400 text-black border-2 border-black shadow-[2px_2px_0px_#000]">
                  CONFIDENCE: {Math.round(t.confidence * 100)}%
                </span>
              </div>

              <p className="text-xs text-slate-300 font-sans">{t.reason}</p>
            </div>
          ))
        )}
      </div>

      {/* Tests & Assumptions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Planned Tests */}
        <div className="p-4 rounded-2xl bg-black border-3 border-black shadow-pop">
          <h4 className="text-[10px] font-mono font-bold text-yellow-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <CheckCircle className="h-4 w-4 text-cyan-400 stroke-[2.5]" />
            Planned dbt Tests ({plan.tests.length})
          </h4>
          <div className="flex flex-wrap gap-1.5">
            {plan.tests.map((test, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded-xl bg-cyan-400 text-black text-xs font-mono font-extrabold border-2 border-black shadow-[2px_2px_0px_#000]"
              >
                ✓ {test}
              </span>
            ))}
          </div>
        </div>

        {/* Assumptions */}
        <div className="p-4 rounded-2xl bg-black border-3 border-black shadow-pop">
          <h4 className="text-[10px] font-mono font-bold text-yellow-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <ShieldCheck className="h-4 w-4 text-cyan-400 stroke-[2.5]" />
            Governance Assumptions ({plan.assumptions.length})
          </h4>
          {plan.assumptions.length === 0 ? (
            <p className="text-xs font-mono text-slate-400 italic">No assumptions required.</p>
          ) : (
            <div className="space-y-1 text-xs text-slate-300 font-mono">
              {plan.assumptions.map((a, i) => (
                <p key={i} className="line-clamp-2">
                  • {a.description}
                </p>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
