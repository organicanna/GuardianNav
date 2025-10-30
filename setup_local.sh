#!/bin/bash

# GUARDIAN - DÉMARRAGE LOCAL SIMPLIFIÉ
# Script de démarrage unique pour l'environnement de développement local

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️  GUARDIAN - DÉMARRAGE LOCAL${NC}"
echo "=========================================="

# Vérifier si on est dans le bon répertoire
if [ ! -f "web_interface.py" ]; then
    echo -e "${RED}❌ Erreur: web_interface.py non trouvé${NC}"
    echo "Exécutez ce script depuis le répertoire Guardian principal"
    exit 1
fi

# Vérifier l'environnement virtuel
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Environnement virtuel non trouvé${NC}"
    echo "Création de l'environnement virtuel..."
    python3 -m venv .venv
    echo -e "${GREEN}✅ Environnement virtuel créé${NC}"
fi

# Activer l'environnement virtuel
echo -e "${BLUE}🔧 Activation de l'environnement virtuel...${NC}"
source .venv/bin/activate

# Installer/Mettre à jour les dépendances
echo -e "${BLUE}📦 Vérification des dépendances...${NC}"

# Dépendances essentielles pour l'interface web
REQUIRED_PACKAGES=(
    "flask>=2.3.3"
    "flask-socketio>=5.3.6" 
    "pyyaml>=6.0"
    "requests>=2.31.0"
)

for package in "${REQUIRED_PACKAGES[@]}"; do
    echo -e "${YELLOW}📋 Installation: $package${NC}"
    pip install "$package" --quiet
done

echo -e "${GREEN}✅ Dépendances installées${NC}"

# Vérifier la configuration
echo -e "${BLUE}🔍 Vérification de la configuration...${NC}"

if [ ! -f "api_keys.yaml" ]; then
    echo -e "${YELLOW}⚠️  Fichier api_keys.yaml non trouvé${NC}"
    echo "Création d'un fichier de configuration minimal..."
    
    cat > api_keys.yaml << EOF
# Configuration Guardian - Mode Local
google_cloud:
  project_id: "guardian-local"
  
  gemini:
    enabled: false  # Activez avec votre vraie clé API si disponible
    api_key: "YOUR_GEMINI_API_KEY_HERE"
    
  # Configuration optionnelle pour Google Maps
  google_maps_api_key: ""  # Ajoutez votre clé pour la carte interactive

# Contacts d'urgence (remplacez par vos vrais contacts)
emergency_contacts:
  - name: "Contact d'urgence"
    phone: "+33123456789" 
    email: "urgence@example.com"

# Mode local - pas besoin de configuration cloud
local_mode: true
EOF
    
    echo -e "${GREEN}✅ Fichier api_keys.yaml créé${NC}"
    echo -e "${YELLOW}💡 Vous pouvez l'éditer pour ajouter vos vraies clés API${NC}"
else
    echo -e "${GREEN}✅ Configuration trouvée${NC}"
fi

# Vérifier les templates
if [ ! -d "templates" ]; then
    echo -e "${RED}❌ Dossier templates manquant${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Templates trouvés${NC}"

# Trouver un port libre
PORT=5001
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    echo -e "${YELLOW}⚠️  Port $PORT occupé, test du port $((PORT+1))...${NC}"
    ((PORT++))
    if [ $PORT -gt 5010 ]; then
        echo -e "${RED}❌ Aucun port libre trouvé entre 5001-5010${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Port $PORT disponible${NC}"

# Mettre à jour le port dans web_interface.py si nécessaire
if [ $PORT -ne 5001 ]; then
    echo -e "${BLUE}🔧 Mise à jour du port vers $PORT...${NC}"
    sed -i.bak "s/port=50[0-9][0-9]/port=$PORT/g" web_interface.py
fi

# Créer le script de démarrage rapide
cat > start_guardian.sh << EOF
#!/bin/bash
# Script de démarrage rapide Guardian
cd "\$(dirname "\$0")"
source .venv/bin/activate
python web_interface.py
EOF

chmod +x start_guardian.sh

echo ""
echo -e "${GREEN}🎉 GUARDIAN PRÊT À DÉMARRER !${NC}"
echo "=========================================="
echo -e "${BLUE}🌐 Interface web:${NC} http://localhost:$PORT"
echo -e "${BLUE}🗺️  Page trajet:${NC} http://localhost:$PORT/map"
echo -e "${BLUE}🚨 Page urgence:${NC} http://localhost:$PORT/emergency"
echo ""
echo -e "${YELLOW}📝 COMMANDES UTILES:${NC}"
echo -e "  ${GREEN}./start_guardian.sh${NC}     - Démarrage rapide"
echo -e "  ${GREEN}python web_interface.py${NC} - Démarrage manuel"
echo -e "  ${GREEN}Ctrl+C${NC}                  - Arrêter le serveur"
echo ""

# Proposer de démarrer immédiatement
read -p "🚀 Démarrer Guardian maintenant ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}🚀 Démarrage de Guardian...${NC}"
    echo -e "${BLUE}💡 Ouvrez votre navigateur sur http://localhost:$PORT${NC}"
    echo ""
    python web_interface.py
else
    echo -e "${YELLOW}💡 Pour démarrer plus tard: ./start_guardian.sh${NC}"
fi