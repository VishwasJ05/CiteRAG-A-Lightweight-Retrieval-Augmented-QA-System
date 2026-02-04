import React, { useState } from 'react';
import type { QueryResponse, Citation } from '../services/api';

interface ResultsPanelProps {
  result: QueryResponse | null;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ result }) => {
  const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set());

  if (!result) {
    return (
      <div className="bg-slate-900 bg-opacity-70 backdrop-blur-md rounded-2xl shadow-2xl p-8 h-full flex items-center justify-center border-2 border-blue-500">
        <div className="text-center">
          <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-6 rounded-full inline-block mb-4 shadow-lg shadow-blue-500/50">
            <svg className="h-16 w-16 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <p className="text-white font-bold text-lg">Ask a question to see AI-powered results</p>
          <p className="text-cyan-300 text-sm mt-2">with citations and sources</p>
        </div>
      </div>
    );
  }

  const toggleCitation = (num: number) => {
    const newExpanded = new Set(expandedCitations);
    if (newExpanded.has(num)) {
      newExpanded.delete(num);
    } else {
      newExpanded.add(num);
    }
    setExpandedCitations(newExpanded);
  };

  const renderAnswerWithCitations = (answer: string) => {
    // Split by citation pattern [1], [2], etc.
    const parts = answer.split(/(\[\d+\])/g);
    return parts.map((part, idx) => {
      const match = part.match(/\[(\d+)\]/);
      if (match) {
        const citationNum = parseInt(match[1]);
        return (
          <button
            key={idx}
            onClick={() => toggleCitation(citationNum)}
            className="text-blue-600 hover:text-blue-800 font-semibold cursor-pointer"
          >
            {part}
          </button>
        );
      }
      return <span key={idx}>{part}</span>;
    });
  };

  const estimatedTokens = Math.max(1, Math.ceil(result.answer.length / 4));
  const usdPerMillionTokens = 0.25;
  const estimatedCost = (estimatedTokens / 1_000_000) * usdPerMillionTokens;

  const isUrl = (value?: string) => !!value && /^https?:\/\//i.test(value);

  return (
    <div className="bg-slate-900 bg-opacity-70 backdrop-blur-md rounded-2xl shadow-2xl p-6 h-full overflow-y-auto border-2 border-blue-500">
      <div className="flex items-center space-x-3 mb-6">
        <div className="bg-gradient-to-br from-blue-500 to-cyan-500 p-2 rounded-xl shadow-lg">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-white">Answer</h2>
      </div>

      <div className="mb-4">
        <div className="bg-slate-950 bg-opacity-70 border-2 border-blue-500 rounded-xl p-5 shadow-inner">
          <p className="text-cyan-50 leading-relaxed whitespace-pre-wrap font-medium text-base">
            {renderAnswerWithCitations(result.answer)}
          </p>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-4 gap-3">
        <div className="bg-slate-950 bg-opacity-70 border border-cyan-500 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-cyan-400">{result.retrieved_chunks}</div>
          <div className="text-xs text-cyan-300 mt-1">Chunks Retrieved</div>
        </div>
        <div className="bg-slate-950 bg-opacity-70 border border-blue-500 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">{result.latency_ms.toFixed(0)}ms</div>
          <div className="text-xs text-blue-300 mt-1">Latency</div>
        </div>
        <div className="bg-slate-950 bg-opacity-70 border border-teal-500 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-teal-400">~{estimatedTokens}</div>
          <div className="text-xs text-teal-300 mt-1">Tokens</div>
        </div>
        <div className="bg-slate-950 bg-opacity-70 border border-emerald-500 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-emerald-400">${estimatedCost.toFixed(4)}</div>
          <div className="text-xs text-emerald-300 mt-1">Cost Estimate</div>
        </div>
      </div>

      {result.citations.length > 0 && (
        <div>
          <h3 className="text-lg font-bold text-white mb-4">
            Sources ({result.citations.length})
          </h3>
          <div className="space-y-3">
            {result.citations.map((citation: Citation) => {
              const isExpanded = expandedCitations.has(citation.citation_number);
              return (
                <div
                  key={citation.citation_number}
                  className="border-2 border-cyan-700 rounded-xl overflow-hidden hover:border-cyan-500 hover:shadow-md transition-all bg-slate-950 bg-opacity-60"
                >
                  <button
                    onClick={() => toggleCitation(citation.citation_number)}
                    className="w-full px-4 py-3 bg-slate-900 bg-opacity-60 hover:bg-slate-800 transition-colors text-left flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 text-white text-sm font-bold shadow-md">
                        {citation.citation_number}
                      </span>
                      <span className="font-semibold text-cyan-100">
                        {citation.title || 'Document'}
                      </span>
                      {citation.source && (
                        isUrl(citation.source) ? (
                          <a
                            href={citation.source}
                            target="_blank"
                            rel="noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-xs text-cyan-400 hover:text-cyan-300 hover:underline font-medium"
                          >
                            view source
                          </a>
                        ) : (
                          <span className="text-xs text-cyan-500 italic">
                            {citation.source}
                          </span>
                        )
                      )}
                    </div>
                    <svg
                      className={`w-5 h-5 text-purple-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {isExpanded && (
                    <div className="px-4 py-4 bg-slate-950 bg-opacity-80 border-t-2 border-cyan-800 max-h-96 overflow-y-auto">
                      <p className="text-sm text-cyan-100 leading-relaxed whitespace-pre-wrap bg-slate-900 bg-opacity-40 p-3 rounded-lg">
                        {citation.text}
                      </p>
                      {citation.position !== undefined && (
                        <p className="text-xs text-gray-500 mt-3 flex items-center space-x-1">
                          <span>\ud83d\udccd</span>
                          <span>Chunk position: {citation.position}</span>
                        </p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsPanel;
