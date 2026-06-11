#!/bin/sh
# Demarre le serveur Ollama puis telecharge le modele si absent.

ollama serve &

echo "[ollama] Attente du demarrage du serveur..."
until ollama list >/dev/null 2>&1; do
    sleep 2
done

echo "[ollama] Serveur pret. Verification du modele llama3.2..."
ollama pull llama3.2

echo "[ollama] Modele pret."
wait
