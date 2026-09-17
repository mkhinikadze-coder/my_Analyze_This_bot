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

# პირველად ის მოდელი ვცადოთ, რაც გარემოს ცვლადშია მითითებული (თუ არის),
# შემდეგ კი, თუ ის გადატვირთულია/მიუწვდომელია, თანმიმდევრულად ვცადოთ
# ეს სარეზერვო მოდელები — ასე ერთი მოდელის დროებითი გადატვირთვა აღარ
# აჩერებს მთელ ანალიზს.
#
# შენიშვნა: "gemini-flash-latest" ალიასი Google-ის საკუთარი დოკუმენტაციით
# ექსპერიმენტულია და გააჩნია გაცილებით მკაცრი ლიმიტები (ამიტომაც გვიბრუნებდა
# ხშირად 503-ს) — ამიტომ ძირითადად კონკრეტულ, სტაბილურ Gemini 3.x მოდელებს
# ვეყრდნობით, "-latest" ალიასს კი მხოლოდ ბოლო სარეზერვო ვარიანტად ვტოვებთ.
_PRIMARY_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
_FALLBACK_MODELS = ["gemini-3.1-flash-lite", "gemini-flash-latest"]
MODELS_TO_TRY = [_PRIMARY_MODEL] + [m for m in _FALLBACK_MODELS if m != _PRIMARY_MODEL]

ATTEMPTS_PER_MODEL = 2
BASE_RETRY_DELAY_SECONDS = 2  # ყოველ ცდაზე ორმაგდება (2, 4, 8...)


def _url_for(model: str) -> str:
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


async def _post_once(url: str, payload: dict, headers: dict) -> str | None:
    """ერთი მოთხოვნა — HTTP შეცდომებს ზემოთ (_try_model-ში) ვამუშავებთ."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            logger.error("Gemini-მ არაფერი დააბრუნა: %s", data)
            return None
        finish_reason = candidates[0].get("finishReason")
        if finish_reason == "MAX_TOKENS":
            logger.warning(
                "Gemini-ს პასუხი შეიკვეცა (MAX_TOKENS) — მოსაზადებელია maxOutputTokens-ის კიდევ გაზრდა."
            )
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        return text or None


async def _try_model(model: str, payload: dict, headers: dict) -> str | None:
    """ცდილობს ერთ კონკრეტულ მოდელს, საჭიროებისამებრ რამდენჯერმე. აბრუნებს
    ტექსტს წარმატების შემთხვევაში, ან None თუ ეს მოდელი საბოლოოდ ჩავარდა."""
    url = _url_for(model)
    delay = BASE_RETRY_DELAY_SECONDS

    for attempt in range(1, ATTEMPTS_PER_MODEL + 1):
        try:
            return await _post_once(url, payload, headers)

        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            # 500/502/503/504 ჩვეულებრივ დროებითია — ღირს თავიდან ცდა.
            # 400/401/403/404 კი მუდმივი პრობლემაა ამ მოდელისთვის.
            if status in (500, 502, 503, 504) and attempt < ATTEMPTS_PER_MODEL:
                logger.warning(
                    "Gemini (%s) დროებით მიუწვდომელია (ცდა %s/%s): %s",
                    model, attempt, ATTEMPTS_PER_MODEL, e,
                )
                await asyncio.sleep(delay)
                delay *= 2
                continue
            logger.warning("Gemini (%s) საბოლოოდ ჩავარდა: %s", model, e)
            return None

        except (httpx.TimeoutException, httpx.TransportError) as e:
            # ქსელური/დროის ამოწურვის შეცდომებიც დროებითია.
            if attempt < ATTEMPTS_PER_MODEL:
                logger.warning(
                    "Gemini (%s)-თან კავშირის პრობლემა (ცდა %s/%s): %s",
                    model, attempt, ATTEMPTS_PER_MODEL, e,
                )
                await asyncio.sleep(delay)
                delay *= 2
                continue
            logger.warning("Gemini (%s) საბოლოოდ ჩავარდა (ქსელი): %s", model, e)
            return None

        except Exception:
            logger.exception("Gemini (%s)-ის გამოძახება მოულოდნელად ჩავარდა", model)
            return None

    return None


async def get_ai_analysis(prompt: str) -> str | None:
    """აბრუნებს AI-ს ტექსტურ პასუხს, ან None თუ ყველა მოდელი/ცდა ჩავარდა."""
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY არ არის დაყენებული")
        return None

    # შენიშვნა: შეგნებულად აღარ ვგზავნით "thinkingConfig" პარამეტრს — სხვადასხვა
    # Gemini მოდელს განსხვავებული, ხშირად შეუთავსებელი ფორმატი აქვს ამისთვის
    # (budget/level/include_thoughts), რაც უამრავ "400 Bad Request"-ს იწვევდა.
    # სამაგიეროდ, უბრალოდ საკმარისად დიდი maxOutputTokens ვაძლევთ, რომ შიდა
    # "დაფიქრებამაც" და ხილულმა პასუხმაც ადგილი დატოვოს.
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 4096,
        },
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    for model in MODELS_TO_TRY:
        text = await _try_model(model, payload, headers)
        if text:
            return text
        logger.info("გადავდივართ შემდეგ სარეზერვო მოდელზე (%s ვერ გამოვიდა)", model)

    logger.error("Gemini API: ყველა მოდელი ჩავარდა (%s)", MODELS_TO_TRY)
    return None
