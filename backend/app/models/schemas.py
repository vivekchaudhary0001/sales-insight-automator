from pydantic import BaseModel, EmailStr, Field


class AnalysisResponse(BaseModel):
    message: str = Field(..., description="Status message")
    recipient: str = Field(..., description="Email the brief was sent to")
    rows_analyzed: int = Field(..., description="Number of data rows processed")
    columns_detected: int = Field(..., description="Number of columns in the dataset")
    summary_preview: str = Field(..., description="First 300 characters of the generated summary")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Analysis complete. Your summary has been dispatched.",
                "recipient": "exec@company.com",
                "rows_analyzed": 6,
                "columns_detected": 7,
                "summary_preview": "## Executive Sales Brief\n\n**Headline:** Q1 2026 delivered $684,000 in revenue...",
            }
        }
    }


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error description")
