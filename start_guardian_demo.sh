#!/bin/bash

# 🛡️ Guardian - Script de Lancement Automatique
# Ce script lance l'interface Guardian et ouvre automatiquement le navigateur

echo "🛡️ Guardian - Assistant de Sécurité Intelligent"
echo "================================================"
echo ""
echo "🚀 Démarrage de Guardian..."
echo ""

# Vérifier si Python3 est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python3 n'est pas installé"
    echo "Veuillez installer Python3 avant de continuer"
    exit 1
fi

# Aller dans le répertoire du projet
cd "$(dirname "$0")"

echo "📂 Répertoire: $(pwd)"
echo ""

# Vérifier si le fichier guardian_web.py existe
if [ ! -f "guardian_web.py" ]; then
    echo "❌ Erreur: guardian_web.py introuvable"
    echo "Assurez-vous d'être dans le bon répertoire"
    exit 1
fi

echo "🔧 Lancement du serveur Guardian..."
echo ""

# Lancer le serveur en arrière-plan
python3 guardian_web.py &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 3

# Vérifier si le serveur fonctionne
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Serveur Guardian démarré avec succès (PID: $SERVER_PID)"
    echo ""
    echo "🌐 URLs disponibles:"
    echo "   - Page d'accueil:     http://localhost:5001"
    echo "   - Démonstration:      http://localhost:5001/demo"
    echo "   - Mode debug:         http://localhost:5001/debug"
    echo ""
    
    # Essayer d'ouvrir le navigateur automatiquement
    if command -v open &> /dev/null; then
        echo "🔗 Ouverture automatique du navigateur..."
        sleep 2
        open "http://localhost:5001"
    elif command -v xdg-open &> /dev/null; then
        echo "🔗 Ouverture automatique du navigateur..."
        sleep 2
        xdg-open "http://localhost:5001"
    else
        echo "💡 Ouvrez manuellement votre navigateur sur: http://localhost:5001"
    fi
    
    echo ""
    echo "🛡️ Guardian est maintenant opérationnel !"
    echo ""
    echo "📋 Commandes disponibles:"
    echo "   - Ctrl+C : Arrêter Guardian"
    echo "   - kill $SERVER_PID : Arrêter depuis un autre terminal"
    echo ""
    echo "⏳ Appuyez sur Ctrl+C pour arrêter Guardian..."
    
    # Attendre l'interruption
    wait $SERVER_PID
else
    echo "❌ Erreur: Impossible de démarrer le serveur Guardian"
    exit 1
fi

echo ""
echo "👋 Guardian arrêté. À bientôt !"