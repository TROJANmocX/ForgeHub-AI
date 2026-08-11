import React from 'react';
import { ValidationReport as ValidationReportType } from '../types';
import { CheckCircle2, XCircle, AlertTriangle, ShieldCheck, RefreshCw } from 'lucide-react';

interface ValidationReportProps {
  report: ValidationReportType;
  repairAttempts: number;
}

export const ValidationReportComponent: React.FC<ValidationReportProps> = ({
  report,
  repairAttempts,
}) => {
  return (
    <div className="bg-zinc-900 rounded-3xl p-6 border-4 border-black mb-6 shadow-pop-cyan">
      <div className="flex items-center justify-between mb-4 border-b-2 border-black pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-yellow-400" />
          <h3 className="font-comic text-xl text-yellow-400 tracking-wider">
            AST & SEMANTIC CONTRACT VERIFICATION
          </h3>
        </div>

        <div className="flex items-center gap-3">
          {repairAttempts > 0 && (
            <span className="flex items-center gap-1 text-xs font-mono font-extrabold px-3 py-1 rounded-xl bg-yellow-400 text-black border-2 border-black shadow-[2px_2px_0px_#000]">
              <RefreshCw className="h-3 w-3 animate-spin stroke-[3]" />
              SELF-REPAIRED ({repairAttempts} RETRIES)
            </span>
          )}

          <span
            className={`px-3 py-1 rounded-xl text-xs font-mono font-black border-2 border-black uppercase tracking-wider shadow-[2px_2px_0px_#000] ${
              report.passed
                ? 'bg-cyan-400 text-black'
                : 'bg-red-600 text-white animate-bounce'
            }`}
          >
            {report.passed ? '✓ CONTRACT PASSED' : '✗ CONTRACT REJECTED'}
          </span>
        </div>
      </div>

      {/* Checklist grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mb-4">
        {report.checks.map((check, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-2xl border-2 border-black flex items-center justify-between font-mono text-xs shadow-[2px_2px_0px_#000] ${
              check.passed
                ? 'bg-black text-slate-100'
                : 'bg-red-950 text-red-200'
            }`}
          >
            <span className="truncate pr-2 font-extrabold">{check.name}</span>
            {check.passed ? (
              <CheckCircle2 className="h-4 w-4 text-cyan-400 shrink-0 stroke-[2.5]" />
            ) : (
              <XCircle className="h-4 w-4 text-red-500 shrink-0 stroke-[2.5]" />
            )}
          </div>
        ))}
      </div>

      {/* Errors list if any */}
      {report.errors.length > 0 && (
        <div className="p-4 rounded-2xl bg-red-600 text-white font-mono text-xs space-y-2 mb-3 border-3 border-black shadow-pop">
          <h4 className="font-mono font-black flex items-center gap-1.5 uppercase tracking-wider text-sm">
            <XCircle className="h-4 w-4 stroke-[3]" />
            CONTRACT VIOLATION ERRORS ({report.errors.length})
          </h4>
          <ul className="space-y-1 font-mono list-disc list-inside font-bold">
            {report.errors.map((err, i) => (
              <li key={i} className="leading-relaxed">
                {err}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings list if any */}
      {report.warnings.length > 0 && (
        <div className="p-4 rounded-2xl bg-yellow-400 text-black font-mono text-xs space-y-2 border-3 border-black shadow-pop">
          <h4 className="font-mono font-black flex items-center gap-1.5 uppercase tracking-wider text-sm">
            <AlertTriangle className="h-4 w-4 stroke-[3]" />
            GOVERNANCE WARNINGS ({report.warnings.length})
          </h4>
          <ul className="space-y-1 font-mono list-disc list-inside font-bold">
            {report.warnings.map((warn, i) => (
              <li key={i} className="leading-relaxed">
                {warn}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
