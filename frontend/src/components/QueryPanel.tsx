import React, { useState } from 'react';
import { queryText } from '../services/api';
import type { QueryResponse } from '../services/api';

interface QueryPanelProps {
  onQueryResult: (result: QueryResponse) => void;
}

const QueryPanel: React.FC<QueryPanelProps> = ({ onQueryResult }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await queryText({ query });
      onQueryResult(response);
      setQuery('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  return (
    <div className="bg-slate-900 bg-opacity-70 backdrop-blur-md rounded-2xl shadow-2xl p-6 border-2 border-teal-500 hover:border-teal-400 transition-all">
      <div className="flex items-center justify-center space-x-3 mb-4">
        <div className="bg-gradient-to-br from-teal-500 to-cyan-500 p-3 rounded-xl shadow-lg">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        </div>
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white">Ask Questions</h2>
          <p className="text-sm text-teal-300 mt-1">Query your knowledge base</p>
        </div>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-teal-200 mb-2">
            Your Question
          </label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask anything about your documents... E.g., 'What is RNN?' or 'Explain transformers'"
            className="w-full px-4 py-3 border-2 border-teal-500 rounded-xl focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-teal-400 resize-none text-base bg-slate-950 bg-opacity-60 text-cyan-50 placeholder-teal-800 shadow-inner"
            rows={3}
            disabled={loading}
          />
          <p className="text-xs text-teal-300 mt-2 font-medium">
            Press Enter to search, Shift+Enter for new line
          </p>
        </div>

        <button
          onClick={handleQuery}
          disabled={loading || !query.trim()}
          className="w-full bg-gradient-to-r from-teal-600 to-cyan-600 text-white py-3 px-6 rounded-xl hover:from-teal-700 hover:to-cyan-700 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed transition-all font-semibold shadow-lg hover:shadow-2xl hover:shadow-teal-500/50 transform hover:scale-[1.02] active:scale-[0.98]"
        >
          {loading ? (
            <span className="flex items-center justify-center space-x-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Searching...</span>
            </span>
          ) : (
            'Search'
          )}
        </button>

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

export default QueryPanel;
