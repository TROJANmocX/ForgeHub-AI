import React, { useState } from 'react';
import { GenerationResult } from '../types';
import { UploadCloud, CheckCircle, ShieldAlert, Lock, ArrowRight } from 'lucide-react';
import { publishModel } from '../api/client';

interface PublishPanelProps {
  generation: GenerationResult;
  onPublished: (urn: string) => void;
}

export const PublishPanel: React.FC<PublishPanelProps> = ({
  generation,
  onPublished,
}) => {
  const [publishing, setPublishing] = useState(false);
  const [publishedUrn, setPublishedUrn] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isRequiresReview = generation.status === 'REQUIRES_REVIEW';
  const isFailed = generation.status === 'FAILED';
  const isAlreadyPublished = generation.status === 'PUBLISHED' || publishedUrn !== null;

  const handlePublish = async () => {
    setPublishing(true);
    setError(null);
    try {
      const res = await publishModel(generation.run_id);
      if (res.success) {
        setPublishedUrn(res.model_urn);
        onPublished(res.model_urn);
      }
    } catch (err: any) {
      setError(err.message || 'Publish failed');
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="bg-zinc-900 rounded-3xl p-6 border-4 border-black mb-6 shadow-pop-yellow">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        {/* Status Info */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h3 className="font-comic text-xl text-yellow-400 tracking-wider">
              GOVERNANCE GATE & DATAHUB WRITE-BACK
            </h3>
            <span
              className={`px-2.5 py-0.5 rounded-xl text-xs font-mono font-black uppercase border-2 border-black shadow-[2px_2px_0px_#000] ${
                isAlreadyPublished
                  ? 'bg-cyan-400 text-black'
                  : isRequiresReview
                  ? 'bg-yellow-400 text-black'
                  : isFailed
                  ? 'bg-red-600 text-white'
                  : 'bg-yellow-400 text-black'
              }`}
            >
              {isAlreadyPublished ? 'PUBLISHED' : generation.status}
            </span>
          </div>

          <p className="text-xs font-mono text-slate-300 leading-relaxed">
            {isAlreadyPublished
              ? 'Model metadata, AI tags, README, and upstream lineage written to DataHub.'
              : isRequiresReview
              ? 'Review identified metadata gap report prior to authorizing publish.'
              : isFailed
              ? 'Generation rejected by validation contract. Publish prohibited.'
              : 'All contract specifications satisfied. Ready for human authorization.'}
          </p>
        </div>

        {/* Publish Action Button */}
        <div>
          {isAlreadyPublished ? (
            <div className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-cyan-400 border-3 border-black text-black font-mono font-black text-xs uppercase shadow-pop">
              <CheckCircle className="h-4 w-4 stroke-[3]" />
              <span>Published to DataHub</span>
            </div>
          ) : isFailed ? (
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-red-600 border-3 border-black text-white font-mono font-black text-xs uppercase shadow-pop">
              <Lock className="h-4 w-4 stroke-[3]" />
              <span>Publish Prohibited</span>
            </div>
          ) : (
            <button
              onClick={handlePublish}
              disabled={publishing}
              className="px-6 py-3.5 rounded-2xl bg-cyan-400 hover:bg-cyan-300 text-black font-mono font-black text-xs uppercase tracking-wider border-3 border-black shadow-pop-red hover:shadow-pop-lg transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {publishing ? (
                <>
                  <span className="h-4 w-4 rounded-full border-2 border-black border-t-transparent animate-spin" />
                  <span>Writing to DataHub...</span>
                </>
              ) : (
                <>
                  <UploadCloud className="h-4 w-4 stroke-[3]" />
                  <span>Approve & Publish to DataHub</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Success notification */}
      {publishedUrn && (
        <div className="mt-4 p-4 rounded-2xl bg-black border-3 border-black text-xs font-mono text-cyan-300 flex items-center justify-between shadow-pop">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-cyan-400 shrink-0 stroke-[3]" />
            <span>Discoverable URN: <strong className="text-yellow-400 font-extrabold">{publishedUrn}</strong></span>
          </div>
          <ArrowRight className="h-4 w-4 text-cyan-400 stroke-[3]" />
        </div>
      )}

      {/* Error notification */}
      {error && (
        <div className="mt-4 p-3 rounded-2xl bg-red-600 border-3 border-black text-xs font-mono text-white flex items-center gap-2 shadow-pop font-bold">
          <ShieldAlert className="h-4 w-4 stroke-[3]" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
