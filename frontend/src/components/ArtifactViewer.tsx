import React, { useState } from 'react';
import { Code2, FileText, BookOpen, Copy, Check } from 'lucide-react';

interface ArtifactViewerProps {
  sql: string;
  schemaYml: string;
  readme: string;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  sql,
  schemaYml,
  readme,
}) => {
  const [activeTab, setActiveTab] = useState<'sql' | 'schema' | 'readme'>('sql');
  const [copied, setCopied] = useState(false);

  const getContent = () => {
    switch (activeTab) {
      case 'sql':
        return sql;
      case 'schema':
        return schemaYml;
      case 'readme':
        return readme;
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(getContent());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-zinc-900 rounded-3xl border-4 border-black overflow-hidden flex flex-col mb-6 shadow-pop">
      {/* Tab Navigation Header */}
      <div className="flex items-center justify-between px-4 pt-3 border-b-3 border-black bg-black">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('sql')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl font-mono text-xs font-extrabold transition-all border-t-3 border-x-3 ${
              activeTab === 'sql'
                ? 'bg-yellow-400 text-black border-black shadow-[2px_0px_0px_#000]'
                : 'text-slate-400 hover:text-white border-transparent hover:bg-zinc-800'
            }`}
          >
            <Code2 className="h-4 w-4 stroke-[2.5]" />
            <span>model.sql</span>
          </button>

          <button
            onClick={() => setActiveTab('schema')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl font-mono text-xs font-extrabold transition-all border-t-3 border-x-3 ${
              activeTab === 'schema'
                ? 'bg-yellow-400 text-black border-black shadow-[2px_0px_0px_#000]'
                : 'text-slate-400 hover:text-white border-transparent hover:bg-zinc-800'
            }`}
          >
            <FileText className="h-4 w-4 stroke-[2.5]" />
            <span>schema.yml</span>
          </button>

          <button
            onClick={() => setActiveTab('readme')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-t-xl font-mono text-xs font-extrabold transition-all border-t-3 border-x-3 ${
              activeTab === 'readme'
                ? 'bg-yellow-400 text-black border-black shadow-[2px_0px_0px_#000]'
                : 'text-slate-400 hover:text-white border-transparent hover:bg-zinc-800'
            }`}
          >
            <BookOpen className="h-4 w-4 stroke-[2.5]" />
            <span>README.md</span>
          </button>
        </div>

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-black text-xs font-mono font-extrabold border-2 border-black shadow-[2px_2px_0px_#000] transition mb-2"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 stroke-[3]" />
              <span>COPIED</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5 stroke-[3]" />
              <span>COPY CODE</span>
            </>
          )}
        </button>
      </div>

      {/* Code / Content Area */}
      <div className="p-4 bg-black font-mono text-xs overflow-x-auto min-h-[320px] max-h-[500px]">
        <pre className="text-slate-200 leading-relaxed whitespace-pre-wrap selection:bg-yellow-400 selection:text-black font-mono">
          {getContent()}
        </pre>
      </div>
    </div>
  );
};
