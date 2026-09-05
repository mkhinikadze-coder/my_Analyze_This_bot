# -*- coding: utf-8 -*-
"""
თხოვნა Google Gemini API-ის უფასო tier-ისადმი (AI Studio API key, ბარათის გარეშე).
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# 'flash' მოდელი უფასო tier-ზეა ხელმისაწვდომი
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


async def get_ai_analysis(prompt: str) -> str | None:
    """აბრუნებს AI-ს ტექსტურ პასუხს, ან None შეცდომის შემთხვევაში."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY არ არის დაყენებული")
        return None

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 500,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(GEMINI_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                logger.error("Gemini-მ არაფერი დააბრუნა: %s", data)
                return None
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(p.get("text", "") for p in parts).strip()
            return text or None
    except Exception:
        logger.exception("Gemini API-ს გამოძახება ჩავარდა")
        return None
