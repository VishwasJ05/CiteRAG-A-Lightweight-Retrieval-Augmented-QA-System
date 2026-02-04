# MiniRAGX

A Retrieval-Augmented Generation (RAG) application that allows users to ingest documents, store them in a vector database, and query them using an LLM with inline citations.

**📄 [Resume Link](https://drive.google.com/file/d/1NiUaUQke0eTOX0M9qmPgbOrmDzH3UIIF/view?usp=sharing)** 

---

## 🌐 Live Demo

**[https://mini-rag-taupe.vercel.app](https://mini-rag-taupe.vercel.app)**

---

## 🏗️ Architecture

```
                        MINI RAG ARCHITECTURE


    ======================== INGEST FLOW ========================

    User Text
        |
        v
    Chunker (1000 tokens, 12% overlap)
        |
        v
    Jina Embeddings v3 (1024 dimensions)
        |
        v
    Pinecone Vector Store (upsert)


    ======================== QUERY FLOW =========================

    User Question
        |
        v
    Jina Embeddings v3 (1024 dimensions)
        |
        v
    Pinecone Retrieval (MMR, top-20)
        |
        v
    Jina Reranker (top-5)
        |
        v
    Groq LLM (Llama 3.3 70B)
        |
        v
    Answer with Citations [1][2][3]


    ======================= TECH STACK ==========================

    Frontend:   React + Vite + TypeScript + Tailwind CSS
    Backend:    FastAPI (Python 3.11)
    Embeddings: Jina Embeddings v3
    Reranker:   Jina Reranker
    Vector DB:  Pinecone (Serverless)
    LLM:        Groq (Llama 3.3 70B Versatile)
    Hosting:    Vercel (Frontend) + Render (Backend)
```

---

## 🛠️ Tech Stack

| Component | Technology | Version/Model |
|-----------|------------|---------------|
| **Frontend** | React + Vite + TypeScript | React 19, Vite 7 |
| **Styling** | Tailwind CSS | v4.1.18 |
| **Backend** | FastAPI + Python | Python 3.11 |
| **Vector DB** | Pinecone (Cloud) | Serverless |
| **Embeddings** | Jina Embeddings v3 | 1024 dimensions |
| **Reranker** | Jina Reranker | - |
| **LLM** | Groq (Llama 3.3 70B) | llama-3.3-70b-versatile |
| **Hosting** | Render (Backend) + Vercel (Frontend) | Free tier |

---

## ⚙️ Configuration

### Chunking Parameters
- **Chunk Size**: 1000 tokens
- **Overlap**: 12% (120 tokens)
- **Tokenizer**: tiktoken (cl100k_base)

### Retrieval Strategy
- **Initial Retrieval**: Top-20 with MMR (Maximal Marginal Relevance)
- **Reranking**: Jina Reranker → Top-5 most relevant
- **Citation Format**: Inline numeric citations [1], [2], [3]

### Pinecone Index Configuration
```yaml
Index Name: mini-rag-index
Dimension: 1024
Metric: cosine
Cloud: AWS
Region: us-east-1
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- API Keys: Jina AI, Pinecone, Groq

### Backend Setup

```bash
# Clone repository
git clone https://github.com/Crypt0-X2/mini-RAG.git
cd mini-RAG

# Create virtual environment
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run backend
uvicorn app.main:app --reload --port 8001
```

### Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env to set backend URL

# Run frontend
npm run dev
```

Visit `http://localhost:5173` to use the app.

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
```env
# Required API Keys
JINA_API_KEY=your_jina_api_key
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key

# Pinecone Config
PINECONE_INDEX_NAME=mini-rag-index

# Optional Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=120
RETRIEVAL_TOP_K=20
RERANK_TOP_K=5
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8001
```

---

## 📡 API Endpoints

### Health Check
```http
GET /health
```
Returns API status and version.

### Ingest Documents
```http
POST /ingest
Content-Type: application/json

{
  "text": "Your document text here...",
  "title": "Document Title",
  "source": "user_input"
}
```

### Query
```http
POST /query
Content-Type: application/json

{
  "query": "What is a neural network?",
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "A neural network is... [1][2]",
  "citations": [
    {
      "citation_number": 1,
      "text": "Source chunk text...",
      "source": "user_input",
      "position": 0
    }
  ],
  "retrieved_chunks": 5,
  "latency_ms": 2500
}
```

---

## 📊 Evaluation Results

See [evaluation.md](evaluation.md) for detailed results.

### Summary (5 Q/A Gold Set)

| Metric | Score |
|--------|-------|
| Precision | 100% |
| Recall | 95% |
| Citation Accuracy | 100% |
| Hallucination Rate | 0% |

---

## 🚢 Deployment

### Backend (Render)
1. Connect GitHub repo to Render
2. Set environment variables (API keys)
3. Build Command: `pip install -r backend/requirements.txt`
4. Start Command: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Connect GitHub repo to Vercel
2. Root Directory: `frontend`
3. Set `VITE_API_BASE_URL` to Render backend URL
4. Deploy

---

## 📝 Remarks

### Trade-offs Made
1. **Free Tier Constraints**: Using Render free tier means cold starts (~30s) after inactivity
2. **Single Index**: All documents stored in one Pinecone index (no multi-tenant support)
3. **No Authentication**: API is open for demo purposes
4. **Context Window**: Limited to top-5 reranked chunks to fit LLM context

### Limitations
1. No persistent document management (no delete/update)
2. No conversation history (single-turn queries only)
3. Rate limits on free tier APIs
4. No file upload (text paste only)

### What I'd Do Next
1. Add document management (list, delete, update)
2. Implement streaming responses for better UX
3. Add authentication and rate limiting
4. Support PDF/DOC file uploads
5. Add evaluation metrics dashboard
6. Implement hybrid search (keyword + semantic)

### Provider Limits Encountered
- **Groq**: 6000 tokens/minute on free tier (sufficient for demo)
- **Pinecone**: 100K vectors on free tier (more than enough)
- **Jina**: 1M tokens/month free (adequate for testing)
- **Render**: Spins down after 15 min inactivity

---

## 📁 Project Structure

```
mini-RAG/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── routers/
│   │   │   ├── ingest.py     # /ingest endpoint
│   │   │   └── query.py      # /query endpoint
│   │   ├── services/
│   │   │   ├── chunker.py    # Text chunking
│   │   │   ├── embedding_service.py
│   │   │   ├── pinecone_service.py
│   │   │   ├── reranker_service.py
│   │   │   └── llm_service.py
│   │   └── models/
│   │       └── schemas.py    # Pydantic models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── IngestPanel.tsx
│   │   │   ├── QueryPanel.tsx
│   │   │   └── ResultsPanel.tsx
│   │   └── services/
│   │       └── api.ts
│   ├── package.json
│   └── .env.example
├── evaluation.md
├── DEPLOYMENT.md
└── README.md
```

---

## 📜 License

MIT License - feel free to use and modify.

---

## 👤 Author
-Vishwas Jasuja
Built for the AI Engineer Track B Assessment.
