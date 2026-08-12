# EcoOptima Deployment & Local Production Bundle Guide

This document outlines how to deploy and run **EcoOptima** in production or stage environments.

---

## 📦 Production Bundle Build Verification

The production distribution bundle for the frontend has been compiled using Vite:

```bash
cd frontend
npm run build
```

- **Output Directory:** `frontend/dist/`
- **Bundle File:** `dist/assets/index-UXOo1pZQ.js` (~206 kB gzipped)
- **Stylesheet:** `dist/assets/index-Coewnj9W.css` (~2.02 kB gzipped)

---

## 🚀 Running Live Deployment Services

### Option A: Local Full-Stack Execution (Pitch Demo Setup)

1. **Backend (FastAPI Uvicorn Production Server):**
   ```powershell
   cd "c:\Users\KISHORE V\Documents\Gstack\backend"
   py -3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
   *Live API Base:* `http://localhost:8000/api`  
   *Swagger Docs:* `http://localhost:8000/docs`

2. **Frontend (Vite / Static Web Server):**
   ```powershell
   cd "c:\Users\KISHORE V\Documents\Gstack\frontend"
   npm run preview -- --port 5173 --host 0.0.0.0
   ```
   *Live App:* `http://localhost:5173`

---

### Option B: Production Cloud Deployment (Vercel / Render / Docker)

#### 1. Backend Deployment (e.g. Render / Railway / AWS App Runner)
- **Environment Variable:** Set `WOLFRAM_APP_ID=3R4RTVW3QR`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 2. Frontend Deployment (e.g. Vercel / Netlify)
- **Root Directory:** `frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Environment / Proxy:** Ensure `/api/*` proxies to your deployed backend URL.

---

## ✅ Deployment Verification Checkpoints

- **Backend Health Check:** `GET http://localhost:8000/api/health` $\rightarrow$ `{"status": "ok"}`
- **Wolfram API Connectivity:** `GET http://localhost:8000/api/health/wolfram` $\rightarrow$ `{"wolfram_available": true, "mode": "wolfram"}`
- **Full Flow Execution:** Navigate to `http://localhost:5173` $\rightarrow$ Click **"⚡ Use Demo Facility"** $\rightarrow$ Click **"⚡ Optimize Now"** $\rightarrow$ Verify **`[Solved via Wolfram Alpha]`** badge and 62.1% cost savings.
