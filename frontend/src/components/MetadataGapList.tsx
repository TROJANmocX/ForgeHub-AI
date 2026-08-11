import React from 'react';
import { Gap } from '../types';
import { AlertOctagon, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

interface MetadataGapListProps {
  gaps: Gap[];
}

export const MetadataGapList: React.FC<MetadataGapListProps> = ({ gaps }) => {
  const blockingGaps = gaps.filter((g) => g.severity === 'blocking');
  const warningGaps = gaps.filter((g) => g.severity === 'warning');

  return (
    <div className="bg-zinc-900 rounded-3xl p-6 border-4 border-black flex flex-col h-full shadow-pop-red">
      <div className="flex items-center justify-between mb-4 pb-3 border-b-2 border-black">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-500 fill-yellow-300" />
          <h3 className="font-comic text-xl text-yellow-400 tracking-wider">
            METADATA GAP DETECTOR
          </h3>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          {blockingGaps.length > 0 && (
            <span className="px-2.5 py-0.5 rounded bg-red-600 text-white font-extrabold border-2 border-black shadow-[2px_2px_0px_#000]">
              {blockingGaps.length} BLOCKING
            </span>
          )}
          {warningGaps.length > 0 && (
            <span className="px-2.5 py-0.5 rounded bg-yellow-400 text-black font-extrabold border-2 border-black shadow-[2px_2px_0px_#000]">
              {warningGaps.length} WARNING
            </span>
          )}
        </div>
      </div>

      <div className="space-y-3 flex-1 overflow-y-auto max-h-[380px] pr-1">
        {gaps.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center bg-black rounded-2xl border-3 border-black shadow-pop">
            <CheckCircle2 className="h-10 w-10 text-cyan-400 mb-2" />
            <h4 className="font-comic text-xl text-white">
              ZERO METADATA GAPS DETECTED!
            </h4>
            <p className="text-xs font-mono text-slate-400 mt-1 max-w-sm">
              All column attributes fully match DataHub catalog specification.
            </p>
          </div>
        ) : (
          gaps.map((gap, idx) => {
            const isBlocking = gap.severity === 'blocking';
            const isWarning = gap.severity === 'warning';

            return (
              <div
                key={idx}
                className={`p-4 rounded-2xl border-3 border-black transition-all ${
                  isBlocking
                    ? 'bg-red-950/60 shadow-pop-red text-red-100'
                    : isWarning
                    ? 'bg-yellow-950/40 shadow-pop-yellow text-yellow-100'
                    : 'bg-black shadow-pop text-slate-300'
                }`}
              >
                <div className="flex items-start gap-2.5">
                  {isBlocking ? (
                    <AlertOctagon className="h-5 w-5 text-red-500 shrink-0 mt-0.5 stroke-[2.5]" />
                  ) : isWarning ? (
                    <AlertTriangle className="h-5 w-5 text-yellow-400 shrink-0 mt-0.5 stroke-[2.5]" />
                  ) : (
                    <Info className="h-5 w-5 text-cyan-400 shrink-0 mt-0.5 stroke-[2.5]" />
                  )}

                  <div className="flex-1 text-xs space-y-1.5 font-mono">
                    <div className="flex items-center justify-between">
                      <span className="font-extrabold text-sm text-yellow-400">{gap.type}</span>
                      <span
                        className={`text-[9px] font-extrabold uppercase px-2 py-0.5 rounded border-2 border-black shadow-[2px_2px_0px_#000] ${
                          isBlocking
                            ? 'bg-red-600 text-white'
                            : isWarning
                            ? 'bg-yellow-400 text-black'
                            : 'bg-cyan-400 text-black'
                        }`}
                      >
                        {gap.severity}
                      </span>
                    </div>

                    <p className="text-slate-300 text-[11px]">
                      Asset: <strong className="text-white font-extrabold">{gap.asset}</strong>
                    </p>

                    <p className="text-slate-200 leading-normal">{gap.reason}</p>

                    <p className="text-[11px] text-cyan-300 italic pt-1 border-t border-black/60">
                      Generation Impact: {gap.generation_impact}
                    </p>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
