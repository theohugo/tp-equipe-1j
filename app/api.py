"""
R3 - API FastAPI
Endpoint POST /ask : reçoit une question, retourne réponse + sources + métriques.
"""
import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.generate import REFUSAL_ANSWER, generate
from app.metrics import compute_report, record_request
from app.retrieve import retrieve

app = FastAPI(title="AssistKB Search API", version="0.1.0")

_STATIC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(_STATIC):
    app.mount("/static", StaticFiles(directory=_STATIC), name="static")


@app.get("/", include_in_schema=False)
def ui():
    index = os.path.join(_STATIC, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return HTMLResponse("<p>Interface non trouvée — vérifiez le dossier <code>static/</code>.</p>", status_code=404)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    latency_ms: float
    tokens: dict


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """
    TODO R3 : brancher retrieve() et generate() ici.
    Le squelette est prêt — il suffit de décommenter quand retrieve/generate sont implémentés.
    """
    start = time.perf_counter()

    chunks, refused = retrieve(req.question)

    if refused:
        latency_ms = (time.perf_counter() - start) * 1000
        record_request(refused=True, score=0.0, latency_ms=latency_ms, tokens={"prompt": 0, "completion": 0})
        return AskResponse(
            answer=REFUSAL_ANSWER,
            sources=[],
            latency_ms=round(latency_ms, 1),
            tokens={"prompt": 0, "completion": 0},
        )

    result = generate(req.question, chunks)
    latency_ms = (time.perf_counter() - start) * 1000
    best_score = chunks[0]["score"] if chunks else 0.0
    record_request(refused=False, score=best_score, latency_ms=latency_ms, tokens=result["tokens"])

    return AskResponse(
        answer=result["answer"],
        sources=result["sources"],
        latency_ms=round(latency_ms, 1),
        tokens=result["tokens"],
    )


@app.get("/metrics")
def metrics():
    """R4 — Tableau de bord des métriques en temps réel."""
    return compute_report()
