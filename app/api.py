"""
R3 - API FastAPI
Endpoint POST /ask : reçoit une question, retourne réponse + sources + métriques.
"""
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.generate import REFUSAL_ANSWER, generate
from app.metrics import compute_report, record_request
from app.retrieve import retrieve

app = FastAPI(title="AssistKB Search API", version="0.1.0")


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

    # TODO R3 : décommenter quand retrieve() est implémenté
    # chunks, refused = retrieve(req.question)

    # if refused:
    #     latency_ms = (time.perf_counter() - start) * 1000
    #     record_request(refused=True, score=0.0, latency_ms=latency_ms, tokens={"prompt": 0, "completion": 0})
    #     return AskResponse(
    #         answer=REFUSAL_ANSWER,
    #         sources=[],
    #         latency_ms=round(latency_ms, 1),
    #         tokens={"prompt": 0, "completion": 0},
    #     )

    # result = generate(req.question, chunks)
    # latency_ms = (time.perf_counter() - start) * 1000
    # best_score = chunks[0]["score"] if chunks else 0.0
    # record_request(refused=False, score=best_score, latency_ms=latency_ms, tokens=result["tokens"])

    # return AskResponse(
    #     answer=result["answer"],
    #     sources=result["sources"],
    #     latency_ms=round(latency_ms, 1),
    #     tokens=result["tokens"],
    # )

    raise HTTPException(status_code=501, detail="Endpoint non encore implémenté — voir retrieve.py et generate.py (R3)")


@app.get("/metrics")
def metrics():
    """R4 — Tableau de bord des métriques en temps réel."""
    return compute_report()
