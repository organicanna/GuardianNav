#!/usr/bin/env python3
"""Test de l'agent statique avec configuration"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from guardian.GPS_agent import StaticAgent
from guardian.config import Config

def trigger_alert():
    print("ALERTE : Vous semblez immobile ou un mot clé vocal a été détecté. Tout va bien ?")

def main():
    """Test principal de l'agent statique"""
    print("Test de l'agent statique GPS...")
    
    # Charger la configuration de test
    config = Config(profile="test")
    static_config = config.get_static_agent_config()
    
    print(f"Configuration: {static_config}")
    
    # Créer l'agent avec la configuration
    agent = StaticAgent(**static_config)
    
    print("Simulation GPS en cours... (Ctrl+C pour arrêter)")
    try:
        for position in agent.simulate_gps():
            if agent.update_position(position):
                trigger_alert()
            else:
                print(f"Position : {position} - Aucun problème détecté.")
    except KeyboardInterrupt:
        print("\nTest arrêté par l'utilisateur")

if __name__ == "__main__":
    main()