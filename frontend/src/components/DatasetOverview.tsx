import React from 'react';
import { DatasetDetail } from '../types';
import { Table, Tag, BookOpen, User, Layers, Shield, Sparkles, Flame } from 'lucide-react';

interface DatasetOverviewProps {
  dataset: DatasetDetail;
  onGenerate: (brokenMode?: boolean) => void;
  generating: boolean;
}

export const DatasetOverview: React.FC<DatasetOverviewProps> = ({
  dataset,
  onGenerate,
  generating,
}) => {
  return (
    <div className="bg-zinc-900 rounded-3xl p-6 border-4 border-black mb-6 shadow-pop-yellow relative overflow-hidden">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
        {/* Left info */}
        <div className="space-y-3.5 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-xl bg-yellow-400 text-black border-2 border-black font-mono text-[11px] uppercase tracking-widest font-extrabold shadow-[2px_2px_0px_#000]">
              {dataset.platform}
            </span>
            <span className="px-3 py-1 rounded-xl bg-cyan-400 text-black border-2 border-black font-mono text-[11px] uppercase tracking-widest font-extrabold shadow-[2px_2px_0px_#000]">
              {dataset.environment}
            </span>
            <span className="text-[11px] text-slate-400 font-mono">
              URN: {dataset.urn}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 rounded-2xl bg-red-500 border-3 border-black text-white shadow-[3px_3px_0px_#000]">
              <Table className="h-6 w-6 stroke-[2.5]" />
            </div>
            <div>
              <h1 className="font-comic text-3xl font-black text-white tracking-wide text-yellow-400 drop-shadow-[2px_2px_0px_#000]">
                {dataset.name}
              </h1>
              <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed font-mono">
                {dataset.description || 'No catalog description.'}
              </p>
            </div>
          </div>

          {/* Badges / Metadata details */}
          <div className="flex flex-wrap items-center gap-5 text-xs text-slate-300 pt-3 border-t-2 border-black">
            {/* Owners */}
            <div className="flex items-center gap-1.5 font-mono">
              <User className="h-3.5 w-3.5 text-yellow-400" />
              <span className="text-slate-400">Owners:</span>
              <span className="text-cyan-300 font-bold">
                {dataset.owners.length > 0 ? dataset.owners.join(', ') : 'Unassigned'}
              </span>
            </div>

            {/* Domain */}
            <div className="flex items-center gap-1.5 font-mono">
              <Layers className="h-3.5 w-3.5 text-yellow-400" />
              <span className="text-slate-400">Domain:</span>
              <span className="text-slate-200 font-bold">
                {dataset.domains.length > 0 ? dataset.domains.join(', ') : 'None'}
              </span>
            </div>

            {/* Columns count */}
            <div className="flex items-center gap-1.5 font-mono">
              <Shield className="h-3.5 w-3.5 text-yellow-400" />
              <span className="text-slate-400">Columns:</span>
              <span className="font-bold text-yellow-400">
                {dataset.column_count} fields
              </span>
            </div>
          </div>

          {/* Tags & Glossary Terms */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            {dataset.tags.map((t) => (
              <span
                key={t}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl bg-black border-2 border-black text-[10px] font-mono font-bold text-slate-200 shadow-[2px_2px_0px_#000]"
              >
                <Tag className="h-3 w-3 text-cyan-400" />
                {t}
              </span>
            ))}
            {dataset.glossary_terms.map((g) => (
              <span
                key={g}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl bg-yellow-400 border-2 border-black text-[10px] font-mono font-extrabold text-black shadow-[2px_2px_0px_#000]"
              >
                <BookOpen className="h-3 w-3 text-black" />
                {g}
              </span>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row lg:flex-col gap-3 justify-center shrink-0">
          <button
            onClick={() => onGenerate(false)}
            disabled={generating}
            className="px-6 py-3.5 rounded-2xl bg-yellow-400 hover:bg-yellow-300 text-black font-mono font-black text-xs uppercase tracking-wider border-3 border-black shadow-pop-red hover:shadow-pop-lg hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-50 group"
          >
            {generating ? (
              <>
                <span className="h-4 w-4 rounded-full border-2 border-black border-t-transparent animate-spin" />
                <span>Executing Contract Plan...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 stroke-[2.5] text-black group-hover:rotate-12 transition-transform" />
                <span>Generate dbt Model</span>
              </>
            )}
          </button>

          {/* Failure Demo / Break It Button */}
          <button
            onClick={() => onGenerate(true)}
            disabled={generating}
            className="px-4 py-2.5 rounded-2xl bg-red-600 hover:bg-red-500 text-white font-mono font-black text-[11px] uppercase tracking-wider border-3 border-black shadow-pop hover:scale-105 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            title="Demonstrates structural contract rejection of hallucinated columns (spec section 34)"
          >
            <Flame className="h-4 w-4 fill-yellow-300 text-black" />
            <span>Failure Demo (Break It)</span>
          </button>
        </div>
      </div>
    </div>
  );
};
