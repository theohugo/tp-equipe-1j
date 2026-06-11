"""
R3 - Generation
Prompt anti-hallucination + appel LLM (Groq ou Gemini).

Livrable : generate.py fonctionnel + section "Retrieval/Generation" du compte rendu
"""
from app.config import settings

REFUSAL_ANSWER = "Je ne dispose pas de cette information dans le corpus."

SYSTEM_PROMPT = """Tu es un assistant de recherche documentaire.
Règles strictes :
1. Réponds UNIQUEMENT à partir des passages fournis dans le contexte.
2. Cite toujours la source (nom du fichier) entre crochets, ex. [fiche_outil_qdrant.html].
3. Si le contexte ne contient pas la réponse, dis exactement : \"""" + REFUSAL_ANSWER + """\"
4. N'invente jamais d'information absente du contexte."""


def build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(f"[{c['source']}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def generate(query: str, chunks: list[dict]) -> dict:
    """
    Appelle le LLM avec le contexte et retourne la réponse + métadonnées tokens.

    Returns dict avec : answer, sources, tokens (prompt, completion)

    TODO R3 :
        - Construire le prompt avec SYSTEM_PROMPT + build_context(chunks) + query
        - Appeler Groq ou Gemini selon settings.llm_provider
        - Extraire le texte de réponse + usage tokens
    """
    context = build_context(chunks)
    sources = list({c["source"] for c in chunks})

    if settings.llm_provider == "groq":
        # TODO R3 : appel Groq
        # from groq import Groq
        # client = Groq(api_key=settings.groq_api_key)
        # completion = client.chat.completions.create(
        #     model=settings.llm_model,
        #     messages=[
        #         {"role": "system", "content": SYSTEM_PROMPT},
        #         {"role": "user", "content": f"Contexte :\n{context}\n\nQuestion : {query}"},
        #     ],
        # )
        # answer = completion.choices[0].message.content
        # tokens = {"prompt": completion.usage.prompt_tokens, "completion": completion.usage.completion_tokens}
        raise NotImplementedError("Groq generation — à compléter (R3)")

    elif settings.llm_provider == "gemini":
        # TODO R3 : appel Gemini
        raise NotImplementedError("Gemini generation — à compléter (R3)")

    else:
        raise ValueError(f"LLM provider inconnu : {settings.llm_provider}")

    return {
        "answer": answer,
        "sources": sources,
        "tokens": tokens,
    }
