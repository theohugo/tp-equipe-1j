#!/usr/bin/env bash
# fetch_corpus.sh - Récupère le corpus public data.gouv (Projet A)
# Usage : PROFILE=open DATA_QUERY="intelligence artificielle" bash scripts/fetch_corpus.sh

PROFILE=${PROFILE:-open}
DATA_QUERY=${DATA_QUERY:-"intelligence artificielle"}
N_ITEMS=${N_ITEMS:-20}
OUT_DIR="corpus/raw"

mkdir -p "$OUT_DIR"
echo "Récupération du corpus (profil=$PROFILE, query='$DATA_QUERY', n=$N_ITEMS)"

if [ "$PROFILE" = "open" ]; then
    ENCODED_QUERY=$(python3 -c "import urllib.parse, sys; print(urllib.parse.quote(sys.argv[1]))" "$DATA_QUERY")
    URL="https://www.data.gouv.fr/api/1/datasets/?q=${ENCODED_QUERY}&page_size=${N_ITEMS}&format=json"

    echo "Appel API data.gouv : $URL"
    curl -sf "$URL" -o "$OUT_DIR/datagouv_results.json"

    if [ $? -eq 0 ]; then
        # Découpe en fichiers individuels si python disponible
        python3 -c "
import json, pathlib
data = json.loads(pathlib.Path('$OUT_DIR/datagouv_results.json').read_text())
for ds in data.get('data', []):
    out = pathlib.Path('$OUT_DIR') / f\"datagouv_{ds['id']}.json\"
    out.write_text(json.dumps(ds, ensure_ascii=False, indent=2))
print(f\"{len(data.get('data', []))} fichiers sauvegardés dans $OUT_DIR\")
" 2>/dev/null || echo "python3 indisponible — fichier brut conservé dans $OUT_DIR/datagouv_results.json"
    else
        echo "Erreur lors de la récupération" >&2
        exit 1
    fi
else
    echo "Profil '$PROFILE' non supporté (projet A = open uniquement)" >&2
    exit 1
fi

echo "Corpus récupéré dans $OUT_DIR/"
