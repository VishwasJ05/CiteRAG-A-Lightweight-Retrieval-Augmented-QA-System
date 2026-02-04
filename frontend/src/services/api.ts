import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface IngestRequest {
  text: string;
  title?: string;
  source?: string;
}

export interface IngestResponse {
  message: string;
  chunk_count: number;
  vector_count: number;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
}

export interface Citation {
  citation_number: number;
  text: string;
  source?: string;
  title?: string;
  position?: number;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  retrieved_chunks: number;
  latency_ms: number;
}

export const ingestText = async (data: IngestRequest): Promise<IngestResponse> => {
  const response = await api.post('/ingest', data);
  return response.data;
};

export const queryText = async (data: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post('/query', data);
  return response.data;
};

export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await api.get('/health');
  return response.data;
};
