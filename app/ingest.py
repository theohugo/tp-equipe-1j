"""
R1 - Data / Ingestion
Transformer le corpus brut en chunks propres avec métadonnées.

Livrable : corpus/chunks.jsonl + section "Ingestion" du compte rendu
"""
import json
import os
from pathlib import Path
from typing import Generator

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

CORPUS_RAW = Path("corpus/raw")
CORPUS_SEED = Path("corpus/seed")
CHUNKS_OUT = Path("corpus/chunks.jsonl")


def extract_text(file_path: Path) -> str:
    """
    TODO R1 : extraire le texte brut selon le format du fichier.
    Formats attendus : PDF, HTML, JSON, TXT
    Conseil : pdfplumber pour PDF, selectolax pour HTML
    """
    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".json":
        # TODO R1 : adapter selon la structure de vos fichiers JSON data.gouv
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return str(data)

    if suffix == ".pdf":
        # TODO R1 : utiliser pdfplumber
        # import pdfplumber
        # with pdfplumber.open(file_path) as pdf:
        #     return "\n".join(p.extract_text() or "" for p in pdf.pages)
        raise NotImplementedError("PDF extraction — à compléter (R1)")

    if suffix in (".html", ".htm"):
        # TODO R1 : utiliser selectolax
        # from selectolax.parser import HTMLParser
        # tree = HTMLParser(file_path.read_text(encoding="utf-8"))
        # return tree.text(separator="\n")
        raise NotImplementedError("HTML extraction — à compléter (R1)")

    return ""


def iter_chunks(file_path: Path) -> Generator[dict, None, None]:
    """Découpe un fichier en chunks et attache les métadonnées."""
    text = extract_text(file_path)
    if not text.strip():
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    chunks = splitter.split_text(text)

    for i, chunk in enumerate(chunks):
        yield {
            "text": chunk,
            "source": file_path.name,
            "source_path": str(file_path),
            "chunk_index": i,
            "total_chunks": len(chunks),
            # TODO R1 (bonus) : ajouter "lang" via langdetect
        }


def run_ingestion() -> int:
    """Ingère seed + raw et écrit corpus/chunks.jsonl. Retourne le nb de chunks."""
    sources = list(CORPUS_SEED.glob("*")) + list(CORPUS_RAW.glob("*"))
    total = 0

    with CHUNKS_OUT.open("w", encoding="utf-8") as out:
        for path in sources:
            if not path.is_file():
                continue
            try:
                for chunk in iter_chunks(path):
                    out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                    total += 1
            except NotImplementedError as e:
                print(f"[SKIP] {path.name} — {e}")
            except Exception as e:
                print(f"[ERROR] {path.name} — {e}")

    print(f"Ingestion terminée : {total} chunks → {CHUNKS_OUT}")
    return total


if __name__ == "__main__":
    run_ingestion()
