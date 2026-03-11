from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging

from app.services.parser import parse_file
from app.services.ai_engine import generate_summary
from app.services.mailer import send_email
from app.models.schemas import AnalysisResponse

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze Sales Data",
    description="""
Upload a CSV or XLSX sales file and provide a recipient email.
The API will:
1. Parse and validate the uploaded file
2. Generate an AI-powered executive summary using Google Gemini
3. Send the summary to the specified email address

**Constraints:**
- Max file size: 10MB
- Allowed formats: .csv, .xlsx
- Rate limit: 10 requests/minute per IP
    """,
    responses={
        200: {"description": "Analysis complete, email dispatched"},
        400: {"description": "Invalid file type, size, or email"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)
async def analyze_sales_data(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="CSV or XLSX sales data file (max 10MB)"),
    recipient_email: str = Form(..., description="Email address to send the summary to"),
):
    # Validate email format (basic)
    if "@" not in recipient_email or "." not in recipient_email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email address format")

    # Validate file extension
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read and size-check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Parse file
    try:
        df, row_count, col_count = parse_file(content, ext)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"File parse error: {e}")
        raise HTTPException(status_code=400, detail="Could not parse the uploaded file")

    # Generate AI summary
    try:
        summary = await generate_summary(df)
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI summary")

    # Send email in background
    background_tasks.add_task(send_email, recipient_email, summary, filename)

    return AnalysisResponse(
        message="Analysis complete. Your summary has been dispatched.",
        recipient=recipient_email,
        rows_analyzed=row_count,
        columns_detected=col_count,
        summary_preview=summary[:300] + "..." if len(summary) > 300 else summary,
    )


@router.get(
    "/analyze/sample",
    summary="Get Sample CSV",
    description="Returns sample Q1 2026 sales data for testing the API.",
)
async def get_sample_data():
    sample = """Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status
2026-01-05,Electronics,North,150,1200,180000,Shipped
2026-01-12,Home Appliances,South,45,450,20250,Shipped
2026-01-20,Electronics,East,80,1100,88000,Delivered
2026-02-15,Electronics,North,210,1250,262500,Delivered
2026-02-28,Home Appliances,North,60,400,24000,Cancelled
2026-03-10,Electronics,West,95,1150,109250,Shipped"""
    return JSONResponse(content={"sample_csv": sample, "description": "Q1 2026 Sales Data"})
