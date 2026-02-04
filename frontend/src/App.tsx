import { useState, useEffect } from 'react';
import IngestPanel from './components/IngestPanel';
import QueryPanel from './components/QueryPanel';
import ResultsPanel from './components/ResultsPanel';
import { checkHealth } from './services/api';
import type { QueryResponse } from './services/api';
import './index.css';

function App() {
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [healthStatus, setHealthStatus] = useState<'checking' | 'healthy' | 'unhealthy'>('checking');

  useEffect(() => {
    checkHealth()
      .then(() => setHealthStatus('healthy'))
      .catch(() => setHealthStatus('unhealthy'));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-cyan-950 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full opacity-15 blur-3xl animate-pulse"></div>
        <div className="absolute top-1/3 -left-40 w-[500px] h-[500px] bg-gradient-to-br from-blue-600 to-teal-600 rounded-full opacity-10 blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-full opacity-15 blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      {/* Header */}
      <header className="relative bg-gradient-to-r from-slate-900 via-blue-900 to-cyan-900 shadow-2xl border-b-4 border-cyan-500">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center relative">
            <div className="absolute right-8 flex items-center space-x-3 bg-slate-900 bg-opacity-70 backdrop-blur-md px-5 py-2.5 rounded-full shadow-xl border-2 border-cyan-500">
              <div className={`w-3 h-3 rounded-full ${healthStatus === 'healthy' ? 'bg-emerald-400 shadow-lg shadow-emerald-400/50 animate-pulse' : healthStatus === 'unhealthy' ? 'bg-red-400 shadow-lg shadow-red-400/50' : 'bg-yellow-400 shadow-lg shadow-yellow-400/50 animate-pulse'}`}></div>
              <span className="text-sm font-bold text-white">
                {healthStatus === 'healthy' ? '✓ Connected' : healthStatus === 'unhealthy' ? '✗ Offline' : '⟳ Connecting...'}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl blur-xl opacity-75 animate-pulse"></div>
                <div className="relative bg-gradient-to-br from-cyan-600 to-blue-700 p-4 rounded-2xl shadow-2xl">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
              </div>
              <div className="text-center">
                <h1 className="text-6xl font-black bg-gradient-to-r from-cyan-400 via-blue-400 to-teal-400 bg-clip-text text-transparent tracking-tight drop-shadow-2xl">
                  Mini RAG
                </h1>
                <p className="text-cyan-200 text-sm font-medium mt-2">
                  Retrieval-Augmented Generation System with Semantic Search
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative w-full px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-180px)]">
          {/* Left Column - Ingest */}
          <div className="h-full">
            <IngestPanel />
          </div>

          {/* Right Column - Query */}
          <div className="h-full flex flex-col space-y-6">
            <QueryPanel onQueryResult={setQueryResult} />
            <div className="flex-1 overflow-hidden">
              <ResultsPanel result={queryResult} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
