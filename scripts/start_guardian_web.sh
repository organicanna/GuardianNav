#!/bin/bash

# Script de démarrage Guardian
echo "🚀 Démarrage de Guardian Web Interface..."

# Aller dans le répertoire du projet
cd "$(dirname "$0")"

# Tuer les processus existants si nécessaire
pkill -f "guardian_web.py" 2>/dev/null

# Attendre un peu
sleep 1

# Démarrer le serveur
echo "🌐 Démarrage du serveur sur http://localhost:5001..."
python3 guardian_web.py

echo "✅ Guardian démarré avec succès!"
echo "📱 Ouvrez votre navigateur sur: http://localhost:5001"