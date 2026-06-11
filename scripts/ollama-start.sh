#!/bin/sh
# Démarre le serveur Ollama puis télécharge le modèle si absent.

ollama serve &

echo "[ollama] Attente du démarrage du serveur..."
until ollama list >/dev/null 2>&1; do
    sleep 2
done

echo "[ollama] Serveur prêt. Vérification du modèle llama3.2..."
ollama pull llama3.2

echo "[ollama] Modèle prêt."
wait
