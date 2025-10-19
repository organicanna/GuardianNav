#!/usr/bin/env python3
"""Test de l'agent vocal avec configuration"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from guardian.voice_agent import VoiceAgent
from guardian.config import Config

def main():
    """Test principal de l'agent vocal"""
    print("Test de l'agent vocal...")
    
    # Charger la configuration
    config = Config(profile="test")
    voice_config = config.get_voice_agent_config()
    
    # Vérifier que le modèle existe
    model_path = voice_config.get("model_path")
    if not model_path or not os.path.exists(model_path):
        print(f"ERREUR: Modèle Vosk non trouvé à {model_path}")
        print("Téléchargez le modèle depuis: https://alphacephei.com/vosk/models")
        return
    
    print(f"Configuration: {voice_config}")
    
    try:
        agent = VoiceAgent(**voice_config)
        print("Parlez, je vous écoute… (prononcez un mot clé)")
        print("Mots clés reconnus:", voice_config.get("keywords", []))
        
        while True:
            if agent.listen_for_keywords():
                print("Mot clé détecté !")
                break
            else:
                print("Aucun mot clé détecté, recommencez…")
                
    except KeyboardInterrupt:
        print("\nTest arrêté par l'utilisateur")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()