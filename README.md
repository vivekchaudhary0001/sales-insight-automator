# 📊 Sales Insight Automator
### Rabbitt AI · Engineering Sprint

> Upload a CSV or XLSX sales file → AI generates an executive brief → delivered to your inbox.

---

## Live URLs

| Service | URL |
|---|---|
| Frontend | `https://sales-insight-automator.vercel.app` |
| Backend API | `https://sia-api.onrender.com` |
| Swagger Docs | `https://sia-api.onrender.com/docs` |
| ReDoc | `https://sia-api.onrender.com/redoc` |

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite (deployed on Vercel) |
| Backend | FastAPI + Python 3.12 (deployed on Render) |
| AI Engine | Google Gemini 1.5 Flash (+ Groq Llama3 fallback) |
| Email | SMTP via Gmail App Password |
| Containerization | Docker (multi-stage) + docker-compose |
| CI/CD | GitHub Actions |

---

## Running Locally with Docker Compose

### 1. Clone the repo

```bash
git clone https://github.com/your-org/sales-insight-automator.git
cd sales-insight-automator
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your API keys and SMTP credentials in .env
```

### 3. Spin up

```bash
docker compose up --build
```

- **Frontend** → http://localhost:3000  
- **Backend API** → http://localhost:8000  
- **Swagger UI** → http://localhost:8000/docs  

### 4. Tear down

```bash
docker compose down
```

---

## Running Without Docker (Development)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Security Architecture

### 1. Input Validation
- File extension allowlist: `.csv`, `.xlsx`, `.xls` only
- File size hard cap: 10MB (checked both at middleware and service layer)
- Email format validation via Pydantic `EmailStr`
- Empty file rejection

### 2. Rate Limiting
A per-IP sliding window rate limiter (`RateLimitMiddleware`) allows **10 requests/minute** per IP address. Responses include `X-RateLimit-*` headers. On breach, returns HTTP `429` with a `Retry-After` header.

> **Production note:** The in-memory store resets on restart. For distributed deployments, swap for Redis-backed rate limiting (e.g., `slowapi` + `redis`).

### 3. Security Headers (via `SecurityMiddleware`)
Every response includes:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; ...
Permissions-Policy: geolocation=(), microphone=(), camera=()
```
Server version headers (`Server`, `X-Powered-By`) are stripped to prevent fingerprinting.

### 4. Bot/Scanner Blocking
The `SecurityMiddleware` maintains a blocklist of known malicious user-agent strings (sqlmap, nikto, nmap, etc.) and returns HTTP `403` to matching requests.

### 5. Non-Root Container
The backend Docker image runs as a dedicated `appuser` (non-root), following container security best practices.

### 6. No Secrets in Code
All credentials are environment-variable-driven. A `.env.example` is provided; `.env` is gitignored.

---

## CI/CD Pipeline

Triggered on every **Pull Request to `main`** and on **push to `main`**.

### Jobs

| Job | What it does |
|---|---|
| `backend-lint-test` | Runs `ruff` linter + import smoke tests |
| `backend-docker` | Builds the backend Docker image (validates Dockerfile) |
| `frontend-lint-build` | ESLint + Vite production build |
| `frontend-docker` | Builds the frontend Docker image |
| `ci-summary` | Aggregates all job results; fails PR if any job fails |

Docker layer caching (`type=gha`) keeps build times fast.

---

## API Reference

Full interactive docs available at `/docs` (Swagger UI) and `/redoc`.

### `POST /api/v1/analyze`

Upload a sales file and trigger AI analysis + email delivery.

**Request** (`multipart/form-data`):
| Field | Type | Description |
|---|---|---|
| `file` | File | `.csv` or `.xlsx`, max 10MB |
| `recipient_email` | string | Destination email address |

**Response `200`**:
```json
{
  "message": "Analysis complete. Your summary has been dispatched.",
  "recipient": "exec@company.com",
  "rows_analyzed": 6,
  "columns_detected": 7,
  "summary_preview": "## Executive Sales Brief..."
}
```

### `GET /api/v1/analyze/sample`
Returns sample Q1 2026 CSV data for testing.

### `GET /health`
Liveness probe endpoint.

---

## Testing with Sample Data

A sample CSV is included for testing:

```
Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status
2026-01-05,Electronics,North,150,1200,180000,Shipped
2026-01-12,Home Appliances,South,45,450,20250,Shipped
2026-01-20,Electronics,East,80,1100,88000,Delivered
2026-02-15,Electronics,North,210,1250,262500,Delivered
2026-02-28,Home Appliances,North,60,400,24000,Cancelled
2026-03-10,Electronics,West,95,1150,109250,Shipped
```

Save as `sales_q1_2026.csv` and upload via the UI or Swagger.

---

## Environment Variables Reference

See `.env.example` for the full list. Key variables:

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes* | Google Gemini API key |
| `GROQ_API_KEY` | No | Groq fallback key |
| `SMTP_USER` | Yes* | Gmail address for sending |
| `SMTP_PASSWORD` | Yes* | Gmail App Password |
| `VITE_API_URL` | Frontend | Backend URL for the frontend |

*Without these, the app runs in demo mode (mock AI summary, email logged to console).

---

## Project Structure

```
sales-insight-automator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + middleware registration
│   │   ├── routers/
│   │   │   └── analysis.py      # POST /analyze endpoint
│   │   ├── services/
│   │   │   ├── parser.py        # CSV/XLSX parsing
│   │   │   ├── ai_engine.py     # Gemini/Groq integration
│   │   │   └── mailer.py        # SMTP email delivery
│   │   ├── middleware/
│   │   │   ├── security.py      # Headers + bot blocking
│   │   │   └── rate_limit.py    # Per-IP rate limiting
│   │   └── models/
│   │       └── schemas.py       # Pydantic models
│   ├── Dockerfile               # Multi-stage, non-root
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Single-page application
│   │   └── main.jsx
│   ├── Dockerfile               # Multi-stage, nginx
│   ├── vite.config.js
│   └── package.json
├── .github/
│   └── workflows/
│       └── ci.yml               # Full CI/CD pipeline
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Deployment Guide

### Backend → Render

1. Connect your GitHub repo to [render.com](https://render.com)
2. Create a **Web Service** → select the `backend/` directory
3. Set **Docker** as the runtime
4. Add environment variables from `.env`
5. Deploy → copy the service URL

### Frontend → Vercel

1. Connect your GitHub repo to [vercel.com](https://vercel.com)
2. Set **Root Directory** to `frontend/`
3. Add env var: `VITE_API_URL=https://your-render-url.onrender.com/api/v1`
4. Deploy

---

*Built by the Rabbitt AI Engineering Team · Sprint v1.0*
