#!/usr/bin/env python3 das ist eine hfg tool app
"""BLAC & White — FastAPI Server"""

import asyncio
import json
import logging
from collections import defaultdict
from pathlib import Path
from time import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from blac import run_agent1, run_agent2, run_agent3, run_agent1_mem, run_agent2_mem, run_agent3_mem

load_dotenv()

logger = logging.getLogger("blac")

app = FastAPI(docs_url=None, redoc_url=None)  # Disable API docs in production

# ── Rate limiting (in-memory, per IP) ────────────────────────────────────────

_rate_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 10   # requests per window
RATE_WINDOW = 60  # seconds


def _check_rate_limit(ip: str) -> bool:
    now = time()
    window = [t for t in _rate_store[ip] if now - t < RATE_WINDOW]
    _rate_store[ip] = window
    if len(window) >= RATE_LIMIT:
        return False
    _rate_store[ip].append(now)
    return True


# ── Input validation ──────────────────────────────────────────────────────────

_VALID_DEPTHS = {"quick", "standard", "deep"}
_MAX_FIELD_LEN = 600


def _validate(body: dict) -> tuple[dict, str, bool]:
    depth = body.get("depth", "standard")
    if depth not in _VALID_DEPTHS:
        raise HTTPException(400, "Ungültige Analysetiefe.")

    memory = bool(body.get("memory", False))
    ui = body.get("input")
    if not isinstance(ui, dict):
        raise HTTPException(400, "Ungültiges Eingabeformat.")

    for field in ("problem", "solution", "industry"):
        val = ui.get(field, "")
        if not isinstance(val, str):
            raise HTTPException(400, f"Feld '{field}' muss ein Text sein.")
        if len(val) > _MAX_FIELD_LEN:
            raise HTTPException(400, f"Feld '{field}' ist zu lang (max. {_MAX_FIELD_LEN} Zeichen).")

    return ui, depth, memory


# ── Endpoint ──────────────────────────────────────────────────────────────────

@app.post("/analyse")
async def analyse(body: dict, request: Request):
    ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(ip):
        raise HTTPException(429, "Zu viele Anfragen — bitte eine Minute warten.")

    user_input, depth, memory = _validate(body)

    async def stream():
        loop = asyncio.get_event_loop()
        try:
            if memory:
                analysis = await loop.run_in_executor(None, run_agent1_mem, user_input)
            else:
                analysis = await loop.run_in_executor(None, run_agent1, user_input, depth)
            yield f"data: {json.dumps({'step': 1, 'data': analysis}, ensure_ascii=False)}\n\n"

            if memory:
                strategy = await loop.run_in_executor(None, run_agent2_mem, analysis)
            else:
                strategy = await loop.run_in_executor(None, run_agent2, analysis, depth)
            yield f"data: {json.dumps({'step': 2, 'data': strategy}, ensure_ascii=False)}\n\n"

            if memory:
                report = await loop.run_in_executor(None, run_agent3_mem, analysis, strategy)
            else:
                report = await loop.run_in_executor(None, run_agent3, analysis, strategy, depth)
            yield f"data: {json.dumps({'step': 3, 'data': report}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.exception("Analyse-Fehler")
            yield f"data: {json.dumps({'step': 'error', 'message': 'Analyse fehlgeschlagen. Bitte erneut versuchen.'})}\n\n"

        yield f"data: {json.dumps({'step': 'done'})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


app.mount(
    "/",
    StaticFiles(directory=str(Path(__file__).parent / "static"), html=True),
    name="static",
)
