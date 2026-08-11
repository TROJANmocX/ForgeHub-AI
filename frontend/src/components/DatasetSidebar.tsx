import React from 'react';
import { DatasetSummary } from '../types';
import { Database, Table, ChevronRight, AlertTriangle } from 'lucide-react';

interface DatasetSidebarProps {
  datasets: DatasetSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  loading: boolean;
}

export const DatasetSidebar: React.FC<DatasetSidebarProps> = ({
  datasets,
  selectedId,
  onSelect,
  loading,
}) => {
  return (
    <aside className="w-72 border-r-4 border-black bg-zinc-900 flex flex-col shrink-0 h-[calc(100vh-5rem)] sticky top-20 shadow-pop">
      {/* Sidebar header */}
      <div className="p-4 border-b-3 border-black flex items-center justify-between bg-zinc-950">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-yellow-400" />
          <h2 className="font-comic text-xl text-yellow-400 tracking-wider">
            CATALOG DATASETS
          </h2>
        </div>
        <span className="text-[10px] font-mono font-black px-2 py-0.5 rounded bg-cyan-400 text-black border-2 border-black shadow-[2px_2px_0px_#000]">
          {datasets.length} ENTITIES
        </span>
      </div>

      {/* Dataset List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {loading ? (
          <div className="space-y-2 p-2">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-16 rounded-2xl bg-zinc-800 animate-pulse border-3 border-black"
              />
            ))}
          </div>
        ) : (
          datasets.map((ds) => {
            const isSelected = ds.id === selectedId;
            const isOrders = ds.id === 'orders';
            const isRevenue = ds.id === 'revenue';
            const hasGap = isOrders || isRevenue;

            return (
              <button
                key={ds.id}
                onClick={() => onSelect(ds.id)}
                className={`w-full text-left p-3.5 rounded-2xl transition-all duration-200 group relative border-3 border-black ${
                  isSelected
                    ? 'bg-yellow-400 text-black shadow-pop-red font-bold translate-x-1'
                    : 'bg-black text-slate-200 hover:bg-zinc-800 hover:shadow-pop'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2 font-mono text-xs font-extrabold">
                    <Table className={`h-4 w-4 shrink-0 ${isSelected ? 'text-black' : 'text-yellow-400'}`} />
                    <span className="truncate">{ds.name}</span>
                  </div>
                  <ChevronRight
                    className={`h-4 w-4 stroke-[3] transition-transform ${
                      isSelected ? 'translate-x-1 text-black' : 'text-slate-400 group-hover:text-yellow-400'
                    }`}
                  />
                </div>

                <p className={`text-[11px] line-clamp-1 mb-2 font-mono leading-relaxed ${
                  isSelected ? 'text-black/90 font-medium' : 'text-slate-400'
                }`}>
                  {ds.description || 'No catalog description.'}
                </p>

                <div className="flex items-center justify-between text-[10px]">
                  <span className={`font-mono uppercase font-black ${
                    isSelected ? 'text-black' : 'text-cyan-400'
                  }`}>
                    {ds.platform} • {ds.environment}
                  </span>

                  {hasGap && (
                    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded border-2 border-black font-mono font-black text-[9px] ${
                      isSelected ? 'bg-red-600 text-white' : 'bg-red-500 text-white shadow-[2px_2px_0px_#000]'
                    }`}>
                      <AlertTriangle className="h-3 w-3 fill-yellow-300 text-black" />
                      GAP
                    </span>
                  )}
                </div>
              </button>
            );
          })
        )}
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t-3 border-black bg-black text-center text-[10px] text-slate-400 font-mono font-bold">
        ⚡ DATAHUB METADATA CONTRACT
      </div>
    </aside>
  );
};
