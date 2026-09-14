# -*- coding: utf-8 -*-
"""
თხოვნა Google Gemini API-ის უფასო tier-ისადმი (AI Studio API key, ბარათის გარეშე).
"""
import asyncio
import os
import logging
import httpx

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
# 'flash' მოდელი უფასო tier-ზეა ხელმისაწვდომი (2026 წლის მდგომარეობით)
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)

# Gemini-ს API ხანდახან დროებით "500 Internal Server Error" აბრუნებს, თავად
# Google-ის მხრიდან — ეს არ არის ჩვენი კონფიგურაციის პრობლემა. ამიტომ
# ვცდილობთ რამდენჯერმე, სანამ საბოლოოდ დავანებებთ თავს.
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2


async def get_ai_analysis(prompt: str) -> str | None:
    """აბრუნებს AI-ს ტექსტურ პასუხს, ან None ყველა ცდის ჩავარდნის შემთხვევაში."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY არ არის დაყენებული")
        return None

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 1024,
            # ახალ Gemini მოდელებს აქვთ "შიდა დაფიქრება" (thinking), რომელიც
            # ხმარობს maxOutputTokens-ის ბიუჯეტს ხილული პასუხის დაწერამდე და
            # პასუხს ხანდახან შუაზე ჭრის. ვთიშავთ, რომ მთელი ბიუჯეტი ხილულ
            # ტექსტს მოხმარდეს.
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
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
        except httpx.HTTPStatusError as e:
            last_error = e
            # 500/503 ჩვეულებრივ დროებითია — ღირს თავიდან ცდა.
            # 400/401/403/404 კი მუდმივი პრობლემაა — ხელახლა ცდა არაფერს შველის.
            if e.response.status_code in (500, 502, 503, 504) and attempt < MAX_ATTEMPTS:
                logger.warning(
                    "Gemini API-მ დროებითი შეცდომა დააბრუნა (ცდა %s/%s): %s",
                    attempt, MAX_ATTEMPTS, e,
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)
                continue
            logger.exception("Gemini API-ს გამოძახება ჩავარდა")
            return None
        except Exception:
            last_error = None
            logger.exception("Gemini API-ს გამოძახება ჩავარდა")
            return None

    if last_error:
        logger.error("Gemini API საბოლოოდ ჩავარდა %s ცდის შემდეგ", MAX_ATTEMPTS)
    return None
