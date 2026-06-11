# AssistKB Search — Projet A

Pipeline RAG de recherche documentaire sur base de connaissances (Qdrant + Groq).

## Démarrage rapide

```bash
# 1. Cloner et configurer
git clone https://github.com/theohugo/tp-equipe-1j.git
cd tp-equipe-1j
git checkout projet-A/assistkb-search

cp .env.example .env
# Éditer .env : renseigner GROQ_API_KEY et vérifier les variables

# 2. Récupérer le corpus (Windows)
./scripts/fetch_corpus.ps1 -Query "intelligence artificielle" -NItems 20
# ou Linux/Mac :
# PROFILE=open DATA_QUERY="intelligence artificielle" bash scripts/fetch_corpus.sh

# 3. Lancer les services
docker compose up -d
docker compose ps   # vérifier que api et qdrant sont healthy

# 4. Tester l'API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelles mesures RGPD pour les données personnelles ?"}'
```

## Architecture

```
Question → [Embedding] → [Qdrant top-k] → [Seuil] → [LLM Groq] → Réponse citée
                                              ↓ (refus si score < seuil)
```

| Service | Port | Rôle |
|---------|------|------|
| `api` (FastAPI) | 8000 | Endpoint POST /ask, GET /metrics |
| `qdrant` | 6333 | Vector store |

## Rôles et fichiers

| Rôle | Membre | Fichiers |
|------|--------|----------|
| R1 Data | ___ | `app/ingest.py` |
| R2 Index | ___ | `app/embed.py`, `app/store.py` |
| R3 Retrieval/LLM | ___ | `app/retrieve.py`, `app/generate.py`, `app/api.py` |
| R4 DevOps/Obs | ___ | `docker-compose.yml`, `app/metrics.py`, `.github/` |

## Pipeline complet

```bash
# Après avoir rempli chaque rôle :
python -m app.ingest       # R1 → corpus/chunks.jsonl
python -m app.embed        # R2 → Qdrant peuplé
docker compose up -d       # R4 → services lancés
curl -X POST http://localhost:8000/ask -d '{"question": "..."}'
curl http://localhost:8000/metrics  # R4 → tableau de bord
```

## Questions de test

**Dans le corpus (doit répondre + citer) :**
- Quelles mesures de sécurité sont recommandées pour les données personnelles ?
- Qu'est-ce qu'une recherche vectorielle hybride ?

**Hors corpus (doit REFUSER) :**
- Quelle est la capitale de l'Australie ?
- Quel est le chiffre d'affaires 2025 de banque-alpha ?

## Sources du corpus

- [data.gouv.fr](https://www.data.gouv.fr) — Licence Ouverte Etalab
- Seed commis dans `corpus/seed/` (hors ligne)
