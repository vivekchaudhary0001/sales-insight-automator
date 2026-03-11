from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.routers import analysis
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Sales Insight Automator starting up...")
    yield
    logger.info("Sales Insight Automator shutting down...")


app = FastAPI(
    title="Sales Insight Automator API",
    description="""
## Sales Insight Automator

Upload sales data (CSV/XLSX) and receive an AI-generated executive brief delivered to your inbox.

### Features
- **File Upload**: Supports CSV and XLSX formats (max 10MB)
- **AI Analysis**: Powered by Google Gemini for professional narrative summaries
- **Email Delivery**: Sends formatted reports via SMTP
- **Rate Limited**: 10 requests/minute per IP to prevent abuse
- **Secured**: Input validation, file type enforcement, and security headers
    """,
    version="1.0.0",
    contact={
        "name": "Rabbitt AI Engineering",
        "email": "engineering@rabbitt.ai",
    },
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten to specific domains in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Custom security middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware)

# Routers
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Sales Insight Automator",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
