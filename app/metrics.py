"""
R4 - Métriques & Observabilité
Collecte en mémoire les métriques de chaque requête et expose un rapport.

Métriques suivies :
  - score moyen top-k (qualité du retrieval)
  - taux de refus (anti-hallucination)
  - latence p50 / p95 (performance)
  - tokens consommés + coût projeté (exploitation)
"""
import statistics
from dataclasses import dataclass, field
from typing import Optional

# Coût Groq free-tier llama-3.3-70b ($/1M tokens) — à jour juin 2026
COST_PER_1M_PROMPT = 0.59
COST_PER_1M_COMPLETION = 0.79


@dataclass
class RequestRecord:
    refused: bool
    score: float
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int


_records: list[RequestRecord] = []


def record_request(
    refused: bool,
    score: float,
    latency_ms: float,
    tokens: dict,
) -> None:
    """Enregistre une requête. Appelé depuis api.py après chaque /ask."""
    _records.append(
        RequestRecord(
            refused=refused,
            score=score,
            latency_ms=latency_ms,
            prompt_tokens=tokens.get("prompt", 0),
            completion_tokens=tokens.get("completion", 0),
        )
    )


def _percentile(data: list[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = (p / 100) * (len(sorted_data) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_data) - 1)
    return sorted_data[lo] + (sorted_data[hi] - sorted_data[lo]) * (idx - lo)


def compute_report() -> dict:
    """Calcule et retourne le rapport de métriques complet."""
    if not _records:
        return {"error": "Aucune requête enregistrée."}

    total = len(_records)
    refused = [r for r in _records if r.refused]
    answered = [r for r in _records if not r.refused]

    latencies = [r.latency_ms for r in _records]
    scores = [r.score for r in answered]

    total_prompt = sum(r.prompt_tokens for r in _records)
    total_completion = sum(r.completion_tokens for r in _records)
    cost_usd = (
        total_prompt / 1_000_000 * COST_PER_1M_PROMPT
        + total_completion / 1_000_000 * COST_PER_1M_COMPLETION
    )

    return {
        "total_requests": total,
        "refused_count": len(refused),
        "refusal_rate_pct": round(len(refused) / total * 100, 1),
        "retrieval": {
            "avg_top1_score": round(statistics.mean(scores), 4) if scores else None,
            "min_score": round(min(scores), 4) if scores else None,
            "max_score": round(max(scores), 4) if scores else None,
        },
        "latency_ms": {
            "p50": round(_percentile(latencies, 50), 1),
            "p95": round(_percentile(latencies, 95), 1),
            "mean": round(statistics.mean(latencies), 1),
        },
        "tokens": {
            "total_prompt": total_prompt,
            "total_completion": total_completion,
            "total": total_prompt + total_completion,
        },
        "cost_usd_projected": round(cost_usd, 6),
    }


def reset() -> None:
    """Remet les métriques à zéro (utile pour les tests)."""
    _records.clear()
