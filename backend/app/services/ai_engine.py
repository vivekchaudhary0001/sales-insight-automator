import os
import httpx
import json
import pandas as pd
import logging

from app.services.parser import dataframe_to_text

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a senior business analyst at a top-tier consulting firm. 
Your role is to transform raw sales data into concise, executive-level briefings.

Your summary must:
1. Open with a one-sentence "headline" capturing the most important insight
2. Cover total revenue, top-performing categories/regions, and notable trends
3. Highlight any risks or anomalies (e.g., cancellations, underperformance)
4. Close with 2-3 actionable recommendations
5. Use professional, confident language — no filler phrases
6. Be formatted with clear sections using markdown headers

Keep the entire brief under 500 words."""


async def generate_summary(df: pd.DataFrame) -> str:
    """Generate an AI narrative summary from a sales DataFrame."""
    data_text = dataframe_to_text(df)

    user_prompt = f"""Analyze the following sales data and produce an executive brief:

{data_text}

Generate a professional executive summary following your instructions."""

    # Try Gemini first, fall back to Groq
    if GEMINI_API_KEY:
        try:
            return await _call_gemini(user_prompt)
        except Exception as e:
            logger.warning(f"Gemini failed: {e}, trying Groq...")

    if GROQ_API_KEY:
        try:
            return await _call_groq(user_prompt)
        except Exception as e:
            logger.warning(f"Groq failed: {e}")

    # Development fallback
    logger.warning("No LLM API key configured — using mock summary")
    return _mock_summary(df)


async def _call_gemini(prompt: str) -> str:
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT + "\n\n" + prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1024,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def _call_groq(prompt: str) -> str:
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            GROQ_URL,
            json=payload,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _mock_summary(df: pd.DataFrame) -> str:
    """Fallback summary when no LLM key is configured."""
    total_rev = df["Revenue"].sum() if "Revenue" in df.columns else "N/A"
    rows = len(df)
    return f"""## Executive Sales Brief (Demo Mode)

**Headline:** Q1 2026 sales totaled ${total_rev:,.0f} across {rows} recorded transactions.

### Performance Overview
- Total records analyzed: {rows}
- Columns tracked: {', '.join(df.columns.tolist())}

### Note
This is a demonstration summary. Configure `GEMINI_API_KEY` or `GROQ_API_KEY` to enable AI-generated insights.

### Recommendations
1. Connect a live LLM API key to unlock full narrative analysis
2. Ensure data includes Revenue, Region, and Category columns for richest insights
3. Schedule weekly automated briefs to keep leadership informed
"""
