# Mini RAG - Deployment Guide

This guide will walk you through deploying the Mini RAG application to Render (backend) and Vercel (frontend).

## Prerequisites

1. **GitHub Account** - Your code should be pushed to a GitHub repository
2. **Render Account** - Sign up at [render.com](https://render.com) (free)
3. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free)
4. **API Keys** - Make sure you have:
   - Jina AI API key
   - Pinecone API key
   - Groq API key

## Part 1: Deploy Backend to Render

### Step 1: Push Your Code to GitHub

```bash
# Make sure all changes are committed
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Create Render Account and Service

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** button → Select **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select your `mini-RAG` repository

### Step 3: Configure the Service

On the configuration page:

- **Name**: `mini-rag-backend` (or any name you prefer)
- **Region**: Choose closest to you (e.g., Oregon)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && gunicorn app.main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
- **Instance Type**: `Free`

### Step 4: Add Environment Variables

Scroll down to **Environment Variables** section and add:

1. **JINA_API_KEY** = `your_jina_api_key_here`
2. **PINECONE_API_KEY** = `your_pinecone_api_key_here`
3. **GROQ_API_KEY** = `your_groq_api_key_here`
4. **PYTHON_VERSION** = `3.11.0`

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment to complete (5-10 minutes)
3. Once deployed, you'll see your backend URL: `https://mini-rag-backend.onrender.com`
4. Test it by visiting: `https://your-url.onrender.com/health`

**Important**: Copy your backend URL - you'll need it for the frontend!

## Part 2: Deploy Frontend to Vercel

### Step 1: Create .env File for Frontend

In the `frontend` directory, create a `.env` file:

```bash
cd frontend
# Copy the example
cp .env.example .env
```

Edit `.env` and update the backend URL:
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

**Note**: Replace `your-backend-url` with the actual URL from Render

### Step 2: Test Locally with Production Backend

```bash
# Make sure you're in the frontend directory
npm run dev
```

Open http://localhost:5173 and verify it connects to your production backend.

### Step 3: Create Vercel Account and Deploy

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click **"Add New..."** → **"Project"**
3. Import your `mini-RAG` repository from GitHub
4. Configure the project:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 4: Add Environment Variable

In the **Environment Variables** section:

1. **Name**: `VITE_API_BASE_URL`
2. **Value**: `https://your-backend-url.onrender.com` (your Render URL)
3. Apply to: **Production, Preview, and Development**

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for build to complete (3-5 minutes)
3. Once deployed, you'll get a URL like: `https://mini-rag.vercel.app`

## Part 3: Update CORS Settings

After deploying frontend, update backend CORS settings:

1. Go to your backend code in [main.py](../backend/app/main.py)
2. Update the CORS origins from `["*"]` to your Vercel URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mini-rag.vercel.app",  # Your Vercel URL
        "http://localhost:5173"  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Commit and push:
```bash
git add .
git commit -m "Update CORS for production"
git push origin main
```

4. Render will automatically redeploy with the new settings

## Part 4: Test Your Deployment

1. Visit your Vercel URL: `https://mini-rag.vercel.app`
2. Check that status shows "Connected" (green dot)
3. Test the workflow:
   - **Ingest**: Paste some text and click "Upload & Process"
   - **Query**: Ask a question about the ingested text
   - **Verify**: Check that citations work and show source snippets

## Troubleshooting

### Backend Issues

**Problem**: "Application failed to start"
- Check Render logs in the dashboard
- Verify all environment variables are set correctly
- Ensure `gunicorn` is in requirements.txt

**Problem**: "Cannot connect to Pinecone"
- Verify PINECONE_API_KEY is correct
- Check that your Pinecone index "mini-rag-index" exists

### Frontend Issues

**Problem**: "Offline" status (red dot)
- Verify VITE_API_BASE_URL is set correctly in Vercel
- Check that backend is deployed and accessible
- Test backend directly: `https://your-backend.onrender.com/health`

**Problem**: CORS errors in browser console
- Update CORS settings in backend main.py
- Add your Vercel URL to allowed origins
- Redeploy backend

### Free Tier Limitations

**Render Free Tier**:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month (more than enough for demo)

**Vercel Free Tier**:
- 100GB bandwidth/month
- Always on (no spin-down)
- Unlimited deployments

## Next Steps

Once deployed:
1. ✅ Mark Phase 8 complete in roadmap
2. ✅ Update README with live URLs
3. ✅ Proceed to Phase 9: Evaluation & Documentation

## Useful Commands

```bash
# View Render logs
# Go to Render dashboard → Your service → Logs tab

# Redeploy frontend
cd frontend
vercel --prod

# Test backend health
curl https://your-backend.onrender.com/health

# Test backend ingest
curl -X POST https://your-backend.onrender.com/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "Test document", "title": "Test"}'
```

## Environment Variables Summary

**Backend (.env)**:
```
JINA_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

**Frontend (.env)**:
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```
