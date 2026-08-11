import React from 'react';
import { QualityReport } from '../types';
import { ShieldCheck, AlertCircle, BarChart3 } from 'lucide-react';

interface MetadataQualityCardProps {
  quality: QualityReport;
}

export const MetadataQualityCard: React.FC<MetadataQualityCardProps> = ({ quality }) => {
  const score = quality.overall_score;

  return (
    <div className="bg-zinc-900 rounded-3xl p-6 border-4 border-black flex flex-col h-full shadow-pop-cyan">
      <div className="flex items-center justify-between mb-4 pb-3 border-b-2 border-black">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-yellow-400" />
          <h3 className="font-comic text-xl text-yellow-400 tracking-wider">
            METADATA QUALITY ENGINE
          </h3>
        </div>
        <span className="text-[10px] text-slate-300 font-mono font-bold px-2 py-0.5 bg-black border-2 border-black rounded shadow-[2px_2px_0px_#000]">
          SCORE: 0–100
        </span>
      </div>

      {/* Main Score Display */}
      <div className="flex items-center gap-6 p-4 rounded-2xl bg-black border-3 border-black mb-5 shadow-pop">
        {/* Gauge Circle */}
        <div className="relative h-20 w-20 rounded-full border-4 border-black bg-yellow-400 flex items-center justify-center font-comic font-black text-3xl text-black shrink-0 shadow-[3px_3px_0px_#000]">
          <span>{score}</span>
          <span className="text-[9px] text-black font-mono font-bold absolute -bottom-1">/100</span>
        </div>

        <div>
          <h4 className="font-comic text-lg text-cyan-300 tracking-wide">
            Verified Catalog Score
          </h4>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed font-mono">
            Evaluates schema completeness, column descriptions, glossary coverage, governance tags, and semantic types.
          </p>

          <div className="flex items-center gap-3 mt-2 text-xs font-mono">
            {quality.blocking_count > 0 ? (
              <span className="inline-flex items-center gap-1 text-red-400 font-extrabold px-2 py-0.5 rounded bg-red-950/80 border border-red-800">
                <AlertCircle className="h-3.5 w-3.5" />
                {quality.blocking_count} BLOCKING GAPS
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-emerald-400 font-extrabold px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800">
                <ShieldCheck className="h-3.5 w-3.5" />
                NO BLOCKING GAPS
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Dimension breakdown bars */}
      <div className="space-y-3 flex-1">
        <h4 className="text-[11px] font-mono font-bold text-yellow-400 uppercase tracking-widest mb-2">
          Dimension Breakdown
        </h4>
        {quality.dimensions.map((dim) => (
          <div key={dim.name} className="space-y-1">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-slate-200 font-bold">{dim.name}</span>
              <span className="text-cyan-400 font-extrabold">{Math.round(dim.score)}%</span>
            </div>
            <div className="h-3 w-full bg-black rounded-full overflow-hidden border-2 border-black">
              <div
                className="h-full rounded-full bg-yellow-400 transition-all duration-500 shadow-[2px_0px_0px_#000]"
                style={{ width: `${dim.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
