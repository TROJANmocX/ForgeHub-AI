import React from 'react';
import { GitCommit, ArrowRight, Database, Layers } from 'lucide-react';

interface LineageGraphProps {
  sourceName: string;
  modelName: string;
  published?: boolean;
}

export const LineageGraph: React.FC<LineageGraphProps> = ({
  sourceName,
  modelName,
  published = false,
}) => {
  return (
    <div className="bg-zinc-900 rounded-3xl p-6 border-4 border-black mb-6 shadow-pop">
      <div className="flex items-center justify-between mb-4 border-b-2 border-black pb-3">
        <div className="flex items-center gap-2">
          <GitCommit className="h-5 w-5 text-yellow-400" />
          <h3 className="font-comic text-xl text-yellow-400 tracking-wider">
            DATAHUB PROVENANCE & LINEAGE DAG
          </h3>
        </div>
        <span className="text-[10px] font-mono text-slate-300 font-bold uppercase">
          Source → Target Graph
        </span>
      </div>

      {/* DAG Visualization */}
      <div className="p-6 rounded-2xl bg-black border-3 border-black flex items-center justify-center gap-4 sm:gap-8 overflow-x-auto shadow-inner">
        {/* Source Node */}
        <div className="p-4 rounded-2xl bg-zinc-900 border-3 border-black text-center min-w-[160px] shadow-pop">
          <div className="flex items-center justify-center gap-2 text-yellow-400 mb-1 font-mono text-xs font-black">
            <Database className="h-4 w-4" />
            <span>SOURCE</span>
          </div>
          <p className="font-mono text-sm font-extrabold text-slate-100">
            {sourceName}
          </p>
          <span className="text-[10px] text-cyan-300 font-mono block mt-1 font-bold">
            BigQuery Physical
          </span>
        </div>

        {/* Connection Arrow */}
        <div className="flex flex-col items-center gap-1">
          <span className="text-[9px] font-mono font-black text-black uppercase tracking-widest px-2.5 py-1 rounded-xl bg-yellow-400 border-2 border-black shadow-[2px_2px_0px_#000]">
            AI TRANSFORMED
          </span>
          <ArrowRight className="h-6 w-6 text-yellow-400 stroke-[3]" />
        </div>

        {/* Target Model Node */}
        <div className={`p-4 rounded-2xl border-3 border-black text-center min-w-[160px] transition-all ${
          published
            ? 'bg-cyan-400 text-black font-bold shadow-pop-red'
            : 'bg-zinc-900 text-white shadow-pop'
        }`}>
          <div className="flex items-center justify-center gap-2 mb-1 font-mono text-xs font-black">
            <Layers className="h-4 w-4" />
            <span>{published ? 'PUBLISHED' : 'GENERATED MODEL'}</span>
          </div>
          <p className="font-mono text-sm font-extrabold">
            forgehub.{modelName}
          </p>
          <span className="text-[10px] font-mono block mt-1 opacity-90">
            dbt Enterprise Model
          </span>
        </div>
      </div>
    </div>
  );
};
