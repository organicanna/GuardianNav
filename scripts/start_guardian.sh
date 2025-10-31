#!/bin/bash
# GUARDIAN - Démarrage rapide 
# Script généré automatiquement par setup_local.sh

cd "$(dirname "$0")"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛡️  Démarrage Guardian Local...${NC}"

# Vérifier l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo "❌ Environnement non configuré. Exécutez: ./setup_local.sh"
    exit 1
fi

# Activer l'environnement
source .venv/bin/activate

# Trouver un port libre
PORT=5001
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    ((PORT++))
    if [ $PORT -gt 5010 ]; then
        echo "❌ Aucun port libre trouvé"
        exit 1
    fi
done

echo -e "${GREEN}🚀 Guardian démarré sur http://localhost:$PORT${NC}"

# Démarrer Guardian
python web_interface.py