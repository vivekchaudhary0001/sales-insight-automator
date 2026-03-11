import io
import pandas as pd
from typing import Tuple


def parse_file(content: bytes, ext: str) -> Tuple[pd.DataFrame, int, int]:
    """
    Parse CSV or XLSX file content into a DataFrame.
    Returns (dataframe, row_count, col_count).
    """
    if ext == ".csv":
        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}")
    elif ext in {".xlsx", ".xls"}:
        try:
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl")
        except Exception as e:
            raise ValueError(f"Failed to parse Excel file: {e}")
    else:
        raise ValueError(f"Unsupported extension: {ext}")

    if df.empty:
        raise ValueError("The uploaded file contains no data rows")

    # Basic sanitization — drop fully empty rows/cols
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    return df, len(df), len(df.columns)


def dataframe_to_text(df: pd.DataFrame, max_rows: int = 100) -> str:
    """Convert a DataFrame to a concise text representation for the LLM."""
    sample = df.head(max_rows)

    # Numeric summary
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    summary_parts = [
        f"Dataset: {len(df)} rows × {len(df.columns)} columns",
        f"Columns: {', '.join(df.columns.tolist())}",
    ]

    if numeric_cols:
        stats = df[numeric_cols].describe().round(2).to_string()
        summary_parts.append(f"\nNumeric Summary:\n{stats}")

    summary_parts.append(f"\nData Sample (first {len(sample)} rows):\n{sample.to_csv(index=False)}")

    return "\n".join(summary_parts)
