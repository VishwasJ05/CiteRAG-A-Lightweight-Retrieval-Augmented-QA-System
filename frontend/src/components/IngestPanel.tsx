import React, { useState } from 'react';
import { ingestText } from '../services/api';
import type { IngestResponse } from '../services/api';

const IngestPanel: React.FC = () => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleIngest = async () => {
    if (!text.trim()) {
      setError('Please enter some text to upload');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await ingestText({ text });
      setResult(response);
      setText('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to ingest text');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 bg-opacity-70 backdrop-blur-md rounded-2xl shadow-2xl p-6 h-full flex flex-col border-2 border-cyan-500 hover:border-cyan-400 transition-all">
      <div className="flex items-center justify-center space-x-3 mb-6">
        <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-3 rounded-xl shadow-lg">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white">Add Documents</h2>
          <p className="text-sm text-cyan-300 mt-1">Upload content to your knowledge base</p>
        </div>
      </div>
      
      <div className="flex-1 flex flex-col space-y-4">
        <div className="flex-1 flex flex-col">
          <label className="block text-sm font-semibold text-cyan-200 mb-2">
            Document Text
          </label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste your document content here... The system will automatically chunk and embed the text for semantic search."
            className="w-full h-full min-h-[300px] px-4 py-3 border-2 border-cyan-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 resize-none text-base bg-slate-950 bg-opacity-60 text-cyan-50 placeholder-cyan-800 shadow-inner"
            disabled={loading}
          />
          <div className="mt-2 flex items-center justify-between text-xs text-cyan-300 font-medium">
            <span>{text.length} characters</span>
            <span>~{Math.ceil(text.length / 4)} tokens</span>
          </div>
        </div>

        <button
          onClick={handleIngest}
          disabled={loading || !text.trim()}
          className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white py-3 px-6 rounded-xl hover:from-cyan-700 hover:to-blue-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed transition-all font-semibold shadow-lg hover:shadow-2xl hover:shadow-cyan-500/50 transform hover:scale-[1.02] active:scale-[0.98]"
        >
          {loading ? (
            <span className="flex items-center justify-center space-x-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Processing...</span>
            </span>
          ) : (
            'Upload & Process'
          )}
        </button>

        {result && (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-lg p-4 shadow-md">
            <p className="text-green-800 font-bold flex items-center space-x-2">
              <span className="text-xl">✓</span>
              <span>Successfully Added!</span>
            </p>
            <p className="text-sm text-green-700 mt-1 font-medium">
              {result.message}
            </p>
            <p className="text-xs text-green-600 mt-1">
              Chunks: {result.chunk_count} | Vectors: {result.vector_count}
            </p>
          </div>
        )}

        {error && (
          <div className="bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-300 rounded-lg p-4 shadow-md">
            <p className="text-red-800 font-bold flex items-center space-x-2">
              <span className="text-xl">⚠</span>
              <span>Error</span>
            </p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default IngestPanel;
